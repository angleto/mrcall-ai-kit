import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('completion_fixture', ROOT / 'shared/scripts/tests/test_doc_evidence.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.env = dict(os.environ, HOME=str(self.home), MRCALL_VERIFICATION_WARNINGS_STATE=str(self.home / 'state'))
        self.kit = self.home / '.config/mrcall-ai-kit'
        self.register = self.kit / 'verification-warnings/register.py'
        self.backend = self.kit / 'verification-warnings/verification_warnings.py'
        self.settings = [self.home / '.claude/settings.json', self.home / '.codex/hooks.json']
        self.sentinel = {'foreign': 42, 'hooks': {'PreToolUse': [{'matcher': '.*', 'custom': 7, 'hooks': [{'type': 'command', 'command': 'foreign-sentinel'}]}]}}
        for p in self.settings:
            p.parent.mkdir(parents=True)
            p.write_text(json.dumps(self.sentinel))
        p = self.home / '.config/opencode/plugins/foreign.ts'
        p.parent.mkdir(parents=True)
        p.write_text('foreign sentinel')

    def run_cli(self, argv, stdin=None, expected=0):
        result = subprocess.run([str(x) for x in argv], input=stdin, env=self.env, capture_output=True, text=True, cwd=ROOT)
        log = os.environ.get('MRCALL_WARNINGS_DELIVERY_LOG')
        if log:
            with open(log, 'a') as h:
                h.write(json.dumps({'test': self.id(), 'argv': [str(x) for x in argv], 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}) + '\n')
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def install(self, mode='copy', activate=False):
        argv = ['bash', ROOT / 'install.sh', '--environment', 'all', '--features', 'verification-warnings', '--mode', mode, '--on-exist', 'overwrite', '--yes']
        if activate:
            argv += ['--activate-verification-warnings', 'all']
        self.run_cli(argv)

    def action(self, runtime, action, expected=0):
        return self.run_cli([sys.executable, self.register, runtime, action], expected=expected)

    def make_task(self):
        previous = fixture.CHECKER
        fixture.CHECKER = self.kit / 'doc-check.py'
        self.addCleanup(setattr, fixture, 'CHECKER', previous)
        f = fixture.CompletionTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        f.initialize('fastpath')
        f.lead_closure(False)
        return f

    def bind(self, f, runtime):
        self.run_cli([sys.executable, self.backend, 'bind', '--runtime', runtime, '--session', runtime+'-session', '--repo', f.root, '--task', f.task])

    def test_installed_registration_roundtrip_and_uninstall(self):
        self.install()
        for runtime in ['claude', 'codex', 'opencode']:
            self.assertIn('dormant', self.action(runtime, 'status').stdout)
        for p in self.settings:
            self.assertEqual(json.loads(p.read_text()), self.sentinel)
        self.install(activate=True)
        f = self.make_task()
        for runtime in ['claude', 'codex', 'opencode']:
            self.assertIn('registered', self.action(runtime, 'status').stdout)
            self.bind(f, runtime)
        for runtime, p in zip(['claude', 'codex'], self.settings):
            v = json.loads(p.read_text())
            owned = v['hooks']['PreToolUse'].pop()['hooks'][0]
            v['hooks']['PreToolUse'][0]['hooks'].append(owned)
            p.write_text(json.dumps(v))
        for runtime in ['claude', 'codex', 'opencode']:
            self.action(runtime, 'off')
            self.assertIn('dormant', self.action(runtime, 'status').stdout)
        for p in self.settings:
            self.assertEqual(json.loads(p.read_text()), self.sentinel)
        self.assertEqual(json.loads(self.run_cli([sys.executable, self.backend, 'status']).stdout)['bindings'], [])
        for runtime in ['claude', 'codex', 'opencode']:
            self.action(runtime, 'on')
            self.bind(f, runtime)
        self.run_cli(['bash', ROOT/'uninstall.sh', '--yes'])
        for p in self.settings:
            self.assertEqual(json.loads(p.read_text()), self.sentinel)
        self.assertEqual((self.home/'.config/opencode/plugins/foreign.ts').read_text(), 'foreign sentinel')
        self.assertFalse((self.home/'.config/opencode/plugins/mrcall-verification-warnings.ts').exists())
        self.assertEqual(list((self.home/'state').glob('*')), [])
        self.assertFalse(self.backend.exists())

    def test_malformed_config_foreign_plugin_and_dry_run(self):
        self.install('symlink')
        self.settings[0].write_text('{bad')
        before=self.settings[0].read_bytes()
        self.action('claude','on',expected=1)
        self.assertEqual(before,self.settings[0].read_bytes())
        p=self.home/'.config/opencode/plugins/mrcall-verification-warnings.ts'
        p.write_text('foreign')
        self.action('opencode','on',expected=1)
        self.action('opencode','off')
        self.assertEqual(p.read_text(),'foreign')
        before=self.settings[1].read_bytes()
        self.run_cli([sys.executable,self.register,'codex','on','--dry-run'])
        self.assertEqual(before,self.settings[1].read_bytes())

    def test_real_stdin_adapters_missing_current_malformed_and_cleanup(self):
        self.install()
        f=self.make_task()
        for runtime in ['claude','codex']:
            hook=self.kit/f'verification-warnings/{runtime}/verification-warnings.py'
            payload={'hook_event_name':'PreToolUse','session_id':runtime+'-session','cwd':str(f.root)}
            self.assertEqual(self.run_cli([sys.executable,hook],json.dumps(payload)).stdout,'')
            self.bind(f,runtime)
            warning=json.loads(self.run_cli([sys.executable,hook],json.dumps(payload)).stdout)
            self.assertEqual(set(warning),{'systemMessage'})
            self.assertIn('missing receipt',warning['systemMessage'])
            self.assertEqual(self.run_cli([sys.executable,hook],json.dumps(payload)).stdout,'')
            self.assertEqual(self.run_cli([sys.executable,hook],'{bad').stdout,'')
            self.assertEqual(self.run_cli([sys.executable,hook],'[]').stdout,'')
        f.call('focused',{'argv':[sys.executable,'src/tool.py']})
        for runtime in ['claude','codex']:
            hook=self.kit/f'verification-warnings/{runtime}/verification-warnings.py'
            payload={'hook_event_name':'PreToolUse','session_id':runtime+'-session','cwd':str(f.root)}
            self.assertEqual(self.run_cli([sys.executable,hook],json.dumps(payload)).stdout,'')
        hook=self.kit/'verification-warnings/claude/verification-warnings.py'
        self.run_cli([sys.executable,hook],json.dumps({'hook_event_name':'SessionEnd','session_id':'claude-session'}))
        result=json.loads(self.run_cli([sys.executable,self.backend,'status']).stdout)
        self.assertEqual([v['runtime'] for v in result['bindings']],['codex'])

    def test_selected_runtime_activation_all_and_unavailable_backend(self):
        self.run_cli(['bash', ROOT/'install.sh', '--environment', 'codex', '--features', 'verification-warnings', '--mode', 'copy', '--on-exist', 'overwrite', '--yes', '--activate-verification-warnings', 'all'])
        self.assertIn('registered', self.action('codex', 'status').stdout)
        self.assertEqual(json.loads(self.settings[0].read_text()), self.sentinel)
        hook=self.kit/'verification-warnings/codex/verification-warnings.py'
        self.backend.unlink()
        result=self.run_cli([sys.executable,hook],json.dumps({'session_id':'codex-session','cwd':str(ROOT)}))
        self.assertEqual(result.stdout,'')
        self.assertEqual(result.stderr,'')

    def test_plugin_real_callback_toast_dedupe_and_exceptions(self):
        self.install()
        f=self.make_task()
        self.bind(f,'opencode')
        script=self.home/'fixture.mts'
        plugin=self.kit/'verification-warnings/opencode/verification-warnings.ts'
        script.write_text('''import { VerificationWarnings } from '''+json.dumps(str(plugin))+''';
import assert from 'node:assert/strict';
let messages=[];
let fail=false;
const hooks=await VerificationWarnings({directory:'''+json.dumps(str(f.root))+''',client:{tui:{showToast:async (request)=>{messages.push(request); if(fail) throw Error('display unavailable')}}}});
const callback=hooks['tool.execute.before'];
const output={args:{filePath:'sentinel',content:'unchanged'}};
const before=JSON.stringify(output);
await callback({sessionID:'opencode-session'},output);
assert.equal(messages.length,1);
assert.equal(messages[0].body.variant,'warning');
await callback({sessionID:'opencode-session'},output);
assert.equal(messages.length,1);
await callback({},output);
assert.equal(messages.length,1);
assert.equal(JSON.stringify(output),before);
console.log('plugin callbacks: warning once; duplicate and absent session silent; args preserved');
''')
        self.run_cli(['node','--experimental-strip-types',script])
        self.run_cli([sys.executable,self.backend,'unbind','--runtime','opencode','--session','opencode-session'])
        self.bind(f,'opencode')
        text=script.read_text().replace('let fail=false','let fail=true')
        script.write_text(text)
        self.run_cli(['node','--experimental-strip-types',script])


if __name__=='__main__':
    unittest.main()
