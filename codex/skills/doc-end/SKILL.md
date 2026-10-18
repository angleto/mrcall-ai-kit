---
name: doc-end
description: End repository work by reconciling living docs to code and session reality, running mechanical and semantic review, and advancing the baseline safely.
---

# Consolidate a documented work session

Read `WORKFLOW.md` beside this selected `SKILL.md` completely, then execute it.
Use the catalog-declared skill path unless repository instructions require a
local override and that individual entry exists. Resolve support files relative
to the selected entry, never another skill's directory.

The shared workflow may contain Claude-style command metadata or pre-injected shell snippets. Treat metadata as capability guidance and run indicated commands with Codex tools at the relevant step. When it requests `doc-critic`, resolve that skill independently from its catalog declaration and any required, present local override. Its `SKILL.md` is the complete critic workflow; there is no sibling `WORKFLOW.md`. Preserve all verification and baseline rules.
