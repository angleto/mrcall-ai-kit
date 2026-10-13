import importlib.util
import json
from pathlib import Path
import sys


def main():
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            return
        here = Path(__file__).absolute().parent
        backend = here.parent / "verification_warnings.py"
        if not backend.is_file():
            backend = Path(__file__).resolve().parents[2] / "shared/scripts/verification_warnings.py"
        spec = importlib.util.spec_from_file_location("verification_warnings", backend)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if payload.get("hook_event_name") == "SessionEnd":
            module.unbind("codex", payload.get("session_id"))
            return
        warning = module.evaluate("codex", payload.get("session_id"), payload.get("cwd"))
        if warning:
            print(json.dumps({"systemMessage": warning}))
    except Exception:
        pass


if __name__ == "__main__":
    main()
