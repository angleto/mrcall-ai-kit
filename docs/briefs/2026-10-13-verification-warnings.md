# Finish the agent-layer work with verification warnings

## Intent

The operator replaces the old agent-layer enforcement proposal with warnings:
missing verification must be visible without stopping a session or asking for
permission. Scope-guard work is accepted with its existing measured limits and
remaining acceptance tests waived; mandatory migration prerequisites are
superseded by the shipped upgrade UX. No further native matrix is requested.

## Scope

Reuse existing completion records, which already declare required focused and
mechanical checks and retain actual execution receipts. Add a read-only shared
advisory for an explicitly selected repository/task. Warn about missing,
failed, content-changing or stale required command evidence. Skip finalized
tasks before freshness calculations so later commits do not revive old warnings.

Supply optional, independently switchable adapters for Claude Code, Codex and
OpenCode. A runtime session must be explicitly bound to the same canonical repo,
worktree Git directory and task; unbound sessions stay silent. Hooks must return
success without blocking decisions, throwing errors, mutating tool output or
calling a model. Installation remains dormant unless activation is explicit.
Preserve foreign configuration and keep existing scope/reread hooks independent.

Retain existing completion refusal semantics. This feature observes required
recorded execution; it does not classify natural-language claims, authenticate
agent honesty, detect arbitrary unregistered checks or force lifecycle use.
Do not add another declaration/execution/receipt subsystem.

## Acceptance

- The installed advisory CLI reports precise missing, failed and stale required
  execution evidence, returns zero for warnings/errors and preserves repository
  files and completion records.
- Valid current receipts and finalized historical tasks are quiet. Explicit
  binding never guesses the newest task, reads unrelated tasks, or attaches a
  session to another repository/worktree.
- Runtime adapters emit advisory-only responses and stay silent when unbound;
  warnings are deduplicated. No session denial, permission request or model call.
- Installed on/off/status and uninstall preserve foreign hooks/plugins; normal
  and --yes installation do not activate the feature implicitly.
- User-facing docs and worker instructions distinguish the new warning from
  required completion gates and describe coverage/visibility limits honestly.
- Focused installed CLI acceptance and real registration roundtrips in isolated
  configuration verify deterministic behavior. Native model launches and broad
  suites remain deferred; unmeasured event visibility is not called supported.

## Delivery

Use a worker chain for planning, implementation, independent integration review,
doc-critic and final review. Preserve the historical plans and decisions. Close
the accepted scope-guard plan, supersede migration prerequisites, and close the
agent-layer plan after its revised warning requirement is delivered. Keep main
clean at closure; this task does not authorize a new release or tag.
