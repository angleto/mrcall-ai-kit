"""Actual resolver CLI and isolated installed catalog-entry acceptance."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'shared/scripts/skill-path.py'


class SkillPathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='skill paths ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.home = self.base / 'home'
        self.home.mkdir()
        self.declared = self.home / '.agents/skills/doc-start/SKILL.md'
        self.write(self.declared, 'Installed workflow entry.\n')
        self.local = self.repo / '.agents/skills/doc-start/SKILL.md'

    def write(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def invoke(self, *args, script=SCRIPT, expected=0):
        argv = [sys.executable, str(script), *map(str, args)]
        result = subprocess.run(argv, cwd=self.repo, env=dict(os.environ, HOME=str(self.home)),
                                capture_output=True, text=True, timeout=10)
        log = os.environ.get('MRCALL_SKILL_PATH_TEST_LOG')
        if log:
            with open(log, 'a') as handle:
                handle.write(json.dumps({'test': self.id(), 'argv': argv, 'exit': result.returncode,
                                         'stdout': result.stdout, 'stderr': result.stderr}) + '\n')
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def test_required_local_present_and_support_anchor(self):
        self.write(self.local, 'Local workflow entry.\n')
        self.write(self.local.with_name('WORKFLOW.md'), 'Selected local support.\n')
        result = self.invoke('--declared', self.declared, '--local', '.agents/skills/doc-start/SKILL.md')
        self.assertEqual(str(self.local) + '\n', result.stdout)
        support = Path(result.stdout.strip()).with_name('WORKFLOW.md')
        self.assertEqual('Selected local support.\n', support.read_text())
        self.assertEqual('Local workflow entry.\n', self.invoke('--declared', self.declared,
                         '--local', self.local, '--read').stdout)

    def test_absent_local_uses_declared_installed_source(self):
        result = self.invoke('--declared', '~/.agents/skills/doc-start/SKILL.md', '--local', self.local)
        self.assertEqual(str(self.declared) + '\n', result.stdout)
        self.assertEqual('Installed workflow entry.\n', self.invoke('--declared', self.declared,
                         '--local', self.local, '--read').stdout)
        self.assertFalse(self.local.exists())

    def test_unrequested_local_does_not_override_catalog(self):
        self.write(self.local, 'Unrequested override.\n')
        self.assertEqual('Installed workflow entry.\n',
                         self.invoke('--declared', self.declared, '--read').stdout)

    def test_missing_declared_source_has_no_partial_success(self):
        self.declared.unlink()
        result = self.invoke('--declared', self.declared, '--local', self.local, '--read', expected=1)
        self.assertEqual('', result.stdout)
        self.assertIn('cannot read declared source', result.stderr)
        self.assertIn(str(self.declared), result.stderr)
        self.assertFalse(self.local.exists())

    def test_cs_symlink_is_not_a_doc_start_catalog(self):
        cs = self.repo / '.claude/skills/cs-capabilities/SKILL.md'
        self.write(cs, 'Real CS skill.\n')
        self.local.parent.parent.parent.mkdir(parents=True)
        (self.repo / '.agents/skills').symlink_to('../.claude/skills', target_is_directory=True)
        negative = subprocess.run(['cat', str(cs), str(self.local)], capture_output=True, text=True)
        self.assertNotEqual(0, negative.returncode)
        self.assertEqual('Real CS skill.\n', negative.stdout)
        self.assertFalse(self.local.exists())
        self.assertEqual('Installed workflow entry.\n', self.invoke('--declared', self.declared,
                         '--local', self.local, '--read').stdout)
        self.assertEqual('Real CS skill.\n', cs.read_text())
        self.assertFalse(self.local.exists())

    def test_invalid_present_override_is_diagnosed(self):
        self.local.mkdir(parents=True)
        result = self.invoke('--declared', self.declared, '--local', self.local, '--read', expected=1)
        self.assertEqual('', result.stdout)
        self.assertIn('required local source', result.stderr)
        self.assertIn(str(self.local), result.stderr)

    def test_dangling_override_is_diagnosed(self):
        self.local.parent.mkdir(parents=True)
        self.local.symlink_to('missing-entry')
        result = self.invoke('--declared', self.declared, '--local', self.local, expected=1)
        self.assertEqual('', result.stdout)
        self.assertIn('required local source', result.stderr)

    def test_installed_copy_and_symlink_catalog_entries(self):
        for mode in ('copy', 'symlink'):
            with self.subTest(mode=mode):
                home = self.base / mode
                home.mkdir()
                (home / '.codex').mkdir()
                owner = home / '.codex/AGENTS.md'
                owner.write_text('Operator-owned instruction.\n')
                env = dict(os.environ, HOME=str(home))
                subprocess.run([str(ROOT / 'install.sh'), '--environment', 'codex', '--features',
                                'doc-harness', '--mode', mode, '--on-exist', 'overwrite', '--yes'],
                               env=env, capture_output=True, text=True, check=True, timeout=60)
                helper = home / '.config/mrcall-ai-kit/skill-path.py'
                self.assertEqual(mode == 'symlink', helper.is_symlink())
                self.assertEqual(SCRIPT.read_bytes(), helper.read_bytes())
                catalog = home / '.agents/skills/doc-start/SKILL.md'
                result = self.invoke('--declared', catalog, '--local', self.local, '--read', script=helper)
                self.assertEqual(catalog.read_text(), result.stdout)
                selected = self.invoke('--declared', catalog, script=helper).stdout.strip()
                self.assertEqual((ROOT / 'shared/commands/doc-start.md').read_bytes(),
                                 Path(selected).with_name('WORKFLOW.md').read_bytes())
                self.assertFalse(self.local.exists())
                manifest = (home / '.config/mrcall-ai-kit/installed.tsv').read_text().splitlines()
                self.assertEqual(1, sum(line.split('\t')[2] == str(helper) for line in manifest))
                self.assertTrue(owner.read_text().endswith('Operator-owned instruction.\n'))
                subprocess.run([str(ROOT / 'uninstall.sh'), '--yes'], env=env,
                               capture_output=True, text=True, check=True, timeout=60)
                self.assertFalse(helper.exists())
                self.assertFalse(helper.is_symlink())
                self.assertEqual('Operator-owned instruction.\n', owner.read_text())

    def test_every_template_install_route_delivers_one_resolver(self):
        for mode in ('copy', 'symlink'):
            for features in ('verification-warnings', 'doc-harness,verification-warnings'):
                with self.subTest(mode=mode, features=features):
                    home = self.base / (mode + features)
                    home.mkdir()
                    env = dict(os.environ, HOME=str(home))
                    subprocess.run([str(ROOT / 'install.sh'), '--environment', 'codex', '--features',
                                    features, '--mode', mode, '--on-exist', 'overwrite', '--yes'],
                                   env=env, capture_output=True, text=True, check=True, timeout=60)
                    kit = home / '.config/mrcall-ai-kit'
                    self.assertEqual((ROOT / 'shared/templates/AGENTS.block.md').read_bytes(),
                                     (kit / 'AGENTS.block.md').read_bytes())
                    helper = kit / 'skill-path.py'
                    self.assertEqual('Installed workflow entry.\n',
                                     self.invoke('--declared', self.declared, '--read', script=helper).stdout)
                    manifest = (kit / 'installed.tsv').read_text().splitlines()
                    self.assertEqual(1, sum(line.split('\t')[2] == str(helper) for line in manifest))
                    subprocess.run([str(ROOT / 'uninstall.sh'), '--yes'], env=env,
                                   capture_output=True, text=True, check=True, timeout=60)
                    self.assertFalse(helper.exists())
                    self.assertFalse(helper.is_symlink())


if __name__ == '__main__':
    unittest.main(verbosity=2)
