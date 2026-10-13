"""Advisory inspection of existing completion receipts and explicit session bindings."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import sys
import subprocess
import tempfile

RUNTIMES = ("claude", "codex", "opencode")


def modules():
    here = Path(__file__).resolve().parent
    directory = here if (here / "doc-check.py").is_file() else here.parent
    loaded = []
    for name in ("doc-check", "doc-evidence"):
        spec = importlib.util.spec_from_file_location(name.replace("-", "_") + "_warnings", directory / (name + ".py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        loaded.append(module)
    return loaded


def check(repo, task):
    result = {"task_id": task, "repo": str(repo), "diagnostics": []}
    try:
        checker, evidence = modules()
        binding = evidence.identity(Path(repo).resolve(), task)
        result.update(binding)
        record = evidence.load(binding)
        if record.get("finalized"):
            result["finalized"] = True
            return result
        obligations = [key for key in evidence.required(record) if key in {"mechanical", "focused"}]
        digest = evidence.snapshot_digest(evidence.snapshot(record, checker))
        for obligation in obligations:
            receipt = record["results"].get(obligation)
            reasons = []
            if not receipt:
                reasons.append("missing receipt")
            elif not isinstance(receipt, dict):
                reasons.append("malformed receipt")
            else:
                if receipt.get("exit_status") != 0:
                    reasons.append("command failed or exit status missing")
                if receipt.get("content_unchanged") is not True:
                    reasons.append("command changed content or content evidence missing")
                if receipt.get("snapshot") != digest:
                    reasons.append("stale content snapshot")
            if reasons:
                result["diagnostics"].append({"obligation": obligation, "reasons": reasons,
                    "action": action_guidance(checker, binding, obligation)})
    except Exception as exc:
        result["diagnostics"].append({"obligation": "evidence", "reasons": [str(exc)],
            "action": "Repair this explicitly selected task's evidence or configuration; no check was executed."})
    return result



def action_guidance(checker, binding, obligation):
    argv = [sys.executable, str(Path(checker.__file__).resolve()), "--repo", binding["repo"],
            "--completion", obligation, "--task", binding["task_id"]]
    command = shlex.join(argv)
    if obligation == "focused":
        return ("Rerun the existing focused check using " + command +
                " --input PATH_TO_ARGV_JSON. Replace PATH_TO_ARGV_JSON with an actual JSON file "
                "containing the intended check's argv array; this is a template, not a runnable command.")
    return "Rerun " + command


def state_root():
    return Path(os.environ.get("MRCALL_VERIFICATION_WARNINGS_STATE", str(Path.home() / ".config/mrcall-ai-kit/verification-warnings/state"))).expanduser().absolute()


def selected(runtime, session):
    if runtime not in RUNTIMES or not isinstance(session, str) or not session or len(session) > 1024 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", session):
        raise ValueError("runtime and simple nonempty session ID required")
    digest = hashlib.sha256(json.dumps([runtime, session], separators=(",", ":")).encode()).hexdigest()
    return state_root() / (digest + ".json"), state_root() / (digest + ".emitted")


def safe(path):
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError("symlink state path refused")


def write(path, value):
    safe(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    fd, temporary = tempfile.mkstemp(prefix=".warnings-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            os.fchmod(handle.fileno(), 0o600)
            json.dump(value, handle, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read(path):
    safe(path)
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError("invalid binding state")
    return value


def bind(runtime, session, repo, task):
    path, emitted = selected(runtime, session)
    _, evidence = modules()
    binding = evidence.identity(Path(repo).resolve(), task)
    evidence.load(binding)
    value = {"runtime": runtime, "session": session, **binding}
    write(path, value)
    safe(emitted)
    emitted.unlink(missing_ok=True)
    return value


def unbind(runtime, session):
    for path in selected(runtime, session):
        safe(path)
        path.unlink(missing_ok=True)


def status(runtime=None, session=None):
    if runtime is not None or session is not None:
        path, _ = selected(runtime, session)
        return [read(path)] if path.exists() else []
    root = state_root()
    safe(root)
    return [read(path) for path in sorted(root.glob("*.json"))] if root.exists() else []


def evaluate(runtime, session, cwd):
    if not session or not cwd:
        return None
    try:
        path, emitted = selected(runtime, session)
        if not path.exists():
            return None
        value = read(path)
        if value.get("runtime") != runtime or value.get("session") != session:
            raise ValueError("runtime/session binding mismatch")
        expected = {key: value[key] for key in ("repo", "git_dir", "task_id")}
        roots = subprocess.run(["git", "rev-parse", "--show-toplevel", "--absolute-git-dir"], cwd=cwd, capture_output=True, text=True)
        if roots.returncode != 0:
            return None
        repo, git_dir = roots.stdout.splitlines()
        if str(Path(repo).resolve()) != expected["repo"] or str(Path(git_dir).resolve()) != expected["git_dir"]:
            return None
        result = check(expected["repo"], expected["task_id"])
        safe(emitted)
        if not result["diagnostics"]:
            emitted.unlink(missing_ok=True)
            return None
        digest = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
        if emitted.exists() and read(emitted).get("digest") == digest:
            return None
        write(emitted, {"digest": digest})
        return format_warning(result)
    except Exception:
        return None


def format_warning(result):
    parts = [f"Verification warning for task {result['task_id']}:"]
    for item in result["diagnostics"]:
        parts.append(f"{item['obligation']}: {', '.join(item['reasons'])}. {item['action']}")
    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    inspect = commands.add_parser("check")
    inspect.add_argument("--repo", required=True)
    inspect.add_argument("--task", required=True)
    inspect.add_argument("--json", action="store_true")
    for action in ("bind", "unbind"):
        command = commands.add_parser(action)
        command.add_argument("--runtime", choices=RUNTIMES, required=True)
        command.add_argument("--session", required=True)
        if action == "bind":
            command.add_argument("--repo", required=True)
            command.add_argument("--task", required=True)
    show = commands.add_parser("status")
    show.add_argument("--runtime", choices=RUNTIMES)
    show.add_argument("--session")
    args = parser.parse_args()
    try:
        if args.action == "check":
            result = check(args.repo, args.task)
            print(json.dumps(result, sort_keys=True) if args.json else format_warning(result) if result["diagnostics"] else "")
        elif args.action == "bind":
            print(json.dumps(bind(args.runtime, args.session, args.repo, args.task), sort_keys=True))
        elif args.action == "unbind":
            unbind(args.runtime, args.session)
            print(json.dumps({"unbound": True}))
        else:
            print(json.dumps({"bindings": status(args.runtime, args.session)}, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        return 0 if args.action == "check" else 1


if __name__ == "__main__":
    raise SystemExit(main())
