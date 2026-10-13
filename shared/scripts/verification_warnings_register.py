import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile


def base():
    return Path.home() / '.config/mrcall-ai-kit/verification-warnings'


def adapter(runtime):
    return base() / runtime / ('verification-warnings.ts' if runtime == 'opencode' else 'verification-warnings.py')


def command(runtime):
    return 'python3 "' + str(adapter(runtime)) + '"'


def config(runtime):
    return Path.home() / ('.claude/settings.json' if runtime == 'claude' else '.codex/hooks.json')


def plugin():
    return Path.home() / '.config/opencode/plugins/mrcall-verification-warnings.ts'


def read(runtime):
    path = config(runtime)
    value = json.loads(path.read_text()) if path.exists() else {}
    if not isinstance(value, dict) or not isinstance(value.get('hooks', {}), dict):
        raise ValueError('malformed hook configuration')
    for groups in value.get('hooks', {}).values():
        if not isinstance(groups, list):
            raise ValueError('malformed hook groups')
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get('hooks'), list) or any(not isinstance(hook, dict) for hook in group['hooks']):
                raise ValueError('malformed hook handlers')
    return value


def enabled(runtime):
    if runtime == 'opencode':
        return plugin().is_symlink() and os.readlink(plugin()) == str(adapter(runtime))
    return any(hook.get('type') == 'command' and hook.get('command') == command(runtime) for group in read(runtime).get('hooks', {}).get('PreToolUse', []) for hook in group['hooks'])


def mutate(runtime, enable, dry):
    if runtime == 'opencode':
        target = plugin()
        if target.exists() or target.is_symlink():
            if not enabled(runtime):
                if enable:
                    raise ValueError('foreign plugin preserved: ' + str(target))
                return
            if not enable and not dry:
                target.unlink()
        elif enable and not dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(adapter(runtime))
        return
    value = read(runtime)
    original = json.dumps(value, sort_keys=True)
    hooks = value.get('hooks', {})
    for event in list(hooks):
        groups = []
        for group in hooks[event]:
            remaining = [hook for hook in group['hooks'] if not (hook.get('type') == 'command' and hook.get('command') == command(runtime))]
            if remaining:
                groups.append({**group, 'hooks': remaining})
            elif remaining == group['hooks']:
                groups.append(group)
        if groups:
            hooks[event] = groups
        else:
            del hooks[event]
    if enable:
        hooks.setdefault('PreToolUse', []).append({'hooks': [{'type': 'command', 'command': command(runtime), 'timeout': 10}]})
        if runtime == 'claude':
            hooks.setdefault('SessionEnd', []).append({'hooks': [{'type': 'command', 'command': command(runtime), 'timeout': 10}]})
    if hooks:
        value['hooks'] = hooks
    else:
        value.pop('hooks', None)
    if not dry and json.dumps(value, sort_keys=True) != original:
        path = config(runtime)
        if path.is_symlink():
            raise ValueError('symlink configuration preserved')
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.verification-warnings-')
        try:
            with os.fdopen(fd, 'w') as stream:
                json.dump(value, stream, indent=2)
                stream.write('\n')
            os.replace(temporary, path)
        finally:
            Path(temporary).unlink(missing_ok=True)


def clear(runtime):
    backend = base() / 'verification_warnings.py'
    spec = importlib.util.spec_from_file_location('verification_warnings', backend)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for binding in module.status():
        if binding.get('runtime') == runtime:
            module.unbind(runtime, binding['session'])


def main():
    parser = argparse.ArgumentParser(description='Manage optional advisory verification hooks.')
    parser.add_argument('runtime', choices=['claude', 'codex', 'opencode'])
    parser.add_argument('action', choices=['on', 'off', 'status', 'unregister'])
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        installed = adapter(args.runtime).is_file()
        if args.action == 'status':
            state = 'registered' if enabled(args.runtime) else 'installed, dormant' if installed else 'not installed'
            if args.runtime == 'codex' and state == 'registered':
                state += '; trust unverified (confirm in /hooks)'
            print('verification warnings for ' + args.runtime + ': ' + state)
            return 0
        if args.action == 'on' and not installed:
            raise ValueError('adapter not installed')
        mutate(args.runtime, args.action == 'on', args.dry_run)
        if args.action != 'on' and not args.dry_run:
            clear(args.runtime)
        print('verification warnings for ' + args.runtime + ': ' + ('would ' if args.dry_run else '') + ('registered' if args.action == 'on' else 'disabled'))
        return 0
    except Exception as exc:
        print(str(exc), file=os.sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
