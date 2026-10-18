---
status: active
---

# Resolve declared skill sources

Approved intent: [brief](../briefs/2026-10-18-skill-path-resolution.md).

## Ownership and dependencies

The lead owns all source and documentation changes. Reviewers own only bounded
external verdict artifacts, with a 90-second target per gate. No implementation
fan-out or paid native model acceptance. Preserve concurrent changes by explicit
path staging and diff inspection; initial working tree was clean.

## M1 — Resolution and instruction delivery

After brief and plan approval:

- Add a stdlib read-only `shared/scripts/skill-path.py` CLI accepting a required
  declared source and an optional explicitly required local entry. Expand home
  notation and anchor relative inputs to the current working directory; catalog
  aliases must be expanded from the actual declared mapping by the caller.
- Choose a readable regular local entry when supplied and present, otherwise
  the declared source. Report missing or unreadable selected sources clearly,
  with nonzero exit and empty stdout. Do not search alternate namespaces.
  Default output is the selected absolute entry path; `--read` outputs that
  entry only after validation. Keep supporting resources relative to its directory.
- Install the resolver once with doc-harness using existing manifest ownership
  and uninstall behavior. Do not refresh this operator's installation.
- Correct canonical repository instructions and this repository's matching block,
  generated Codex global entry, relevant wrappers and critic instructions. Wire
  the installed helper spelling with MRCALL_KIT_HOME/HOME, without personal paths.
  Resolve all batch inputs first; never treat partial output plus nonzero exit
  as a completed read.
- Exercise actual CLI cases in isolated fixtures: local present, absent local
  with valid installed declaration, missing declaration, and unrelated CS
  symlink with no local doc-start. Include path spaces, relative support files
  and invalid/unreadable sources where deterministic permissions permit.
- Run isolated copy/symlink installs and uninstall; assert helper delivery,
  catalog-to-installed-path reads, no local skill creation, manifest uniqueness,
  and operator content preservation. Update existing installation fixtures for
  the new required helper without weakening missing-source checks.
- Obtain milestone integration review before closure.

## M2 — Documentation and verified delivery

After M1 review:

- Reconcile the durable harness entry contract, README installation overview,
  changelog and living context. Record measured deterministic scope and limits;
  no universal model-compliance claim. Preserve any displaced narrative.
- Run configured mechanical check, generator consistency, focused CLI/install
  acceptance and affected migration/checker regressions. Reuse unchanged passing
  evidence; expand only for failures or materially affected contracts.
- Invoke doc-end and explicit doc-critic over affected documentation and living
  shape. Record actual results through a distinct completion task. Obtain a
  separate fresh final review of approved artifacts and actual CLI evidence.
- Finalize baseline and plan status through the checker, then commit only this
  assignment's paths. No release, push, operational clone edits or restarts.

## Verification and rollback

Tests invoke real Python CLI and isolated installed copies without model calls.
Instructions and their packaging are inspected alongside actual resolver outputs;
this does not establish that a model always chooses to invoke the resolver.
The regression includes the original concatenated-read failure as a negative
control, then the resolved individual skill read. External evidence stays under
`/tmp/mrcall-ai-kit/skill-path-resolution/`.

Rollback is a normal revert of this task's commits in ai-kit. Existing downstream
copies remain unchanged; symlinked instruction assets in this checkout can expose
source updates immediately, but no installation refresh is performed. Never
revert unrelated operator changes or copy skills into a clone as recovery.
