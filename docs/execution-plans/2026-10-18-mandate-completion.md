---
status: completed
---

# Mandate completion execution plan

Approved brief: [mandate completion](../briefs/2026-10-18-mandate-completion.md).
Lead owns implementation, integration, trials and documentation closure.
Each reviewer receives one read-only gate, a concrete deliverable and a three
minute limit. No implementation delegation or automatic paid retry loop.

## Constraints

Startup and configured build passed at baseline
`e62a5a011950125bdab3510184b3849b211ec161`. Keep the canonical v9 repository block
unchanged. Use isolated installs; no changes to REMOTE, operator configuration,
model choice, production, commits or release. Disk exhaustion interrupted the
first plan write; only regenerable Python/pip caches were removed to recover
space. Use memory-backed scratch for native artifacts if disk remains constrained.

## M1 — deliver the decision to yield

Add one source block under shared/roles/ checking completion of the whole bounded
mandate, unmet acceptance, useful authorized next action and legitimate stops.
Keep independent work moving while one branch waits; preserve authorization and
resource limits. Carry pending obligations in existing plans/handoffs, without
a parallel task database or always-on reviewer. Questions, briefs and reviews
remain bounded to the requested artifact. Workers assess their own assignment.

Compose the block into generated final-answer procedures and Codex's existing
global kit AGENTS entry. Move its static text into an explicit template and
extend the existing generator; regenerate rather than edit composed output.
The six evidence/style checklist items remain intact. Preserve operator-only
sc/av invocation. Codex fresh leads receive the rule with doc-harness installation;
OpenCode generated leads and all kit workers receive it through existing paths.
Claude ordinary leads have no existing global installer route in this scope:
document that gap, without claiming coverage or creating a global CLAUDE route.

Add a free CLI test of isolated copy/symlink installs, installed global content,
operator-owned text preservation, reinstall and uninstall. Run existing generation,
reread-install and relevant Codex-agent install checks. Retain actual command
outputs outside repository content. Fresh M1 reviewer approves before M2.

## M2 — observe native behavior

Add an opt-in Python acceptance runner under tests/; never call a paid client
from a default free suite. Use native codex exec JSONL with isolated installed
global instructions and scratch repositories. Do not paste the rule into prompts.
Reuse configured auth without printing or changing secrets, retain the operator's
model/reasoning choice, and disable unrelated integrations in isolated config.
Record actual runtime/configuration and differences from interactive operation.

Nine conversations: multi-step task without status question; recoverable failed
CLI check; status request with an explicit active mandate; resumption from an
existing unfinished plan; indispensable ungranted authorization; read-only
question; brief-only artifact; explicit pause; explicit tool-action/resource cap.
Resumption tests supplied state, not actual client compaction. Positive acceptance
requires real output artifacts and actual passing CLI verification before yielding.
Fixture checks record invocations, so prose claims cannot substitute for execution.
Negative cases assert forbidden effects absent and allowed artifacts present.

Run sequentially, stop the matrix on its first failure, diagnose and repair before
rerun. At most ten attempted native conversations for this workstream including
failures/retries; runner counts persisted attempts and refuses excess. Each has
180-second process-group timeout, bounded output configuration where supported,
prompt limit of eight tool calls and no delegation or external services.
Retain JSONL/final output, exact argv/configuration, elapsed time, exit and reported
usage. Missing auth/runtime or exhausted cap blocks acceptance; never call it a
pass. No native Claude/OpenCode calls: their delivery can be checked freely,
behavior remains explicitly unverified. Free runner self-checks precede paid use.
Fresh M2 reviewer judges artifacts and limits. Samples prove no universal adherence,
interception, actual compaction persistence or interactive UI behavior.

## M3 — closure and final review

Reconcile docs/reread-guard.md, shared/roles/README.md, relevant README installation
instructions, docs/documentation-harness.md and docs/active-context.md. Include
unchanged docs/harness-runtime-support.md as a claim boundary. Preserve historical
narrative and archive displaced living context verbatim if needed. Record actual
native results and unsupported surfaces, never just source delivery.

Run doc-end: impact/reconciliation, mechanical, explicit doc-critic including
living-context shape, keywords, focused evidence and pre-review completion check.
Then a separate fresh final reviewer checks integrated evidence. Initialize one
development completion record declaring this brief/plan, M1 and M2 sources as this
plan, and active-to-completed transition. Retain immutable artifacts with real raw
verdicts at each gate. Progress notes may change without changing approved scope.
Finalize baseline/status only with the checker after final approval. Required
acceptance failures cannot be waived as nonblocking deferrals.

## Verification and rollback

Commands: bash tests/test_agents_generated.sh; bash tests/test_reread_install.sh;
new isolated lead-install test; new runner free self-check; relevant Codex installer
suite; configured build. Final focused command validates retained native evidence
and reruns free checks, without buying another matrix. Rollback reverts only this
task's source/generated edits. Isolated installs do not affect the operator's home.

## Gate record

- Brief: APPROVED, completion_brief_review; raw report retained outside repository.
- Plan: APPROVED, completion_plan_review.
- M1: APPROVED, completion_m1_review; generation/install/reread/Codex suites pass.
- M2: APPROVED, completion_m2_review; nine native cases pass after free assessor repair.
- Closure and separate final review: authoritative verdicts are in completion task
  `mandate-completion-20261018`.

## Acceptance result references

Evidence root: `/tmp/mrcall-ai-kit/mandate-completion/`. Immutable approved
brief/plan/M1/M2 versions and raw review reports are retained there. M1 logs:
`M1-generation.log`, `M1-install.log`, `M1-reread.log`, `M1-roles.log`.
Native records: `native/summary.json`, original per-case `result.json` and JSONL;
free re-evaluation: `native/reassessment.json`, per-case `result-reassessed.json`,
`M2-reassessed.log`. Full limits and observations: `native-acceptance-notes.txt`.

Nine native Codex 0.163.0 conversations took 207.472 seconds. Reported cumulative
input/cached-input/output/reasoning tokens: 713968/565888/5499/797, excluding
review workers. The original resource-cap assessment rejected shell quoting;
shlex parsing and a free self-check repair that evaluator. Actual native evidence
was retained, rechecked without paid retries, and independently reviewed. The
original running monitor counted shell commands; reassessment checks total tool
items against the current expanded monitor. No candidate/source rule changed
between those trials. The brief-only fixture's unnecessary startup attempt does
not establish lifecycle compliance. No old-rule control group, interactive trial,
true compaction trial, universal reliability, or native other-runtime adherence
is claimed. Auth copies are removed; no global installer has run and REMOTE has
not been controlled. Codex's physical AGENTS entry and role copies need refresh;
source-linked Claude/OpenCode assets already reflect checkout edits. Release and
explicit global installation remain outside this task.
