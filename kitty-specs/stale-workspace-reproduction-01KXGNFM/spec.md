# Mission Specification: Recover Missing Lane Workspaces

**Mission Branch**: `fix/stale-workspace-reproduction`
**Created**: 2026-07-14
**Status**: Draft
**Input**: GitHub issue #2626 — stale lane-workspace metadata can make WP transitions crash or report success while leaving tracking writes uncommitted.

## Intent Summary

An operator resumes a Mission after its coordination branch has been recreated, while a persisted lane-workspace record still names a lane worktree that no longer exists. The operator must receive one truthful outcome: the canonical workspace authority safely recovers the transition and commits every tracking mutation at its owning placement, or the command refuses before mutation with an actionable recovery diagnostic. A raw filesystem exception, a misleading coordination path, or a successful transition paired with a dirty primary checkout is never acceptable. This Mission is reproduction-first: implementation is permitted only if the defect is RED on the current planning base.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stale workspace state is reproduced honestly (Priority: P1)

A maintainer needs a deterministic witness that models a persisted lane assignment whose recorded worktree directory has disappeared, then invokes the same operator entry points implicated by #2626.

**Why this priority**: The report was observed on another repository and Spec Kitty version. Current-base code truth must be established before changing an authority seam.

**Independent Test**: Build a real temporary Git repository with Mission metadata, lane assignment, coordination topology, and a stale workspace record; invoke the supported transition/review entry points and assert the full consistency boundary.

**Acceptance Scenarios**:

1. **Given** valid lane metadata whose persisted worktree path is absent, **When** the witness runs against the current planning base, **Then** it proves either a live RED defect or an already-correct outcome without mocking away workspace resolution or commit routing.
2. **Given** a transition attempt in that state, **When** observations are collected, **Then** exit/result, event-log state, materialized status, WP tracking content, commit placement, and checkout dirt are all recorded together.

---

### User Story 2 - Transition outcomes are atomic and actionable (Priority: P1)

An operator invokes `mark-status`, `move-task`, or the review action while lane metadata is stale. The command either recovers through the canonical authority and completes cleanly, or refuses before any durable transition/write with a diagnostic naming the missing workspace and a supported recovery action.

**Why this priority**: A green-looking command paired with an uncommitted tracking file creates silent state divergence and data-loss risk.

**Independent Test**: Exercise each affected entry-point family against the RED fixture and prove no outcome can combine success with an uncommitted WP mutation or partial state transition.

**Acceptance Scenarios**:

1. **Given** a recoverable missing lane worktree, **When** the command chooses recovery, **Then** all authoritative state and tracking writes are committed at their canonical placement and every relevant checkout is clean.
2. **Given** a missing lane worktree that cannot be recovered safely, **When** the command runs, **Then** it exits non-zero before mutation and identifies the stale record, missing path, and supported recovery command.
3. **Given** either outcome, **When** human and JSON output are inspected, **Then** neither reports an overall success while an auto-commit failed.

---

### User Story 3 - Healthy workspace flows remain unchanged (Priority: P2)

Operators whose lane and coordination worktrees exist continue to receive the current transition, commit-placement, and structured-output behavior.

**Why this priority**: A stale-state guard must not create a second workspace resolver or perturb healthy lane topology.

**Independent Test**: Run the existing healthy lane/coord transition suites alongside the stale-state witness and prove byte-compatible public outcomes where no workspace is missing.

**Acceptance Scenarios**:

1. **Given** a healthy lane worktree and record, **When** the same commands run, **Then** transition and commit behavior remains unchanged.
2. **Given** JSON mode, **When** a stale-state refusal occurs, **Then** stdout remains one parseable document and diagnostics do not leak as unrelated stdout text.

### Edge Cases

- The lane branch exists but its worktree is absent and recoverable.
- Both the lane branch and worktree are absent while the stale record remains.
- The coordination worktree exists but the lane worktree does not.
- The recorded path is relative, absolute, malformed, or points outside the repository authority boundary.
- A transition has dependencies or review guards that would independently refuse it; stale-workspace handling must not bypass those guards.
- Recovery or refusal is interrupted; no subprocess, lock, partial event, or dirty tracking mutation remains.

## Requirements *(mandatory)*

### Functional Requirements

| ID | Title | User Story | Priority | Status |
|----|-------|------------|----------|--------|
| FR-001 | Current-base reproduction | The Mission MUST provide a non-fakeable current-base witness for #2626 using supported operator entry points and realistic Git/workspace state. | High | Open |
| FR-002 | Full consistency observation | The witness MUST jointly observe command result, status event log, materialized lane state, WP tracking content, commit placement, and dirt across primary, coordination, and lane checkouts. | High | Open |
| FR-003 | Reproduction-first disposition | Production code MUST change only if FR-001 is RED on the planning base; an already-correct result MUST be documented and closed without speculative implementation. | High | Open |
| FR-004 | Atomic success | A successful stale-workspace transition MUST leave all intended authoritative and tracking writes committed at canonical placement with relevant checkouts clean. | High | Open |
| FR-005 | Fail before mutation | When safe recovery is unavailable, the command MUST fail before durable mutation and MUST NOT report the transition as successful. | High | Open |
| FR-006 | Actionable diagnostics | Refusal MUST identify the stale workspace record or lane, the missing path, and a supported recovery action without exposing a raw `FileNotFoundError` or misleading path. | High | Open |
| FR-007 | Entry-point coverage | The disposition MUST cover `mark-status`, `move-task`, and the review action at their shared canonical authority seam, with entry-point-specific regression coverage where behavior differs. | High | Open |
| FR-008 | Structured-output truth | JSON mode MUST remain one parseable stdout document whose status agrees with the durable outcome; human mode MUST make commit failure or refusal unmistakable. | Medium | Open |

### Non-Functional Requirements

| ID | Title | Requirement | Category | Priority | Status |
|----|-------|-------------|----------|----------|--------|
| NFR-001 | Determinism | The focused stale-workspace witness MUST pass reliably across repeated local runs and avoid timing-only assertions. | Reliability | High | Open |
| NFR-002 | Cross-platform semantics | Path validation and diagnostics MUST remain correct on Linux, macOS, and Windows-shaped paths; platform-specific recovery behavior MUST have focused coverage. | Portability | High | Open |
| NFR-003 | Quality gates | Changed code MUST pass focused pytest coverage, Ruff, and strict mypy with zero new warnings or blanket suppressions. | Maintainability | High | Open |
| NFR-004 | Diagnostic latency | A non-recoverable missing-workspace state MUST be detected before launching transition side effects and complete within 2 seconds in a local fixture. | Performance | Medium | Open |

### Constraints

| ID | Title | Constraint | Category | Priority | Status |
|----|-------|------------|----------|----------|--------|
| C-001 | Canonical workspace authority | Consume the existing workspace resolver/allocation/recovery authority; do not reconstruct lane paths or create a parallel stale-record resolver at command call sites. | Architecture | High | Open |
| C-002 | Status event authority | `status.events.jsonl` remains the sole authority for lane state; WP frontmatter/activity text is tracking evidence, not an alternative transition authority. | Architecture | High | Open |
| C-003 | Placement authority | Tracking and status artifacts MUST be committed through their canonical placement/commit-router seams; never fall back to an arbitrary checkout merely because it exists. | Architecture | High | Open |
| C-004 | No silent workaround | Do not delete stale metadata, hand-commit primary-checkout files, or auto-create directories outside the supported workspace lifecycle as an implementation shortcut. | Safety | High | Open |
| C-005 | Issue boundary | #2160 and #2367 are adjacent authority/race mechanisms; this Mission changes them only if the #2626 reproduction proves the same owning seam and the plan records the fold explicitly. | Scope | Medium | Open |
| C-006 | Draft PR workflow | All changes reach `origin/main` only through a DRAFT PR; the human operator alone may mark ready or merge. | Governance | High | Open |

### Key Entities

- **Workspace record**: Persisted `.kittify/workspaces/<mission>-<lane>.json` context describing a lane assignment and expected worktree.
- **Resolved workspace**: Canonical runtime result for a WP, including execution mode, lane, branch, path, and existence state.
- **Coordination placement**: Owning location/ref for Mission planning and tracking artifacts in coordinated topology.
- **Transition transaction**: The coupled decision, event append, materialization, tracking write, commit, and structured result that must present one truthful outcome.
- **Recovery action**: Existing supported workspace lifecycle operation that can recreate or reconcile a missing lane worktree without fabricating authority.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The planning-base witness produces a recorded RED or already-fixed verdict across all six consistency surfaces in FR-002.
- **SC-002**: After disposition, zero tested entry points can return success while leaving an intended tracking mutation uncommitted.
- **SC-003**: Non-recoverable stale workspace state yields a non-zero, actionable result before any event-log or WP-file mutation in 100% of focused cases.
- **SC-004**: Healthy lane and coordination regression suites remain green with no public output-contract drift.
- **SC-005**: Focused tests, Ruff, strict mypy, and required architectural/terminology guards pass before review.

## Assumptions

- Assignment plus the single claim comment on #2626 is the complete issue-thread interaction; all later evidence belongs in the DRAFT PR.
- The preferred outcome is not predetermined: safe recovery and fail-closed refusal are both acceptable when grounded in the canonical authority and an honest durable result.
- The report's original Spec Kitty 3.2.5 environment is context, not proof that the defect survives current `origin/main`.
- This request is not a bulk edit; any cross-file changes are semantic wiring/tests around one stale-workspace behavior, not a repeated identifier migration.
