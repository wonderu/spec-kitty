# Implementation Plan: Recover Missing Lane Workspaces

**Branch**: `fix/stale-workspace-reproduction` | **Date**: 2026-07-14 | **Spec**: [spec.md](spec.md)
**Input**: GitHub issue #2626 and the reviewed Mission specification

## Summary

Preserve the approved production-shaped witness and its frozen rows 1–8, then finish the four RED `agent action review` rows through one Mission Management-owned composite operation. The workflow boundary resolves readiness once and mints one invocation ID; Mission Management holds the canonical mutation lock, mints one transaction ID per attempt, commits COORD status and PRIMARY tracking through their existing owners, and returns one typed in-process result. Exact canonical receipts—not observed ref movement—authorize success and reverse compensation. A typed post-commit failure carries its receipt; expected-old CAS restoration lives in the canonical ref-advance authority; every safe-commit-affected caller-state path is preserved. Local commit precedes independent best-effort outbound delivery. The registered CLI and direct Mission Management real-Git layers jointly prove the contract.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Typer CLI, Git CLI/subprocess boundary, `mission_runtime` placement seam, Mission Management status aggregate/lifecycle service, `BookkeepingTransaction`, partition-aware commit router, `safe_commit`, canonical ref-advance authority
**Storage**: Repository files (`meta.json`, `lanes.json`, persisted workspace JSON, status JSONL/materialization, Markdown tracking) and Git refs/worktrees
**Testing**: Frozen registered-CLI witness `tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py`; direct Mission Management real-Git integration for typed results; focused transaction/router/ref-advance/safe-commit tests; receipt-producer architectural gate
**Target Platform**: Linux, macOS, and Windows 10+ through existing platform-neutral Git/path abstractions
**Project Type**: Python CLI monorepo
**Performance Goals**: Non-recoverable stale workspace refused before side effects within 2 seconds in the focused fixture
**Constraints**: ATDD RED first; no patches over resolver/commit/status seams; no arbitrary primary fallback; no direct `origin/main` push; PR remains DRAFT
**Scale/Scope**: One issue and one review-only composite path. `mark-status` and `move-task` rows 1–8 stay frozen; WP04 expands in place with no WP/lane/topology recomputation.

## Charter Check

- **Canonical authority**: PASS if workspace resolves once and PRIMARY tracking remains separate from COORD status. No command-local path reconstruction.
- **Domain ownership**: PASS only when Mission Management owns the composite operation and canonical lock; workflow is a request/result adapter.
- **ATDD first**: PASS only after a test-only RED commit reproduces a current-base defect. Already-green arms receive characterization evidence, not speculative production changes.
- **Tiered rigor**: Critical workflow mutation requires real-Git CLI proof, focused seam tests, independent review, and architectural gates.
- **Tracker hygiene**: #2626 is assigned and claimed; `issue-matrix.md` marks it as the sole addressed issue. No adjacent ticket is activated by this amendment.
- **Git/PR discipline**: Planning stays on `fix/stale-workspace-reproduction`; implementation uses resolved lane workspaces; PR #2641 remains DRAFT and the operator merges.
- **Campsite/terminology**: New branches receive tests; no suppressions, legacy Mission terminology, or unrelated cleanup.

## Project Structure

### Documentation

```text
kitty-specs/stale-workspace-reproduction-recovery-01KXGR6S/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── issue-matrix.md
├── disposition-matrix.md
├── contracts/stale-workspace-transition-contract.md
└── tasks.md

docs/adr/3.x/
└── 2026-07-14-2-cross-partition-workflow-transaction.md
```

### Source and tests

```text
src/specify_cli/
├── cli/commands/agent/
│   ├── tasks_mark_status.py
│   ├── tasks_move_task.py
│   ├── workflow.py
│   └── workflow_executor.py
├── coordination/
│   ├── types.py
│   ├── transaction.py
│   ├── status_transition.py
│   ├── outbound.py
│   └── commit_router.py
├── git/
│   ├── commit_helpers.py
│   └── ref_advance.py
├── status/
│   ├── review_transaction.py
│   └── work_package_lifecycle.py
├── sync/local_commit.py
├── workspace/context.py
└── lanes/lifecycle_sync.py

tests/
├── agent/test_workflow_review_lane_gate.py
├── architectural/test_review_receipt_producer_gate.py
├── specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py
├── specify_cli/cli/commands/test_workspace_husk_resolution_1833.py
├── specify_cli/coordination/
│   ├── test_commit_router_partition.py
│   ├── test_status_transition.py
│   ├── test_transaction.py
│   ├── test_outbound.py
│   └── test_types.py
├── specify_cli/git/
│   ├── test_commit_helpers.py
│   └── test_ref_advance.py
├── specify_cli/sync/test_local_commit.py
└── specify_cli/status/test_review_transaction.py
```

**Structure Decision**: Add `status/review_transaction.py` as the Mission Management composite domain service, consistent with the accepted execution-state domain ADR. Keep placement, COORD transaction, PRIMARY routing, safe commit, and ref resynchronization in their existing authorities. `coordination/types.py` owns the one canonical class `PlacementCommitReceipt`; the existing public/internal name `CommitReceipt` becomes a compatibility type alias to that exact class identity, not a subclass, wrapper, second dataclass, or second constructor authority. Workflow remains a thin registered-command adapter. WP04 expands in its existing lane-d; do not add WP05, edit `lanes.json`, or run mutating task finalization.

## Complexity Tracking

No charter violations are planned.

## Implementation Concern Map

IC-01 through IC-06 are immutable reviewed historical state. WP01–WP03 approvals,
the disposition rows, test-only witness commit `980eae6a9`, remediation commit
`eaff3130c`, and both WP04 review artifacts are inputs, not work to reactivate. The
amendment begins at IC-07. No instruction below authorizes edits to rows 1–8, WP02,
WP03, or any adjacent-ticket mechanism.

### IC-01 — Real persisted-context witness

- **Historical outcome (immutable)**: Approved production-shaped witness and reviewed disposition; do not rerun as a planning decision or edit frozen rows.
- **Preserved evidence**: Approved witness commit/blob, registered argv, six-surface observations, and reviewer reference.

### IC-02 — Disposition gate and ownership matrix

- **Historical outcome (immutable)**: The committed authoritative matrix assigns rows 9–12 to WP04 and freezes rows 1–8; do not amend its ownership decisions.
- **Preserved evidence**: Committed disposition matrix and case-by-case frozen-witness Charter exception.

### IC-03 — Task-command and placement remediation

- **Historical outcome (immutable)**: WP02 is independently approved; task-command behavior and its tests are not amendment owners.
- **Preserved evidence**: Test-only RED, production GREEN, exact approved witness blob, and independent review.

### IC-04 — Review readiness before claim

- **Historical outcome (immutable)**: Readiness-before-claim and invocation-owned workspace cleanup from the preserved WP04 implementation remain the starting base.
- **Preserved evidence**: `980eae6a9`, `eaff3130c`, cleanup/ownership tests, and review cycles 1–2.

### IC-05 — Lifecycle missing-authority diagnostics

- **Historical outcome (immutable)**: WP03 is an approved no-op; its lifecycle owners remain unchanged.
- **Preserved evidence**: Byte-identical owner hashes and approved lifecycle verification.

### IC-06 — Cross-surface regression evidence

- **Historical outcome (immutable baseline)**: Approved regression evidence defines the floor; amendment validation may rerun it but may not reinterpret or weaken it.
- **Preserved evidence**: Full witness, focused suites, Ruff, strict mypy, and architectural/terminology gates recorded by prior reviews.

### IC-07 — Mission Management review composite

- **Purpose**: Own `agent action review` COORD status plus PRIMARY tracking as one locked domain attempt and return `CompositeWorkflowResult`.
- **Relevant requirements**: FR-004, FR-010, FR-014, FR-016, C-009, C-011
- **Affected surfaces**: new `src/specify_cli/status/review_transaction.py`, `status/work_package_lifecycle.py`, `coordination/status_transition.py`, workflow caller adapters
- **Sequencing/depends-on**: IC-04 readiness; precedes all durable review mutation
- **Design**: Workflow mints `invocation_id` once. Mission Management mints unique `transaction_id` per attempt, holds the existing Mission mutation lock through terminal ref/state observation, stages outbound effects, and invokes existing placement owners. No public JSON flag or persisted result artifact.
- **Lock order**: acquire the review workspace/resource lock first; then the sole `status.locking.feature_status_lock`; then Git worktree/index locks. `BookkeepingTransaction` is the transaction scope under the already-held feature lock, not a distinct lock. The receipt-returning lower status seam consumes that open scope and MUST NOT reacquire the feature lock. Expected-old ref CAS runs while the feature lock is held; CAS still protects against foreign Git writers outside that lock. No new composite lock is introduced.
- **Risks**: Violating this order can deadlock or double-commit. Tests assert acquisition order and that the lower status seam does not reacquire the feature lock.

### IC-08 — Canonical receipt and post-commit failure propagation

- **Purpose**: Make one owner-produced `PlacementCommitReceipt` the only success/compensation authority and preserve it when a commit exists but caller-state recovery fails.
- **Relevant requirements**: FR-011, FR-015, C-013, C-014
- **Affected surfaces**: `coordination/types.py`, `transaction.py`, `status_transition.py`, `commit_router.py`, `git/commit_helpers.py`, receipt-producer architectural gate
- **Sequencing/depends-on**: IC-07 transaction/attempt identity
- **Design**: `PlacementCommitReceipt` is the sole class. `CommitReceipt = PlacementCommitReceipt` preserves exact class identity for compatibility. Receipt contains invocation/transaction IDs, destination ref, lock-held `before_sha`, commit SHA, worktree, committed diff-tree paths, and event IDs. `PlacementCommitFailure` carries the complete receipt plus recovery diagnostics. The initial shrink-only producer-gate baseline includes reviewed legacy/current constructors and the new Git-to-coordination adapter sites; no workflow producer is permitted.
- **Git evidence seam**: `safe_commit` gains an additive composite-deferral mode returning Git-owned generic pending `LocalCommit` plus post-commit caller-recovery evidence. Default non-composite behavior remains byte-compatible. Git modules do not import `coordination.types`; placement owners adapt Git evidence into the canonical coordination receipt/failure.
- **Risks**: `safe_commit` temporarily touches unrelated caller index/worktree state. Snapshot and verify every affected staged, unstaged, and untracked path, including unrelated sentinels.

### IC-09 — Reverse expected-old compensation

- **Purpose**: Restore every invocation-owned landed placement in reverse order after later failure without erasing foreign history.
- **Relevant requirements**: FR-012, C-010, C-014
- **Affected surfaces**: `git/ref_advance.py`, `coordination/transaction.py`, Mission Management composite service, focused real-Git tests
- **Sequencing/depends-on**: IC-08 receipts/failures
- **Design**: Extend the canonical ref-advance module with expected-old CAS restore. CAS uses receipt `commit_sha` as expected old and `before_sha` as replacement; checked-out worktrees resynchronize only after CAS. A mismatch, incomplete caller-state restore, or post-CAS resync failure yields `compensation_failed` with repair evidence.
- **Risks**: Ref restoration can succeed before resync fails. Preserve both facts and never relabel the result compensated.

### IC-10 — Post-commit outbound and two-layer proof

- **Purpose**: Separate local atomicity from best-effort delivery and prove both public and typed contracts.
- **Relevant requirements**: FR-013, C-012, C-015, SC-008, SC-011
- **Affected surfaces**: `coordination/outbound.py`, `BookkeepingTransaction.defer_outbound` and `_run_deferred_outbound`, `sync/local_commit.py`, configured capture-sink adapters, frozen CLI witness, direct real-Git integration, architectural gate
- **Sequencing/depends-on**: IC-07 through IC-09
- **Design**: Composite staging includes LocalCommit persistence/send alongside SaaS, offline queue, and dossier effects. Zero persistence/send attempts occur before local `committed`; all staged effects are discarded for non-success. After commit, each real adapter records `dispatch_succeeded` or retryable `dispatch_failed`, and later channels continue. A configured file-backed/offline/local capture sink injects a failing middle channel and proves a later channel succeeds. Registered CLI proves output/durable state; direct Mission Management integration proves typed results, IDs, receipts, failures, compensation, sentinels, and channel evidence.
- **Risks**: Treating delivery failure as transaction failure would attempt unsafe rollback after externally visible delivery. Keep local outcome committed and surface retryable per-channel diagnostics.

## Execution Strategy

1. Start from preserved `980eae6a9`, `eaff3130c`, and the two WP04 review artifacts. IC-01–IC-06 and rows 1–8 remain immutable historical evidence.
2. Land a fresh test-only RED commit before production. It includes the receipt-producer gate with a non-zero legacy/current/new-adapter floor, shrink-only expected producer set, and self-mutation test; deterministic real-Git receipt/compensation/outbound tests; and the invocation-retry adapter test.
3. Use exact fault stimuli and assert each stimulus was reached: a conditional PRIMARY Git hook for commit refusal; an independent helper that advances COORD before compensation; a post-commit hook that creates caller-state recovery conflict; and an expected-old transaction hook that obstructs checked-out-worktree resync after CAS. A test fails if its stimulus marker was not observed.
4. Implement IC-07 through IC-09 in order. Enforce the fixed lock order; add the Git-owned deferred `LocalCommit` evidence mode without changing default safe-commit behavior; adapt evidence only at placement owners; never import coordination types into Git or derive a receipt from ref movement.
5. Implement IC-10 across real outbound and LocalCommit adapters. Configure the file-backed/offline/local capture sink so the middle channel fails and a later channel succeeds; prove no persistence/send attempt on any non-success local outcome.
6. Run an adapter test proving workflow mints `invocation_id` once across an internal retry while Mission Management mints distinct transaction IDs and each attempt's receipts/result inherit the correct pair unchanged.
7. Run the registered-CLI and direct Mission Management real-Git layers, receipt-producer architectural gate, preserved IC-06 regression floor, independent WP review, and Mission closeout while PR #2641 stays DRAFT. WP04 remains the only active package; no task/topology refinalization occurs.

## Acceptance Witness Matrix

**Test module**: `tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py`

| Entry point | Exact argv | Required starting state |
|---|---|---|
| `mark-status` | `agent tasks mark-status T001 --status done --mission <slug> --json` | `tasks.md` contains pending T001; stale lane context exists but must remain irrelevant |
| `move-task` | `agent tasks move-task WP01 --to for_review --mission <slug> --agent codex --json` | WP01 is `in_progress`, subtasks complete, implementation commit present, dependencies satisfied |
| `agent action review` | `agent action review WP01 --agent codex --mission <slug>` | WP01 is `for_review`, implementation commit present, coordination topology/status materialized |

Each argv runs against healthy, matching-branch/missing-worktree, branch-absent, and divergent-context rows as applicable. Rows 1–8 and the reviewed fixture/observation harness remain byte-frozen. Review rows retain the test-only `980eae6a9` desired contract and gain real-Git fault stimuli through repository-local hooks or an independent fixture helper, never production monkeypatching. Before/after ref OIDs, exact bytes, staged/unstaged patches, untracked path/byte/mode sets, locks, worktrees, porcelain, commit diff-tree paths, and outbound attempt counts are observed under the Mission lock where applicable.

The direct Mission Management integration uses the same real repositories and worktrees to inspect `CompositeWorkflowResult`, invocation/transaction inheritance, canonical receipts, `PlacementCommitFailure`, compensation results, and per-channel delivery evidence. It does not introduce a public JSON surface.

The `move-task --skip-pre-review-gate` escape hatch may be retained only as a separately labelled negative-control row. It cannot satisfy the ordinary `move-task` acceptance row because it returns before workspace resolution.

## Readiness and Compensation Protocol

1. **Classify without mutation**: reconcile persisted context with the current lane assignment and branch inventory into ready/recoverable/unavailable/divergent.
2. **Acquire invocation-owned resources**: only a recoverable row may create/attach the worktree and acquire a review lock; record whether each resource was created by this invocation.
3. **Open one domain attempt**: workflow passes the resolved identity and one invocation ID to Mission Management; the service mints one transaction ID, acquires the canonical Mission mutation lock, snapshots all safe-commit-affected caller state, and stages outbound effects.
4. **Commit with canonical receipts**: COORD status and PRIMARY WP tracking remain physically partitioned and commit through existing owners. Each owner returns the same canonical receipt type; post-commit caller recovery failure raises `PlacementCommitFailure` carrying that receipt.
5. **Compensate in reverse**: on later failure, consume only owner-produced or error-carried receipts, newest first. Expected-old CAS restoration happens in `ref_advance`; resync follows successful CAS. Restore exact caller state and invocation-owned workspace/lock resources.
6. **Observe terminal local state under lock**: exact receipt set yields `committed`; zero delta yields `refused`; exact restoration yields `compensated`; any unattributed movement, CAS/resync failure, or caller-state mismatch yields `compensation_failed`.
7. **Deliver after commit**: only local `committed` unlocks best-effort per-channel outbound. Delivery failure remains diagnostic/retryable and does not alter the local result.

## Rejected Alternatives

- **Fallback commit in the primary checkout**: placement, not directory availability, owns artifacts.
- **One global stale-workspace wrapper**: commands have distinct owners and workspace requirements.
- **Rollback-first design**: readiness can be established before mutation; compensation is a last resort.
- **Observed-ref receipts**: movement proves neither producer nor compensation ownership; rejected in favor of owner-produced typed receipts and typed post-commit failure.
- **Workflow-owned transaction/dictionaries**: violates Mission Management ownership and duplicates policy; workflow remains a caller.
- **Outbound inside local atomicity**: a later delivery failure cannot safely retract earlier external delivery; rejected in favor of post-commit per-channel evidence.
- **Add WP05/refinalize topology**: would recompute live lanes and risk #2644; fold the operator-authorized owner expansion into WP04 in place.
- **Delete/rewrite stale context automatically**: disagreement is an authority conflict, not implicit permission.
- **Activate adjacent-ticket work**: rejected; the amendment is limited to the reviewed `agent action review` composite gap.

## Post-Design Charter Re-check

PASS: the design preserves canonical authorities, uses RED-first evidence, keeps one-issue scope, assigns new branches focused tests, and retains the DRAFT/operator-only landing boundary.

## Risks and Rollback

- **Nested-lock/deadlock risk**: Mission Management is the sole outer lock holder; receipt-returning lower seams accept the active transaction instead of reacquiring the same lock.
- **Lock-order invariant**: workspace/resource → feature-status → Git worktree/index. `BookkeepingTransaction` operates inside the already-held feature-status scope; there is no separate transaction or composite lock. Expected-old CAS remains under the feature lock.
- **Type-identity drift risk**: `CommitReceipt` is an alias to `PlacementCommitReceipt`, and the architectural gate covers all baseline/new producer sites before production changes.
- **Caller-state loss risk**: preflight captures full relevant-worktree staged, unstaged, and untracked state, including unrelated sentinels. Any mismatch blocks `compensated`.
- **Foreign-ref risk**: expected-old CAS preserves foreign history. CAS refusal is `compensation_failed`, never a forced reset.
- **Post-CAS resync risk**: record restored ref plus failed checkout path and supported repair; do not conceal the split outcome.
- **Outbound duplication risk**: no attempts before local commit; per-channel retry evidence is explicit and delivery failures do not trigger Git rollback.
- **LocalCommit leakage risk**: composite mode defers both sync-state persistence and send; default safe-commit and non-composite LocalCommit behavior remain unchanged.
- **Implementation rollback**: before Mission landing, revert WP04 code commits as a unit while retaining the immutable witness and planning evidence. Runtime compensation never uses broad `git reset --hard`, deletes persisted workspace authority, or rewrites a ref without receipt-bound expected-old CAS.
