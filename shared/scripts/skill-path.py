#!/usr/bin/env python3
"""Resolve a catalog-declared skill entry without guessing its namespace."""
import argparse
import os
from pathlib import Path
import sys


def absolute(value):
    return Path(os.path.abspath(Path(value).expanduser()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--declared", required=True, help="exact catalog source; expand declared root aliases first")
    parser.add_argument("--local", help="entry explicitly required by repository instructions, if any")
    parser.add_argument("--read", action="store_true", help="emit the complete selected entry instead of its path")
    args = parser.parse_args()
    selected = None
    origin = "declared source"
    try:
        declared = absolute(args.declared)
        local = absolute(args.local) if args.local else None
        if local is not None and (local.exists() or local.is_symlink()):
            selected, origin = local, "required local source"
        else:
            selected = declared
        if not selected.is_file():
            raise OSError("not a regular file or missing")
        content = selected.read_bytes()
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"skill-path: cannot read {origin} {str(selected) if selected else repr(args.declared)}: {exc}", file=sys.stderr)
        return 1
    if args.read:
        sys.stdout.buffer.write(content)
    else:
        print(selected)
    return 0


if __name__ == "__main__":
    sys.exit(main())
