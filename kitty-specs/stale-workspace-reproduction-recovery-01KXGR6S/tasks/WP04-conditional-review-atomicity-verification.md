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
- FR-010
- FR-011
- FR-012
- FR-013
- FR-014
- FR-015
- FR-016
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
- C-009
- C-010
- C-011
- C-012
- C-013
- C-014
- C-015
plan_concern_refs:
- IC-02
- IC-04
- IC-06
- IC-07
- IC-08
- IC-09
- IC-10
tracker_refs: []
planning_base_branch: fix/stale-workspace-reproduction
merge_target_branch: fix/stale-workspace-reproduction
branch_strategy: Planning artifacts for this mission were generated on fix/stale-workspace-reproduction. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into fix/stale-workspace-reproduction unless the human explicitly redirects the landing branch.
subtasks:
- T022
- T023
- T024
- T025
history: []
agent_profile: python-pedro
authoritative_surface: src/specify_cli/cli/commands/agent/
create_intent:
- src/specify_cli/status/review_transaction.py
- tests/specify_cli/status/test_review_transaction.py
- tests/architectural/test_review_receipt_producer_gate.py
- tests/specify_cli/git/test_ref_advance.py
execution_mode: code_change
model: ''
owned_files:
- src/specify_cli/cli/commands/agent/workflow.py
- src/specify_cli/cli/commands/agent/workflow_executor.py
- src/specify_cli/coordination/types.py
- src/specify_cli/coordination/transaction.py
- src/specify_cli/coordination/status_transition.py
- src/specify_cli/coordination/outbound.py
- src/specify_cli/coordination/commit_router.py
- src/specify_cli/git/commit_helpers.py
- src/specify_cli/git/ref_advance.py
- src/specify_cli/status/review_transaction.py
- src/specify_cli/status/work_package_lifecycle.py
- src/specify_cli/sync/local_commit.py
- tests/agent/test_workflow_review_lane_gate.py
- tests/architectural/test_review_receipt_producer_gate.py
- tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py
- tests/specify_cli/cli/commands/test_workspace_husk_resolution_1833.py
- tests/specify_cli/coordination/test_commit_router_partition.py
- tests/specify_cli/coordination/test_status_transition.py
- tests/specify_cli/coordination/test_transaction.py
- tests/specify_cli/coordination/test_types.py
- tests/specify_cli/coordination/test_outbound.py
- tests/specify_cli/git/test_commit_helpers.py
- tests/specify_cli/git/test_ref_advance.py
- tests/specify_cli/sync/test_local_commit.py
- tests/specify_cli/status/test_review_transaction.py
- tests/status/test_work_package_lifecycle.py
role: implementer
tags: []
shell_pid_created_at: "1784023781.31"
shell_pid: "138606"
agent: "codex"
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
7. `docs/adr/3.x/2026-07-14-2-cross-partition-workflow-transaction.md`
8. The completed WP01 through WP03 review evidence and both preserved WP04 review cycles.

---

## Objective

Conditionally repair the review action only where WP01's production-shaped
disposition proves a current-base RED: establish one reconciled execution
workspace before the review claim, track resources owned by this invocation,
and compensate those resources if a later operation fails. Preserve already-green
arms unchanged, keep PRIMARY tracking and COORD status at their canonical
placements, and finish with aggregate evidence that the original WP01 witness
remains unchanged and green.

The reviewed operator amendment now completes only the architectural gap found after
review cycle 2: Mission Management owns the review-only PRIMARY+COORD composite,
canonical receipts and typed post-commit failure drive reverse CAS compensation, and
outbound effects wait for local commit. The earlier readiness/resource implementation
is preserved; amendment work begins at T022.

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
- Stay inside the expanded `owned_files` frontmatter list. It is the reviewed
  operator-authorized WP04 scope amendment; it does not alter dependencies, lane-d,
  the prompt ID, or topology. Stop if implementation requires any other file.

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

### Reviewed operator scope amendment — binding

The operator directed the architectural ownership finding to be folded into this
same WP04. IC-01 through IC-06, WP01 through WP03 approvals, witness commit
`980eae6a9`, remediation commit `eaff3130c`, approved WP02 witness blob
`48ca83d8091dde8cd288fc7905ea6c128aec62f8` at ref `8289cf39`, both WP04 review
cycles, and all existing activity history are immutable inputs. T016 through T021
are historical execution records and MUST NOT be re-executed, reinterpreted, or used
to reactivate rows 1–8 or adjacent-ticket work. Amendment execution starts at T022.

The frozen acceptance witness remains governed only by the earlier Charter exception.
Its fixture, `_MATRIX`, ordering, registered invocation, observation helpers, rows 1–8,
and the row 9–12 desired contract committed at `980eae6a9` are byte-frozen. There are
no post-`980eae6a9` expectation edits. New failure coverage belongs in the newly named
focused tests and direct Mission Management integration, not in witness expectations.

#### Narrow shared-file Charter Exception Handling

WP04 may edit the WP02-owned files below only for the composite receipt adapter and
its focused regression:

- `src/specify_cli/coordination/commit_router.py`
- `tests/specify_cli/coordination/test_commit_router_partition.py`

This exception is valid because WP02 is approved, inactive, and has a clean dependency
lane; its approved witness blob/ref above is frozen; WP04 is the sole serial writer; and
no topology recomputation occurs. It grants no authority over any other WP02 file or
behavior. Stop if an approval is withdrawn, a concurrent writer appears, the approved
blob/ref differs, the frozen witness changes, or the edit cannot remain limited to
Git-evidence-to-canonical-receipt adaptation. Do not run `finalize-tasks`, edit
`lanes.json`, add a WP, or recompute ownership topology.

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

### Subtask T022: Ratify the ADR and land the mandatory test-only RED contract

**Purpose**: Convert the reviewed scope amendment into immutable ATDD evidence before
any new production edit.

**Steps**:

1. Verify `docs/adr/3.x/2026-07-14-2-cross-partition-workflow-transaction.md`
   remains Proposed and matches FR-010 through FR-016 and C-009 through C-015.
2. Create one test-only commit. It MUST change only the newly owned test files; it
   MUST NOT edit production, the frozen witness, or any post-`980eae6a9` expectation.
3. Add the receipt producer gate first with these exact nodes:
   - `tests/architectural/test_review_receipt_producer_gate.py::test_receipt_producer_floor_is_non_vacuous`
   - `tests/architectural/test_review_receipt_producer_gate.py::test_receipt_producer_allowlist_is_shrink_only`
   - `tests/architectural/test_review_receipt_producer_gate.py::test_receipt_producer_gate_rejects_self_mutation`
4. Freeze this exact initial producer floor as `(file, qualified symbol)` tuples; the
   gate compares AST-resolved construction/adapter call sites, not text matches:
   - (`src/specify_cli/coordination/transaction.py`,
     `BookkeepingTransaction.commit`)
   - (`src/specify_cli/coordination/status_transition.py`,
     `emit_status_transition_transactional`)
   - (`src/specify_cli/coordination/status_transition.py`,
     `emit_status_transition_batch_transactional`)
   - (`src/specify_cli/coordination/commit_router.py`,
     `_commit_partition_group`)
   The first tuple is the reviewed current constructor and the remaining tuples are
   the only authorized Git-to-coordination adapter sites. No workflow constructor is
   allowed. The self-mutation node MUST inject an unauthorized production call site,
   run the gate and prove rejection, then restore the production file byte-for-byte
   in `finally`; a synthetic test-file-only mutation is insufficient.
5. Add these exact real-Git nodes in
   `tests/specify_cli/status/test_review_transaction.py`:
   - `test_missing_coord_receipt_is_compensation_failed`
   - `test_wrong_coord_hash_is_compensation_failed`
   - `test_duplicate_destination_receipt_is_compensation_failed`
   - `test_mismatched_attempt_ids_are_compensation_failed`
   - `test_unattributed_ref_movement_is_compensation_failed`
   - `test_attempt_id_pair_is_inherited_by_all_evidence`
   - `test_committed_requires_exact_primary_and_coord_receipts`
   - `test_refused_has_zero_delta_and_zero_receipts`
   - `test_non_success_has_zero_outbound_attempts[refused]`
   - `test_non_success_has_zero_outbound_attempts[compensated]`
   - `test_non_success_has_zero_outbound_attempts[compensation_failed]`
   - `test_outbound_is_not_attempted_before_local_commit`
   - `test_review_transaction_lock_order_is_resource_status_git`
   - `test_primary_hook_failure_compensates_reverse_order`
   - `test_foreign_coord_helper_blocks_expected_old_cas`
   - `test_post_commit_recovery_conflict_uses_error_carried_receipt`
   - `test_post_cas_resync_obstruction_is_compensation_failed`
   - `test_internal_retry_reuses_invocation_id_and_rotates_transaction_id`
   - `test_file_backed_outbound_middle_failure_continues_later_channel`
6. Add
   `tests/status/test_work_package_lifecycle.py::test_review_lifecycle_reuses_held_status_lock_without_implicit_commit`
   and an architectural node
   `tests/architectural/test_review_receipt_producer_gate.py::test_git_layer_does_not_import_coordination_receipt_types`.
7. Use deterministic fixture-owned stimuli and assert each reached marker:
   - conditional PRIMARY Git hook refuses the intended commit only;
   - independent helper advances COORD before compensation;
   - post-commit hook creates caller-state recovery conflict;
   - expected-old transaction hook obstructs worktree resync only after CAS.
   Every concurrent stimulus MUST use fixture-owned `ready`, `release`, and `done`
   marker files or pipe barriers. Tests MUST embed the expected invocation ID,
   transaction ID, before/after OIDs, and destination ref in the barrier payload;
   assert that each marker was reached and that observed order equals the prescribed
   order. Sleeps, polling retries, timing windows, and retry-to-green are prohibited.
   The PRIMARY failure node additionally snapshots and asserts byte-identical
   unrelated staged, unstaged, and untracked files, their executable modes, the full
   index patch, and the full worktree patch before and after compensation.
8. Add exact type/adapter nodes:
   - `tests/specify_cli/coordination/test_types.py::test_commit_receipt_alias_has_placement_receipt_identity`
   - `tests/specify_cli/coordination/test_commit_router_partition.py::test_composite_adapter_propagates_error_carried_receipt`
   - `tests/specify_cli/git/test_commit_helpers.py::test_composite_deferral_returns_pending_local_commit_evidence`
9. T022 is additive test work only: no delete, rename, skip, `xfail`, assertion
   relaxation, fixture weakening, or frozen-witness edit is permitted. Record
   `git diff --name-status` and an assertion/fixture audit in the RED handoff.
10. Run this exact serial RED command on the preserved production base and record
   every intentional failure:

   ```bash
   PWHEADLESS=1 uv run --extra test pytest -n0 -q \
     tests/architectural/test_review_receipt_producer_gate.py \
     tests/specify_cli/status/test_review_transaction.py \
     tests/status/test_work_package_lifecycle.py::test_review_lifecycle_reuses_held_status_lock_without_implicit_commit \
     tests/specify_cli/coordination/test_types.py::test_commit_receipt_alias_has_placement_receipt_identity \
     tests/specify_cli/coordination/test_commit_router_partition.py::test_composite_adapter_propagates_error_carried_receipt \
     tests/specify_cli/git/test_commit_helpers.py::test_composite_deferral_returns_pending_local_commit_evidence \
     tests/specify_cli/git/test_ref_advance.py
   ```

   No new production file may change until this commit exists and the review handoff
   includes the exact commit SHA and failing assertions.

**Validation**:

- The test-only commit contains no production or frozen-witness diff.
- Every stimulus marker proves the intended real Git boundary was reached.
- Missing COORD receipt, wrong COORD hash, duplicate destination, mismatched attempt
  IDs, and unattributed ref movement all resolve to `compensation_failed`; committed
  accepts only exact receipts, refused has zero delta/receipts, and every non-success
  status has zero outbound attempts.
- Full invocation/transaction ID-pair inheritance, outbound-after-local-commit order,
  direct lock order, held-lock lifecycle reuse without implicit commit, and the Git
  import boundary are executable RED contracts.
- The producer gate and receipt/compensation/outbound contract are RED for the right
  missing behavior, not fixture setup failure.

### Subtask T023: Propagate canonical receipts, post-commit failure, and LocalCommit deferral

**Purpose**: Expose one receipt identity across placement owners while keeping Git
generic and preserving default non-composite behavior.

**Steps**:

1. Define `PlacementCommitReceipt` as the sole class in
   `coordination/types.py`; set `CommitReceipt = PlacementCommitReceipt` as an exact
   compatibility type alias. Do not add a wrapper, subclass, duplicate dataclass, or
   workflow-owned receipt dictionary.
2. Include `invocation_id`, `transaction_id`, destination ref, lock-held
   `before_sha`, commit SHA, worktree root, exact committed diff-tree paths, and event
   IDs. All evidence for one attempt inherits the same ID pair unchanged.
3. Add typed `PlacementCommitFailure` carrying the complete canonical receipt plus
   primary caller-state recovery diagnostics. Compensation consumes only this embedded
   receipt; `rev-parse`/ancestry/porcelain reconstruction is prohibited.
4. Add an additive composite-deferral mode to `safe_commit`. It returns Git-owned
   generic pending `LocalCommit` plus post-commit recovery evidence. Its default mode
   and all non-composite callers remain unchanged.
5. Git modules MUST NOT import `coordination.types`. `BookkeepingTransaction`, status
   transition, and commit-router placement owners adapt generic Git evidence into the
   canonical receipt/failure.
6. Make the receipt-returning status/lifecycle seam consume the already-held status
   lock and transaction; it MUST NOT reacquire either or commit implicitly after return.
7. Extend `coordination/outbound.py`, `BookkeepingTransaction.defer_outbound` /
   `_run_deferred_outbound`, and `sync/local_commit.py` so composite mode stages
   LocalCommit persistence/send together with SaaS, offline queue, and dossier effects.
   Non-success discards all staged effects; default non-composite behavior is unchanged.

**Validation**:

- Alias identity is exact and the producer gate contains only reviewed producers.
- A commit-created recovery failure exposes its complete error-carried receipt.
- Git has no import edge to `coordination.types`.
- Default safe-commit and LocalCommit regressions are byte-compatible.

### Subtask T024: Implement the Mission Management composite and reverse CAS compensation

**Purpose**: Make Mission Management the sole review transaction owner and produce one
truthful typed local result.

**Steps**:

1. Add `status/review_transaction.py`. Workflow mints one `invocation_id` at the
   registered boundary; Mission Management mints one unique `transaction_id` per
   attempt. Internal retry retains invocation ID and rotates transaction ID.
2. Enforce this exact lock order: review workspace/resource lock → sole outer
   `status.locking.feature_status_lock` → Git worktree/index locks.
   `BookkeepingTransaction` is transaction scope entered while that status lock is
   already held; it has no internal lock and MUST NOT acquire/reacquire one. Add no
   composite lock.
3. Hold the status lock through terminal ref/caller-state observation. Expected-old
   CAS runs under that lock but still guards against foreign Git writers.
4. Snapshot every staged/index/worktree/untracked path `safe_commit` may temporarily
   mutate, including unrelated sentinels. Preserve bytes, executable modes, the full
   index patch, and the full worktree patch for unrelated staged, unstaged, and
   untracked state. A non-owned caller-state mismatch is `compensation_failed`.
5. Commit COORD status and PRIMARY tracking through existing owners. Success requires
   the exact canonical receipt set; missing/unattributed movement is indeterminate
   `compensation_failed`, never `refused`.
6. On later failure, compensate every invocation-owned landed placement in reverse
   order, including an error-carried PRIMARY receipt. Extend canonical
   `git/ref_advance.py` with expected-old CAS; resync checked-out worktrees only after
   CAS. Foreign advance, failed restore, or post-CAS resync obstruction is
   `compensation_failed` with repair evidence.
7. Return typed in-process `CompositeWorkflowResult` with `committed`, `refused`,
   `compensated`, or `compensation_failed`. Do not add a public JSON option or persisted
   result artifact.
8. Only local `committed` releases staged outbound. A configured file-backed,
   offline/local capture sink makes the middle channel fail, records retryable
   `dispatch_failed`, and proves a later channel records `dispatch_succeeded`; local
   outcome remains committed. Every non-success outcome has zero attempts.

**Validation**:

- Lock-order and no-reacquisition tests pass.
- All four deterministic real-Git stimulus nodes pass and their markers are asserted.
- The internal-retry adapter test proves one invocation ID and distinct transaction IDs.
- Ref, caller-state, resource, terminal, and outbound contracts match the spec exactly.

### Subtask T025: Run aggregate two-layer proof and architectural gates

**Purpose**: Prove the registered operator contract and direct domain contract without
weakening historical evidence.

**Steps**:

1. Registered-CLI real-Git layer: run the unchanged 12-row witness plus focused
   workspace/workflow tests. Prove operator output, durable refs/bytes/index/worktrees,
   clean refusal, and zero outbound attempts on non-success.
2. Direct Mission Management real-Git layer: run every
   `tests/specify_cli/status/test_review_transaction.py` node and inspect typed result,
   ID inheritance, receipts, `PlacementCommitFailure`, reverse compensation, unrelated
   sentinels, terminal under-lock observations, and per-channel delivery evidence.
3. Run all owned coordination, Git, sync, workflow, and workspace tests. Include real
   adapter regressions for `coordination/outbound.py`, transaction deferred outbound,
   and `sync/local_commit.py`.
4. Run this exact serial focused GREEN command. It covers every WP04-owned test path,
   the frozen witness, and the complete WP02/WP03 regression floor:

   ```bash
   PWHEADLESS=1 uv run --extra test pytest -n0 -q \
     tests/agent/test_workflow_review_lane_gate.py \
     tests/architectural/test_review_receipt_producer_gate.py \
     tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py \
     tests/specify_cli/cli/commands/test_workspace_husk_resolution_1833.py \
     tests/specify_cli/coordination/test_commit_router_partition.py \
     tests/specify_cli/coordination/test_status_transition.py \
     tests/specify_cli/coordination/test_transaction.py \
     tests/specify_cli/coordination/test_types.py \
     tests/specify_cli/coordination/test_outbound.py \
     tests/specify_cli/git/test_commit_helpers.py \
     tests/specify_cli/git/test_ref_advance.py \
     tests/specify_cli/sync/test_local_commit.py \
     tests/specify_cli/status/test_review_transaction.py \
     tests/status/test_work_package_lifecycle.py \
     tests/specify_cli/cli/commands/agent/test_tasks_mark_status.py \
     tests/specify_cli/cli/commands/agent/test_tasks_mark_status_seam.py \
     tests/specify_cli/cli/commands/agent/test_tasks_move_task_authority_staging.py \
     tests/specify_cli/cli/commands/agent/test_tasks_move_task_placement.py \
     tests/specify_cli/cli/commands/agent/test_tasks_move_task_seam.py \
     tests/specify_cli/coordination/test_commit_router_placement.py \
     tests/integration/test_lane_lifecycle_sync.py
   ```

5. Run Ruff across every owned Python path:

   ```bash
   uv run ruff check \
     src/specify_cli/cli/commands/agent/workflow.py \
     src/specify_cli/cli/commands/agent/workflow_executor.py \
     src/specify_cli/coordination/types.py \
     src/specify_cli/coordination/transaction.py \
     src/specify_cli/coordination/status_transition.py \
     src/specify_cli/coordination/outbound.py \
     src/specify_cli/coordination/commit_router.py \
     src/specify_cli/git/commit_helpers.py \
     src/specify_cli/git/ref_advance.py \
     src/specify_cli/status/review_transaction.py \
     src/specify_cli/status/work_package_lifecycle.py \
     src/specify_cli/sync/local_commit.py \
     tests/agent/test_workflow_review_lane_gate.py \
     tests/architectural/test_review_receipt_producer_gate.py \
     tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py \
     tests/specify_cli/cli/commands/test_workspace_husk_resolution_1833.py \
     tests/specify_cli/coordination/test_commit_router_partition.py \
     tests/specify_cli/coordination/test_status_transition.py \
     tests/specify_cli/coordination/test_transaction.py \
     tests/specify_cli/coordination/test_types.py \
     tests/specify_cli/coordination/test_outbound.py \
     tests/specify_cli/git/test_commit_helpers.py \
     tests/specify_cli/git/test_ref_advance.py \
     tests/specify_cli/sync/test_local_commit.py \
     tests/specify_cli/status/test_review_transaction.py \
     tests/status/test_work_package_lifecycle.py
   ```

6. Run strict mypy on every owned production target:

   ```bash
   uv run mypy --strict \
     src/specify_cli/cli/commands/agent/workflow.py \
     src/specify_cli/cli/commands/agent/workflow_executor.py \
     src/specify_cli/coordination/types.py \
     src/specify_cli/coordination/transaction.py \
     src/specify_cli/coordination/status_transition.py \
     src/specify_cli/coordination/outbound.py \
     src/specify_cli/coordination/commit_router.py \
     src/specify_cli/git/commit_helpers.py \
     src/specify_cli/git/ref_advance.py \
     src/specify_cli/status/review_transaction.py \
     src/specify_cli/status/work_package_lifecycle.py \
     src/specify_cli/sync/local_commit.py
   ```

7. Run the new producer gate plus the shared-package and terminology gates, then the
   whitespace/error check, using these exact commands:

   ```bash
   PWHEADLESS=1 uv run --extra test pytest -n0 -q \
     tests/architectural/test_review_receipt_producer_gate.py \
     tests/architectural/test_shared_package_boundary.py \
     tests/architectural/test_no_legacy_terminology.py
   git diff --check
   ```
8. Verify the frozen witness blob and post-`980eae6a9` diff are unchanged; verify the
   WP02 shared-file exception remained limited to the two named files and its approved
   blob/ref still matches.
9. Verify all relevant worktrees are clean and PR #2641 remains DRAFT. Report exact
   RED/GREEN commit SHAs, commands, counts, stimulus markers, receipt producer set,
   caller-state sentinels, and outbound channel evidence to the independent reviewer.

**Validation**:

- Both real-Git layers pass without a public JSON or persisted result artifact.
- Historical approvals, rows 1–8, witness expectations, lane-d, and topology remain
  unchanged.
- All quality, architectural, ownership-exception, and DRAFT-PR gates pass.

## Amendment Definition of Done

- [ ] T022 test-only RED commit predates every amendment production edit.
- [ ] `PlacementCommitReceipt` is the sole class and `CommitReceipt` is its exact alias.
- [ ] Git remains independent of coordination receipt types.
- [ ] Mission Management owns one attempt under the fixed lock order with no new lock.
- [ ] Error-carried receipts drive reverse expected-old CAS compensation.
- [ ] All safe-commit-affected caller state, including unrelated sentinels, is restored
      or the result is `compensation_failed`.
- [ ] LocalCommit/SaaS/offline/dossier effects have zero attempts before local commit
      and on every non-success; best-effort channel failure does not stop later channels.
- [ ] Registered-CLI and direct Mission Management real-Git proof layers pass.
- [ ] Receipt producer gate is non-vacuous, shrink-only, and self-mutating.
- [ ] Frozen witness, historical approvals/activity, shared-file exception, lane-d,
      topology, DRAFT PR, and operator-only merge boundary remain intact.

## Historical Definition of Done — retained as review evidence

The checklist below records T016–T021's original contract. It is not an active
implementation checklist and does not authorize adjacent-ticket or witness changes.

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

## Historical Risks — retained as review evidence

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

## Historical Reviewer Guidance — retained as review evidence

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

## Amendment Reviewer Guidance

Use a reviewer profile distinct from the implementer and reject unless:

1. T022 is a test-only RED commit preceding every amendment production edit, with no
   frozen-witness diff after `980eae6a9`.
2. `PlacementCommitReceipt` is the sole class, `CommitReceipt` is the exact alias, and
   the producer gate rejects workflow/unauthorized constructors.
3. Git exposes generic pending `LocalCommit`/recovery evidence without importing
   coordination types or changing default behavior.
4. The exact lock order is preserved, the lower status seam does not reacquire the
   status lock/transaction, and no composite lock exists.
5. Compensation consumes only canonical or error-carried receipts in reverse order and
   expected-old CAS/resync evidence distinguishes every terminal outcome truthfully.
6. All unrelated caller-state sentinels restore exactly or produce
   `compensation_failed`.
7. LocalCommit/SaaS/offline/dossier adapters have zero attempts before local commit and
   on non-success; the configured middle failure does not stop later success.
8. Registered-CLI and direct Mission Management real-Git layers, deterministic stimulus
   markers, internal-retry IDs, producer gate, Ruff, mypy, and architectural checks all
   pass.
9. The WP02 shared-file exception is limited to its two named files and its frozen
   approved blob/ref; lane-d/topology and all prior approvals/activity remain unchanged.
10. No public JSON result surface, persisted result artifact, topology recomputation,
    or non-DRAFT PR transition was introduced.

## Activity Log

- 2026-07-14T18:54:19Z – codex – shell_pid=138606 – Assigned agent via action command
- 2026-07-14T19:18:48Z – codex – shell_pid=138606 – Ready for independent review: atomic review workspace preparation and partition-aware claim commit; exact rows 9-12 and full acceptance witness green.
- 2026-07-14T19:20:12Z – codex – shell_pid=138606 – Started review via action command
- 2026-07-14T19:27:56Z – user – Moved to planned
- 2026-07-14T19:29:23Z – codex – shell_pid=138606 – Assigned agent via action command
- 2026-07-14T19:42:29Z – codex – shell_pid=138606 – Ready for independent re-review: both placement refs proven from pre-emission hashes; partial outcomes refused; invocation cleanup ownership and failure precedence covered.
- 2026-07-14T19:43:14Z – codex – shell_pid=138606 – Started review via action command
- 2026-07-14T19:45:17Z – user – Moved to planned
- 2026-07-14T19:47:01Z – codex – shell_pid=138606 – Assigned agent via action command
- 2026-07-14T20:00:55Z – user – shell_pid=138606 – Blocked at reviewed ownership boundary: zero-delta split-placement requires upstream composite PRIMARY+COORD transaction receipt and conditional compensation; operator scope decision required.
