# Implementation Plan: Recover Missing Lane Workspaces

**Branch**: `fix/stale-workspace-reproduction` | **Date**: 2026-07-14 | **Spec**: [spec.md](spec.md)
**Input**: GitHub issue #2626 and the reviewed Mission specification

## Summary

Build one real-Git, real-CLI persisted-workspace fixture that classifies #2626 per entry point and snapshots the complete consistency boundary. Treat the historical recoverable branch-present case honestly if already green. If a current-base RED exists, fix only its proven owner: establish one resolved workspace and readiness before durable review mutation, preserve PRIMARY-versus-COORD placement, and make failure output agree with durable state. Stop without production changes if all exact arms are green.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Typer CLI, Git CLI/subprocess boundary, `mission_runtime` placement seam, Spec Kitty status/workspace/lane modules
**Storage**: Repository files (`meta.json`, `lanes.json`, persisted workspace JSON, status JSONL/materialization, Markdown tracking) and Git refs/worktrees
**Testing**: Pytest module `tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py` with real temporary Git repositories, genuine Git worktrees, and registered Typer command entry points; focused unit/integration characterization plus architectural guards
**Target Platform**: Linux, macOS, and Windows 10+ through existing platform-neutral Git/path abstractions
**Project Type**: Python CLI monorepo
**Performance Goals**: Non-recoverable stale workspace refused before side effects within 2 seconds in the focused fixture
**Constraints**: ATDD RED first; no patches over resolver/commit/status seams; no arbitrary primary fallback; no direct `origin/main` push; PR remains DRAFT
**Scale/Scope**: One issue, three entry-point families, one persisted-context fixture, and only code owners proven RED by that fixture

## Charter Check

- **Canonical authority**: PASS if workspace resolves once and PRIMARY tracking remains separate from COORD status. No command-local path reconstruction.
- **ATDD first**: PASS only after a test-only RED commit reproduces a current-base defect. Already-green arms receive characterization evidence, not speculative production changes.
- **Tiered rigor**: Critical workflow mutation requires real-Git CLI proof, focused seam tests, independent review, and architectural gates.
- **Tracker hygiene**: #2626 is assigned and claimed; `issue-matrix.md` marks it as the sole addressed issue. #2160/#2367 remain references only.
- **Git/PR discipline**: Planning stays on `fix/stale-workspace-reproduction`; implementation uses resolved lane workspaces; PR #2641 remains DRAFT and the operator merges.
- **Campsite/terminology**: New branches receive tests; no suppressions, legacy Mission terminology, or unrelated cleanup.

## Project Structure

### Documentation

```text
kitty-specs/stale-workspace-reproduction-01KXGNFM/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── issue-matrix.md
├── contracts/stale-workspace-transition-contract.md
└── tasks.md
```

### Source and tests

```text
src/specify_cli/
├── cli/commands/agent/
│   ├── tasks_mark_status.py
│   ├── tasks_move_task.py
│   ├── workflow.py
│   └── workflow_executor.py
├── workspace/context.py
└── lanes/lifecycle_sync.py

tests/
├── specify_cli/cli/commands/agent/
├── integration/
└── architectural/
```

**Structure Decision**: Keep behavior in existing command/workspace/lifecycle owners. Add a shared test-fixture helper only if it removes fixture duplication without becoming production authority. Do not add a service or resolver layer unless the RED call-path matrix proves an owner missing from current architecture.

## Complexity Tracking

No charter violations are planned.

## Implementation Concern Map

### IC-01 — Real persisted-context witness

- **Purpose**: Reproduce and classify every reported entry point without any production monkeypatching; only canonical fixture serialization, environment isolation, and cache clearing are allowed.
- **Relevant requirements**: FR-001, FR-002, FR-003, FR-007, NFR-001
- **Affected surfaces**: `tests/specify_cli/cli/commands/agent/`, existing Git/CLI test helpers
- **Sequencing/depends-on**: none
- **Risks**: A helper-level or mocked test can false-green; branch HEAD and committed path sets must be asserted, not just porcelain.

### IC-02 — Disposition gate and ownership matrix

- **Purpose**: Emit an authoritative disposition matrix and separate already-green negative controls/recoverable arms from current REDs before binding each RED to its existing owner.
- **Relevant requirements**: FR-003, FR-007, FR-009, C-005, C-007
- **Affected surfaces**: `research.md`, the transition contract, witness results
- **Sequencing/depends-on**: IC-01
- **Risks**: Treating all commands uniformly would manufacture a cross-command resolver and broaden #2626. Every row records baseline SHA, exact argv, state classification, RED/GREEN, six-surface delta, existing owner, and `stop`/`continue`.

### IC-03 — Review readiness before claim

- **Purpose**: If review ordering is RED, consume one reconciled workspace classification and establish/materialize readiness before `for_review → in_review` mutation.
- **Relevant requirements**: FR-004, FR-005, FR-006, FR-009, C-001, C-002, C-003, C-008
- **Affected surfaces**: `src/specify_cli/cli/commands/agent/workflow.py`, `workflow_executor.py`, `workspace/context.py`, and only proven lifecycle consumers
- **Sequencing/depends-on**: IC-02 and IC-04 when the lifecycle row is RED; otherwise IC-02. Conditional on a review RED.
- **Risks**: Readiness has two phases: non-mutating classify/validate, then invocation-owned recovery and lock. Any later failure releases the lock and removes only a worktree proven created by this invocation. The live review bookkeeping path currently sends the mixed WP/status bundle through one coordination transaction; the witness must classify that placement rather than assuming it already splits.

### IC-04 — Lifecycle missing-authority diagnostics

- **Purpose**: If branch-plus-worktree absence or divergence is RED, make the canonical workspace seam reconcile persisted context with current lane assignment and return ready/recoverable/unavailable/divergent before any cwd-bound probe.
- **Relevant requirements**: FR-005, FR-006, FR-008, FR-009, NFR-004, C-008
- **Affected surfaces**: `src/specify_cli/lanes/lifecycle_sync.py` and focused integration tests
- **Sequencing/depends-on**: IC-02; conditional on a lifecycle/reconciliation RED; precedes IC-03 when both activate
- **Risks**: Thread the same resolved identity into lifecycle sync instead of recomposition; no directory fabrication or arbitrary branch creation.

### IC-05 — Cross-surface regression evidence

- **Purpose**: Prove healthy behavior, structured output, clean checkouts, correct commit placement, and exact refusal deltas after conditional fixes.
- **Relevant requirements**: FR-002, FR-004, FR-005, FR-008, NFR-002, NFR-003
- **Affected surfaces**: focused CLI/integration suites, Ruff, mypy, architectural gates
- **Sequencing/depends-on**: IC-02 and any implemented IC-03/IC-04
- **Risks**: Passing focused tests without marker/authority guards can miss CI routing or split-placement regressions.

## Execution Strategy

1. Land IC-01 as a test-only commit. Parameterize healthy, matching-branch recoverable, branch-absent, and persisted-context-divergent states for each entry point using exact registered CLI argv and healthy positive-control twins.
2. Produce the disposition matrix with baseline SHA, exact command, classification, RED/GREEN, six-surface delta, reached owner, and `stop`/`continue` for every row.
3. If every row is green, stop production implementation. Mixed verdicts activate production work only for rows marked RED/continue.
4. If a placement row is RED, record it explicitly as a #2160-adjacent residual in `issue-matrix.md` and the DRAFT PR before editing production code. The conditional fix must route through the existing canonical partition-aware commit seam rather than hand-rolling dual commits; it does not close or claim #2160.
5. If lifecycle/reconciliation is RED, implement IC-04 first. If review ordering is RED, implement IC-03 after IC-04 when activated, otherwise directly after IC-02.
6. Run IC-05 after every activated remediation concern, then independent WP review and Mission closeout while PR #2641 stays DRAFT.

## Acceptance Witness Matrix

**Test module**: `tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py`

| Entry point | Exact argv | Required starting state |
|---|---|---|
| `mark-status` | `agent tasks mark-status T001 --status done --mission <slug> --json` | `tasks.md` contains pending T001; stale lane context exists but must remain irrelevant |
| `move-task` | `agent tasks move-task WP01 --to for_review --mission <slug> --agent codex --skip-pre-review-gate --json` | WP01 is `in_progress`, subtasks complete, implementation commit present, dependencies satisfied |
| `agent action review` | `agent action review WP01 --agent codex --mission <slug>` | WP01 is `for_review`, implementation commit present, coordination topology/status materialized |

Each argv runs against healthy, matching-branch/missing-worktree, branch-absent, and divergent-context rows as applicable. Before/after ref OIDs are recorded for PRIMARY, COORD, and lane refs; every commit in each OID range and its path set is enumerated. Refusal requires an empty OID range, not merely byte-equivalent files. The acceptance module may not monkeypatch any production symbol, subprocess, root/placement resolution, lifecycle, commit, or status path.

## Readiness and Compensation Protocol

1. **Classify without mutation**: reconcile persisted context with the current lane assignment and branch inventory into ready/recoverable/unavailable/divergent.
2. **Acquire invocation-owned resources**: only a recoverable row may create/attach the worktree and acquire a review lock; record whether each resource was created by this invocation.
3. **Claim/commit through observed authority**: the witness records where the current mixed WORK_PACKAGE_TASK/STATUS_STATE bundle lands. If canonical PRIMARY/COORD placement is RED, the activated remediation adapts the review path to the existing partition-aware commit seam; it does not pretend the current coordination transaction already splits the bundle.
4. **Compensate post-readiness failure**: release invocation-owned locks and remove only an invocation-created worktree when a later claim/commit fails; never remove pre-existing resources.
5. **Proceed**: pass the same reconciled workspace identity into lifecycle/review consumers; do not resolve or compose it again.

## Rejected Alternatives

- **Fallback commit in the primary checkout**: placement, not directory availability, owns artifacts.
- **One global stale-workspace wrapper**: commands have distinct owners and workspace requirements.
- **Rollback-first design**: readiness can be established before mutation; compensation is a last resort.
- **Delete/rewrite stale context automatically**: disagreement is an authority conflict, not implicit permission.
- **Broaden to #2160/#2367/#2392**: requires exact same-seam RED evidence and owner coordination.

## Post-Design Charter Re-check

PASS: the design preserves canonical authorities, uses RED-first evidence, keeps one-issue scope, assigns new branches focused tests, and retains the DRAFT/operator-only landing boundary.
