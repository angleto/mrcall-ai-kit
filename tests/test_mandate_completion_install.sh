#!/usr/bin/env bash
set -euo pipefail
KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEST_ROOT"' EXIT
for mode in copy symlink; do
  test_home="$TEST_ROOT/$mode"
  mkdir -p "$test_home/.codex"
  printf 'Operator-owned rule.\n' > "$test_home/.codex/AGENTS.md"
  for attempt in first reinstall; do
    HOME="$test_home" "$KIT_DIR/install.sh" --environment codex --features doc-harness \
      --mode "$mode" --on-exist overwrite --yes > "$TEST_ROOT/$mode-$attempt.log"
    python3 - "$KIT_DIR" "$test_home" <<'CHECK'
import json, pathlib, sys, tomllib
root, home = map(pathlib.Path, sys.argv[1:])
block = (root / 'shared/roles/block-mandate-completion.md').read_text().strip()
installed = (home / '.codex/AGENTS.md').read_text()
assert installed.count(block) == 1
assert installed.endswith('Operator-owned rule.\n')
assert '{{MANDATE_COMPLETION}}' not in installed
for path in (home / '.codex/agents').glob('*.toml'):
    assert block in tomllib.loads(path.read_text())['developer_instructions']
assert (root / 'shared/templates/AGENTS.block.md').read_bytes() not in block.encode()
manifest = json.loads((root / 'shared/roles/agents.json').read_text())
for entry in manifest.values():
    if entry['runtime'] == 'opencode':
        for budget in ('low', 'medium', 'high'):
            assert block in (root / entry['src'].format(budget=budget)).read_text()
assert block in (root / 'shared/skills/kit-role-rules/SKILL.md').read_text()
CHECK
  done
  HOME="$test_home" "$KIT_DIR/uninstall.sh" --yes > "$TEST_ROOT/$mode-uninstall.log"
  test "$(cat "$test_home/.codex/AGENTS.md")" = 'Operator-owned rule.'
done
printf 'Mandate completion installation, generation delivery and owner preservation: PASS\n'
