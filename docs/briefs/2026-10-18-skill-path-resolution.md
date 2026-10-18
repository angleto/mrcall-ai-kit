# Resolve declared skill sources

## Intent

Prevent kit instructions from turning an installed skill catalog entry into an
invented repository-local path. In the reported clone, a real CS skill read
succeeds before a concatenated read of absent `.agents/skills/doc-start/SKILL.md`
fails. The clone's CS workflow directory points to `.claude/skills`; it does not
supply the documentation harness skills.

## Scope and constraints

Correct the canonical repository protocol, Codex global entry, affected skill
wrappers and durable contract. Add a small installed read-only path resolver so
selection and failure diagnostics have deterministic CLI coverage. Use the path
declared by the current skill catalog, resolving its root aliases as declared.
Only explicitly required repository-local overrides participate; an absent local
entry falls back to the declared source. Resolve supporting files relative to
the selected skill entry. Validate sources before batching reads.

Changes are limited to ai-kit. Preserve unrelated work. Do not copy global
skills, hardcode operator home paths, suppress read failures, alter runtime
engines or cron, modify operational clones, restart sessions, or run paid model
acceptance. Commit after applicable reviews and documentation closure. Release,
push and refreshing operator installations are outside this assignment.

## Acceptance

- Identify and correct kit-owned instructions that suggest an invented local
  path; catalog locations remain authoritative when no usable required local
  override exists.
- Exercise the actual resolver CLI with a present local override, an absent
  local override plus valid declared installed source, and a missing declared
  source with a clear nonzero diagnostic and no content output.
- Verify a local CS directory/symlink does not imply a local doc-start exists;
  successful output from another read cannot mask a failed source resolution.
- Cover installation in isolated temporary homes, copy and symlink modes, and
  preserve uninstall/ownership behavior. Keep shared workflows and Codex copies
  synchronized; mechanical gate and generated-agent checks pass.
- Finish affected documentation, completion evidence, final review and commits.
  Deterministic tests establish resolver behavior, not universal model obedience.

## Assumptions

The runtime owns skill discovery and supplies the catalog. The kit consumes
those declarations; it must not invent another catalog or scan user directories
for a same-named replacement. Existing downstream copies need their normal
explicit refresh to receive updated instructions; this task changes none.
