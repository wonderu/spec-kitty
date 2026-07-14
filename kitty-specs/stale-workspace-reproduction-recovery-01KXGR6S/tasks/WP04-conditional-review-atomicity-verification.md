---
work_package_id: WP04
title: Conditional review atomicity and verification
dependencies:
- WP03

requirement_refs:
- FR-003
- FR-004
- FR-005
- FR-006
- FR-007
- FR-008
- FR-009
- NFR-002
- NFR-003
- NFR-004
- C-001
- C-002
- C-003
- C-004
- C-005
- C-006
- C-008
tracker_refs: []
planning_base_branch: fix/stale-workspace-reproduction
merge_target_branch: fix/stale-workspace-reproduction
branch_strategy: Planning artifacts for this mission were generated on fix/stale-workspace-reproduction. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into fix/stale-workspace-reproduction unless the human explicitly redirects the landing branch.
subtasks:
- T016
- T017
- T018
- T019
- T020
- T021
agent: codex
history: []
agent_profile: python-pedro
authoritative_surface: src/specify_cli/cli/commands/agent/
create_intent: []
execution_mode: code_change
model: ''
owned_files:
- src/specify_cli/cli/commands/agent/workflow.py
- src/specify_cli/cli/commands/agent/workflow_executor.py
- tests/specify_cli/cli/commands/test_workspace_husk_resolution_1833.py
- tests/agent/test_workflow_review_lane_gate.py
role: implementer
tags: []
---

# WP04 — Conditional Review Atomicity and Verification

## ⚡ Do This First: Load Agent Profile

Run `/ad-hoc-profile-load python-pedro` before reading anything else. Adopt the
profile's implementer identity, governance scope, boundaries, and verification
discipline for the entire work package.

- **Profile**: `python-pedro`
- **Role**: `implementer`
- **Agent/tool**: `codex`

Then read, in order:

1. `kitty-specs/stale-workspace-reproduction-recovery-01KXGR6S/spec.md`
2. `kitty-specs/stale-workspace-reproduction-recovery-01KXGR6S/plan.md`
3. `kitty-specs/stale-workspace-reproduction-recovery-01KXGR6S/research.md`
4. `kitty-specs/stale-workspace-reproduction-recovery-01KXGR6S/data-model.md`
5. `kitty-specs/stale-workspace-reproduction-recovery-01KXGR6S/contracts/stale-workspace-transition-contract.md`
6. `kitty-specs/stale-workspace-reproduction-recovery-01KXGR6S/disposition-matrix.md`
7. The completed WP01 through WP03 review evidence.

---

## Objective

Conditionally repair the review action only where WP01's production-shaped
disposition proves a current-base RED: establish one reconciled execution
workspace before the review claim, track resources owned by this invocation,
and compensate those resources if a later operation fails. Preserve already-green
arms unchanged, keep PRIMARY tracking and COORD status at their canonical
placements, and finish with aggregate evidence that the original WP01 witness
remains unchanged and green.

## Context

Issue #2626 reports that stale lane-workspace metadata can make a transition fail
after durable tracking state has already changed. Research found a concrete review
ordering hazard: the review path may claim `for_review -> in_review` before
`_prepare_review_workspace` establishes that the execution workspace is usable.
It also found that review can resolve workspace state twice, permitting path or
branch disagreement between readiness and execution.

This WP is not authorization for a broad workflow refactor. WP01 owns the real-CLI
stale-workspace witness and the reviewed matrix carries the row-by-row
`stop`/`continue` disposition. WP03 owns conditional lifecycle reconciliation.
WP04 consumes both outputs and changes
production code only for review rows that are explicitly RED and marked
`continue`. A GREEN review row is a mandatory no-op arm: record the evidence,
run its regression tests, and do not edit production code for that behavior.

The governing state model is:

- `PersistedWorkspaceContext` is evidence, not proof that a path still exists.
- `CurrentLaneAssignment` is reconciled with persisted context once.
- One `ResolvedWorkspace` identity is passed unchanged through readiness,
  recovery, claim, review execution, and cleanup.
- `status.events.jsonl` remains the lane-state authority.
- PRIMARY owns WP/task tracking; COORD owns status in coordinated topologies.
- A successful result requires every intended placement commit and clean relevant
  checkouts; refusal requires zero durable deltas.

## Branch and Workspace Contract

- **Planning base and merge target**: `fix/stale-workspace-reproduction`.
- **Dependencies**: WP01 through WP03 must all be `approved` or `done` before WP04 is
  claimed. Do not bypass dependency gating.
- **Start command**:

  ```bash
  spec-kitty agent action implement WP04 --agent codex --mission stale-workspace-reproduction-recovery-01KXGR6S
  ```

- The action command resolves the computed lane workspace. Work only in the
  returned workspace path and current branch; do not create, guess, or reconstruct
  a worktree path from the Mission slug.
- Before editing, verify the Mission branch contract resolves to
  `fix/stale-workspace-reproduction` and that the allocated lane workspace is the
  path reported by the canonical action/branch-context surfaces.
- Completed WP04 changes merge back to `fix/stale-workspace-reproduction`. The
  existing pull request remains DRAFT; only the human operator may mark it ready
  or merge it.
- Stay inside the four owned files, except for the single justified acceptance
  file named below. If a proven RED requires any other out-of-map edit,
  stop and return a structured ownership finding to the orchestrator rather than
  silently expanding this package.

### Charter Exception Handling decision

ATDD / Reviewer Renata, Architect Alphonso, and the runtime-governance reviewer
have approved this exception as recorded in the disposition matrix. This is a
case-by-case Charter Exception Handling decision, not authority from generic
ownership-map leeway. WP04 must not consume it until WP02 is approved.

WP01 is canonically approved or done, inactive, and with a clean dependency lane.
Lane-b contains approved blob `d1f89937dc25353d74615d7305c97e9af00848ee`
at ref `ff7eca5e2`; WP02 then WP04 execute serially with no concurrent writer. The
exception covers one test-only file: WP04 may edit exactly
`tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py`
for these immutable pytest IDs only:

- `tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py::test_stale_workspace_transition_matrix[review-healthy]` (matrix row 9)
- `tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py::test_stale_workspace_transition_matrix[review-recoverable]` (matrix row 10)
- `tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py::test_stale_workspace_transition_matrix[review-unavailable]` (matrix row 11)
- `tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py::test_stale_workspace_transition_matrix[review-divergent]` (matrix row 12)

Record this one-line rationale in the test-only commit and review handoff:
`Charter exception: dependency witness rows 9–12 only; frozen harness, serial writer, no topology recomputation.`
The approved WP02 witness blob, recorded in WP02's review handoff, is WP04's
immutable dependency baseline.

Do not reorder or rename `_MATRIX`, its IDs, or row-number binding. Freeze fixture
construction, `_snapshot`, `_observe`, `_assert_common_record`, the registered
invocation path, all common six-surface measurements, and rows 1–8 against the
approved WP02 blob. Only state-specific desired-outcome branches for the four
named IDs may change.

Shared `owned_files` would recompute active topology, conflict with live
workspaces, and reproduce #2644. Duplicating the fixture is prohibited because a
parallel witness is fakeable. A fresh replacement Mission would discard truthful
reviewed state. Historical evidence and the frozen harness remain immutable; the
PR stays DRAFT and operator-only readiness/merge remains the final review.

This decision supersedes only ownership-map-leeway step 1 and its corresponding
failure mode for this file and these four nodes. It grants no general ownership.
Stop if any recorded approval is withdrawn or rejected. Stop unless WP01 is
canonically approved or done, inactive,
and with a clean dependency lane. Also stop if WP02 state/dependency evidence is
invalid, the lane-b ref/blob or approved WP02 blob differs, a concurrent writer
appears, or any frozen surface, other node/file, shared ownership, or topology
change is needed. Return a structured exception finding to the orchestrator.

### Subtask T016: Consume the disposition and preserve no-op GREEN arms

**Purpose**: Convert WP01 through WP03 evidence into an explicit authorization gate so
WP04 never performs speculative production work.

**Steps**:

1. Read every `agent action review` row in `disposition-matrix.md`, including:
   - baseline SHA and exact registered CLI argv;
   - workspace classification (`ready`, `recoverable`, `unavailable`, or
     `divergent`);
   - RED/GREEN verdict and `stop`/`continue` decision;
   - the six-surface before/after delta;
   - the reached production owner and placement result.
2. Read WP03's approved result and determine whether lifecycle reconciliation was:
   - activated and implemented for a proven RED;
   - characterized as already correct and left unchanged; or
   - blocked, in which case WP04 must not begin production edits.
3. Build a local implementation checklist mapping each review row to exactly one
   action:
   - `GREEN/stop`: no production edit; retain as a regression witness;
   - `RED/continue — ordering`: activate T017 through T019;
   - `RED/continue — review placement`: activate T020 only when the reached owner
     is one of WP04's workflow paths and the reviewed matrix checkpoint already records adjacency;
   - `RED owned elsewhere`: stop and report the ownership boundary.
4. Confirm the RED was witnessed on WP01's planning base through the registered
   command, not created by a helper-only test or a production monkeypatch.
5. Preserve the witness expectations. Do not weaken a failing assertion, relax a
   zero-delta requirement, or reclassify a row merely to make implementation green.
6. If all review rows are GREEN/stop, make no production changes. Run T021's
   aggregate verification, record the no-op disposition in the handoff, and finish.

**Files**:

- Read-only input: `disposition-matrix.md` and WP01 through WP03 evidence.
- No owned file must change for an all-GREEN disposition.

**Validation**:

- Every activated production edit points to a named RED/continue row.
- Every GREEN/stop row has zero behavior-changing diff.
- The handoff states whether T017–T020 were activated, skipped, or stopped.

### Subtask T017: Establish non-mutating readiness before claim

**Purpose**: For a proven review-ordering RED, ensure the command classifies and
establishes workspace readiness before any durable `for_review -> in_review`
mutation, using one reconciled identity throughout.

**Steps**:

1. Trace the live review command from `workflow.py` into `workflow_executor.py`.
   Identify the current ordering of:
   - Mission/WP context resolution;
   - canonical workspace resolution;
   - readiness/materialization;
   - review-lock acquisition;
   - status claim and WP tracking mutation;
   - commit routing and prompt/executor handoff.
2. Retain the canonical resolver as the single authority. Do not compose a branch,
   lane name, or `.worktrees/...` path at the command call site.
3. Introduce or adapt the smallest internal input/result shape needed to carry the
   same `ResolvedWorkspace` value through the review path. Prefer an existing typed
   value over a new parallel model.
4. Split readiness into a non-mutating classification/validation phase and, only
   for `recoverable`, an invocation-owned acquisition phase.
5. Order the path so `ready` and successfully recovered workspaces reach claim,
   while `unavailable` and `divergent` results fail before:
   - event append or materialization;
   - WP tracking mutation;
   - any PRIMARY or COORD ref movement;
   - lock persistence or orphaned worktree creation.
6. Preserve actionable diagnostics from the canonical seam. The error must name
   the missing path or lane and a supported recovery action without leaking a raw
   `FileNotFoundError` or inventing a misleading coordination path.
7. Preserve JSON/human output ownership. Do not print incidental diagnostics to
   stdout in JSON mode.
8. Add focused tests in the owned test modules for ordering and identity reuse.
   Assert readiness occurs before claim and the downstream consumer receives the
   exact resolved object or immutable identity, not a recomputed equivalent.

**Files**:

- `src/specify_cli/cli/commands/agent/workflow.py`: minimal orchestration ordering
  and canonical resolved-workspace threading.
- `src/specify_cli/cli/commands/agent/workflow_executor.py`: executor input and
  readiness-before-mutation sequencing where this module owns it.
- `tests/specify_cli/cli/commands/test_workspace_husk_resolution_1833.py`: focused
  stale/recoverable/unavailable readiness tests.
- `tests/agent/test_workflow_review_lane_gate.py`: review claim-order and identity
  propagation tests.

**Validation**:

- An unavailable/divergent workspace produces no claim call and no durable delta.
- A ready/recoverable workspace reaches claim only after readiness succeeds.
- Resolver invocation count and object-identity assertions prove resolve-once.
- Existing healthy review behavior and output remain unchanged.

### Subtask T018: Track invocation-owned recovery and lock resources

**Purpose**: Make acquisition ownership explicit so later cleanup removes only
resources created or acquired by the current review invocation.

**Steps**:

1. Inspect `_prepare_review_workspace` and the current review-lock API before
   designing a result. Reuse existing ownership signals where present.
2. Represent, without global mutable state, the resources the current invocation
   owns, including at minimum:
   - whether it created or attached the lane worktree;
   - the exact canonical workspace path;
   - whether it acquired the review lock;
   - the lock identity/token needed for safe release.
3. Do not infer ownership from `Path.exists()` after the operation. Record it at
   the acquisition boundary so a pre-existing worktree is never mistaken for an
   invocation-created one.
4. Preserve the existing behavior for a workspace that was already ready:
   - do not recreate it;
   - do not mark it invocation-created;
   - acquire only the resources the review action already requires.
5. For a recoverable husk, allow materialization only after WP03/canonical
   reconciliation confirms an agreeing existing branch.
6. For branch absence or identity divergence, return refusal without attempting
   worktree creation or lock acquisition.
7. Ensure active-lock conflicts remain hard failures and do not remove the other
   invocation's lock.
8. Extend the husk tests to cover pre-existing versus invocation-created resources,
   lock conflicts, worktree-add failure, and successful acquisition ordering.

**Files**:

- `workflow.py` and/or `workflow_executor.py`: invocation-local ownership result
  and propagation, kept at the narrow existing review seam.
- `test_workspace_husk_resolution_1833.py`: resource-ownership and failure tests.
- `test_workflow_review_lane_gate.py`: live review orchestration assertions.

**Validation**:

- Tests distinguish pre-existing, recovered-by-this-invocation, and unavailable
  workspaces.
- No failed acquisition leaves a lock or newly created path behind.
- No cleanup path removes a pre-existing worktree or another invocation's lock.
- No module-level receipt or mutable singleton becomes cleanup authority.

### Subtask T019: Compensate invocation-owned resources on later failure

**Purpose**: If claim, placement commit, prompt construction, or another later
review step fails after readiness, restore invocation-owned resources without
rolling back or deleting pre-existing authority.

**Steps**:

1. Enumerate failure points after readiness and before the command hands control to
   a successfully started reviewer. Tie each failure to its durable-state boundary.
2. Prefer ordering that prevents mutation. Compensation is a last resort for
   resources acquired during readiness, not a substitute for preflight.
3. Add one structured cleanup path that runs for every post-readiness exception or
   refusal and receives the invocation ownership record from T018.
4. Release a review lock only when this invocation acquired that lock.
5. Remove a worktree only when this invocation created or attached it and removal
   is safe through the existing Git/worktree abstraction.
6. Never remove a pre-existing worktree, delete persisted workspace context, erase
   a canonical lane branch, or fall back to raw directory deletion.
7. Preserve the original failure as the operator-visible outcome. Cleanup failure
   may add diagnostic context but must not turn the command into success or hide the
   primary cause.
8. Add failure-injection tests at meaningful later boundaries. Each test snapshots
   before/after lock state, path existence, status/WP bytes, refs, and porcelain as
   appropriate to the reached boundary.
9. Prove idempotent or guarded cleanup: repeated cleanup attempts do not remove
   resources the invocation no longer owns.

**Files**:

- `workflow.py` / `workflow_executor.py`: narrow exception-safe lifetime around
  readiness, claim, and executor handoff.
- Both owned test modules: focused compensation and non-ownership regression tests.

**Validation**:

- Later failure releases invocation-owned lock state.
- Later failure removes only an invocation-created worktree.
- Pre-existing workspace and lock authority remain untouched.
- The command remains non-zero and truthful when cleanup also reports a problem.

### Subtask T020: Handle a proven placement RED without absorbing issue #2160

**Purpose**: If and only if WP01 proves the review bookkeeping bundle commits at
the wrong authority, adapt review to the existing partition-aware commit seam while
recording the finding as adjacent to #2160 rather than claiming or closing it.

**Steps**:

1. Activate this subtask only when the disposition matrix has an explicit
   `RED/continue — placement` review row with ref/path-set evidence.
2. Before production editing, confirm the reviewed matrix checkpoint already
   recorded the #2160-adjacent residual in `issue-matrix.md`. WP04 does not own
   that planning surface and must
   not edit it directly.
3. Do not assign, claim, comment on, close, or otherwise change issue #2160.
4. Trace the repository's canonical partition-aware commit router. Confirm how it
   maps WORK_PACKAGE_TASK tracking to PRIMARY and STATUS_STATE to COORD under the
   stored topology.
5. Adapt the review path to that seam. Do not hand-roll two Git commits, commit the
   mixed bundle through the coordination transaction, or fall back to whichever
   checkout happens to exist.
6. Preserve one truthful aggregate outcome: success only when every required
   placement commit succeeds and all relevant checkouts are clean.
7. On placement refusal/failure, preserve the contract established by the RED:
   never report overall success alongside an uncommitted tracking mutation.
8. Add tests that enumerate new commit ranges and committed path sets, proving WP
   tracking lands on PRIMARY and status lands on COORD where topology requires it.
9. If no canonical partition-aware seam can be consumed within owned files, stop
   and return an architectural ownership finding. Do not invent one inside workflow.

**Files**:

- Production edits remain limited to `workflow.py` and `workflow_executor.py`.
- Focused placement assertions belong in `test_workflow_review_lane_gate.py`.
- `issue-matrix.md` is orchestrator-owned, reviewed read-only input; PR progress is
  orchestrator-owned follow-through, not a WP04 file edit.

**Validation**:

- Commit path sets prove canonical PRIMARY/COORD partitioning.
- Failure cannot produce success-plus-dirt or success-plus-warning.
- No implementation or tracker action claims to resolve #2160.
- GREEN placement rows remain behaviorally unchanged.

### Subtask T021: Run aggregate GREEN gates and preserve the WP01 witness

**Purpose**: Demonstrate that every activated remediation closes its exact RED,
healthy review behavior remains stable, and no gate was weakened to manufacture a
green result.

**Steps**:

1. Before production changes, author and commit the test-only desired contract for
   the four named review IDs while preserving rows 1–8 and all frozen surfaces
   byte-for-byte against the approved WP02 blob.
2. Run the four exact pytest IDs on the dependency base and prove them RED for the
   reviewed production behavior. Only then begin production implementation.
3. Require every former RED/continue review row to be GREEN with six-surface
   observation and coverage intact; expected deltas may change only for the four
   named nodes and only to the pre-production desired contract.
4. Require every original GREEN/stop row and healthy positive-control twin to stay
   GREEN with byte-compatible public outcomes.
5. Run the complete owned test surfaces:

   ```bash
   PWHEADLESS=1 uv run --extra test pytest \
     tests/specify_cli/cli/commands/test_workspace_husk_resolution_1833.py \
     tests/agent/test_workflow_review_lane_gate.py -q
   ```

6. Run the dependency-ordered acceptance module using the exact command documented
   by WP01. Do not substitute a narrower helper test or change the test-only
   desired contract after production implementation begins.
7. Run focused regression suites named by WP01 through WP03 for healthy workspace and lane
   lifecycle behavior, including WP03's integration module when WP03 activated.
8. Run lint and strict typing on every changed production/test file, including
   the justified out-of-map acceptance witness:

   ```bash
   uv run ruff check \
     src/specify_cli/cli/commands/agent/workflow.py \
     src/specify_cli/cli/commands/agent/workflow_executor.py \
     tests/specify_cli/cli/commands/test_workspace_husk_resolution_1833.py \
     tests/agent/test_workflow_review_lane_gate.py
   uv run mypy --strict \
     src/specify_cli/cli/commands/agent/workflow.py \
     src/specify_cli/cli/commands/agent/workflow_executor.py
   ```

9. Run the architectural checks relevant to shared-package boundaries, placement,
   dead symbols, and terminology. At minimum include:

   ```bash
   PWHEADLESS=1 uv run --extra test pytest \
     tests/architectural/test_shared_package_boundary.py \
     tests/architectural/test_no_legacy_terminology.py -q
   ```

   Add any non-vacuous placement/authority guard identified by WP01, WP03, or WP04.
10. Run `git diff --check` and verify every relevant checkout has clean porcelain
   after the test run.
11. Report activated versus skipped subtasks, exact commands, counts, the approved
    WP02 blob, the one-line out-of-map rationale, and any
    remaining externally owned issue in the review handoff. Never retry-to-green.

**Files**:

- No new files are expected.
- Test updates remain within the two owned test modules plus the single justified
  out-of-map acceptance file.
- The out-of-map acceptance diff is limited to the pre-production desired-outcome
  branches for the four exact review IDs; frozen construction/observation surfaces
  and earlier reviewed evidence remain immutable.

**Validation**:

- The dependency-ordered acceptance witness is GREEN, with rows 1–8 and common
  six-surface coverage preserved from the approved WP02 blob.
- Existing healthy review tests and all three owned test modules are GREEN.
- Ruff, strict mypy, architectural checks, terminology guard, and diff check pass.
- Relevant worktrees are clean and the DRAFT PR boundary remains intact.

## Definition of Done

- [ ] WP01 through WP03 are approved/done and their dispositions were consumed before
      any WP04 production edit.
- [ ] Every production edit is authorized by a named `RED/continue` review row.
- [ ] Every `GREEN/stop` arm remains a no-op with regression evidence.
- [ ] Review workspace classification/readiness occurs before claim mutation.
- [ ] One reconciled workspace identity is passed through readiness and execution.
- [ ] Invocation-owned worktree and lock resources are tracked explicitly.
- [ ] Later failure compensates only resources owned by this invocation.
- [ ] Unavailable/divergent refusal leaves status, tracking bytes, refs, locks,
      paths, and porcelain unchanged.
- [ ] If placement work activated, canonical PRIMARY/COORD routing is proven by
      commit path sets and #2160 remains unclaimed/unclosed by this Mission.
- [ ] Earlier approved evidence is immutable; the test-only desired contract was
      RED before production and is GREEN after changes limited to the four exact
      review IDs.
- [ ] Owned tests, healthy regressions, Ruff, strict mypy, architectural checks,
      terminology guard, and `git diff --check` are GREEN.
- [ ] Review handoff lists exact evidence and skipped conditional work.
- [ ] Changes remain on the resolved WP04 lane and target
      `fix/stale-workspace-reproduction`; the PR remains DRAFT.

## Risks

- **Speculative repair**: implementing an imagined review defect would violate
  FR-003. Mitigation: T016 makes the reviewed matrix an explicit authorization gate.
- **Second resolver**: recomputing a path in workflow can disagree with lifecycle.
  Mitigation: pass one canonical `ResolvedWorkspace` identity end to end.
- **Premature mutation**: claim before readiness recreates the reported atomicity
  gap. Mitigation: classify and establish readiness before any durable transition.
- **Over-cleanup**: compensation could delete a pre-existing worktree or foreign
  lock. Mitigation: record ownership at acquisition and clean only owned resources.
- **Placement scope creep**: the mixed bundle can pull #2160 into this Mission.
  Mitigation: require exact RED evidence, record adjacency, and consume only the
  existing partition-aware seam.
- **False green**: helper tests can bypass the registered CLI and real Git state.
  Mitigation: the dependency-ordered real-CLI witness remains the acceptance
  authority, frozen common six-surface measurements prevent coverage shrinkage,
  and earlier reviewed commits preserve the original RED evidence.
- **Output corruption**: incidental logs can break one-document JSON output.
  Mitigation: assert structured output and keep diagnostics on the owning channel.

## Reviewer Guidance

The reviewer must load a reviewer profile distinct from `python-pedro` and reject
the WP if implementation begins without a WP01 RED/continue disposition. Review
the aggregate diff against the following questions:

1. Does review establish workspace readiness before `for_review -> in_review`?
2. Is exactly one canonical workspace identity resolved and threaded through the
   whole invocation, or does any call site reconstruct branch/path state?
3. Are created worktrees and acquired locks recorded as invocation-owned at the
   moment of acquisition?
4. Does cleanup leave pre-existing and foreign resources untouched?
5. Do unavailable/divergent cases prove an empty ref range and byte-identical
   status/WP evidence, not merely a non-zero exit?
6. If placement changed, are PRIMARY and COORD path sets proven through the
   canonical router, with #2160 only referenced as adjacent?
7. Is the approved WP02 blob recorded, are rows 1–8 and frozen surfaces unchanged,
   and did the four exact review IDs go RED in a test-only commit before the same
   contract passed through the registered CLI with real Git/worktree state?
8. Are GREEN/no-op arms preserved without production churn?
9. Are all new branches directly exercised without suppressions, complexity growth,
   timing-only assertions, or retry-to-green behavior?
10. Does the branch/workspace evidence show the resolved WP04 lane targets
    `fix/stale-workspace-reproduction` and the PR remains DRAFT?

Approve only when the durable outcome, structured result, resource lifetime, and
canonical placement all tell the same story.
