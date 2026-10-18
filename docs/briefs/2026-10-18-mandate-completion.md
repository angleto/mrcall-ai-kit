# Finish the authorized mandate before yielding

## Intent and observed failure

An agent can accurately report unfinished work and still fail its assignment by
ending the turn while useful authorized work remains. The operator reports this
across sessions. In the inspected REMOTE transcript, the lead ended with an
unfinished operator, then resumed executable work after another user prompt.
This is a decision-to-stop failure, not primarily a wording or status-question
problem. A status question is only one regression case.

The shipped six-item re-read checklist checks evidence and presentation. It has
no explicit mandate-completion decision. Generated role agents receive it, but
the Codex lead's global kit block does not contain that checklist. General
persistence instructions were present in REMOTE and did not prevent the stop.

## Scope and constraints

Strengthen the lead's decision before yielding and the shared final-report
checklist. Deliver the instruction through the existing supported entry points;
verify actual delivery rather than inferring it from generated worker profiles.
Use existing plans/handoffs for active intent, acceptance criteria, unfinished
obligations and blockers across resumption. Add no parallel task database,
always-on reviewer, automatic retry loop, or operator-only skill invocation.

Continue only within authorized scope and explicit resource limits. Valid stops
include verified completion, explicit pause/cancellation, an indispensable user
input or authorization, an external blocker leaving no useful independent work,
and an actual resource/runtime limit. Record remaining work and the concrete
blocking condition when yielding incomplete. Avoid repeated attempts without
new evidence. Honest incompleteness alone does not justify yielding.

Apply the rule to the entire open mandate, incorporating subsequent corrections.
A question, brief-only or review-only assignment is complete when its requested
artifact is delivered; it must not trigger unsolicited implementation. A genuine
status request during active execution is answered without silently cancelling
the existing mandate. Preserve authorization boundaries and existing reviews.
Workers judge completion against their bounded assignment, not the lead's whole
project. Do not turn the rule into unlimited spending or autonomous publication.

Keep protocol version 9 and existing lifecycle/migration contracts. Prefer the
existing global instruction integration and role generation; do not rewrite the
canonical managed v9 repository block merely to ship this behavior improvement.
Do not alter active REMOTE or unrelated sessions. No release, push, production
change, or global installation is authorized by this task; use isolated installs.

## Acceptance

1. Native lead entry points covered by this change receive a concise explicit
   decision: identify the open result and unmet acceptance; if a useful authorized
   next action exists within limits, perform it before yielding. Docs state exact
   entry points, installation/restart requirements, and unsupported paths.
2. Shared reports distinguish factual accuracy from justified stopping. Generated
   agents remain reproducible and retain their fixed headers and scope limits.
3. A bounded native Codex trial through an isolated installed lead entry proves
   actual artifact completion without a user prompt to continue. Cases cover a
   multi-step task without a status question, a recoverable failed check, a later
   status question, and resumption with explicit unfinished mandate context.
4. Negative cases prove legitimate stopping: missing indispensable authorization,
   a read-only question, a brief-only request, explicit pause, and a resource cap.
   Assertions use observable artifacts/tool activity and side-effect boundaries,
   not an LLM grading its own prose or a checklist marker.
5. Run deterministic install/generation checks before paid native trials. One
   fixed small matrix, at most ten native conversations, each at most three
   minutes and a bounded turn/output budget; record usage when available and
   wall time regardless. Stop failing candidates and fix from evidence before
   any bounded rerun. Do not consume other clients' credit without a concrete
   native verification need; distinguish delivery tests from behavior evidence.
6. Report pass/fail per case, actual runtime/configuration, command and output
   references, and limits. A passing sample establishes bounded observations,
   never universal adherence or interception. Required acceptance failures block
   completion; unavailable credentials/runtime are concrete blockers, not passes.

## Assumptions and risks

Instruction following is probabilistic. Codex currently has no demonstrated
final-answer interceptor in this repository. This change must not claim one.
An instruction can pass the small matrix without proving reliability across
long sessions or compactions; explicit resumption tests cover supplied context,
not automatic preservation by every client. Other runtimes may receive the rule
without native behavioral evidence and must be labelled accordingly.

Review the brief, then the execution plan, then each integrated milestone and a
separate final-user-path review. Reconcile affected durable docs and living
context through doc-end before baseline finalization. Preserve actual evidence
outside repository prose. Release remains a separately authorized action.
