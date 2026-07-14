# Implementation Plan: Recover Missing Lane Workspaces

**Branch**: `fix/stale-workspace-reproduction` | **Date**: 2026-07-14 | **Spec**: [spec.md](spec.md)
**Input**: GitHub issue #2626 and the reviewed Mission specification

## Summary

Build one real-Git, real-CLI persisted-workspace fixture that classifies #2626 per entry point and snapshots the complete consistency boundary. Treat the historical recoverable branch-present case honestly if already green. If a current-base RED exists, fix only its proven owner: establish one resolved workspace and readiness before durable review mutation, preserve PRIMARY-versus-COORD placement, and make failure output agree with durable state. Stop without production changes if all exact arms are green.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Typer CLI, Git CLI/subprocess boundary, `mission_runtime` placement seam, Spec Kitty status/workspace/lane modules
**Storage**: Repository files (`meta.json`, `lanes.json`, persisted workspace JSON, status JSONL/materialization, Markdown tracking) and Git refs/worktrees
**Testing**: Pytest with real temporary Git repositories and Typer command entry points; focused unit/integration characterization plus architectural guards
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

- **Purpose**: Reproduce and classify every reported entry point without patching away workspace, commit, or status authority.
- **Relevant requirements**: FR-001, FR-002, FR-003, FR-007, NFR-001
- **Affected surfaces**: `tests/specify_cli/cli/commands/agent/`, existing Git/CLI test helpers
- **Sequencing/depends-on**: none
- **Risks**: A helper-level or mocked test can false-green; branch HEAD and committed path sets must be asserted, not just porcelain.

### IC-02 — Disposition gate and ownership matrix

- **Purpose**: Separate already-green negative controls/recoverable arms from current REDs and bind each RED to its existing owner.
- **Relevant requirements**: FR-003, FR-007, FR-009, C-005, C-007
- **Affected surfaces**: `research.md`, the transition contract, witness results
- **Sequencing/depends-on**: IC-01
- **Risks**: Treating all commands uniformly would manufacture a cross-command resolver and broaden #2626.

### IC-03 — Review readiness before claim

- **Purpose**: If review ordering is RED, resolve once and establish/materialize workspace readiness before `for_review → in_review` mutation.
- **Relevant requirements**: FR-004, FR-005, FR-006, FR-009, C-001, C-002, C-003, C-008
- **Affected surfaces**: `src/specify_cli/cli/commands/agent/workflow.py`, `workflow_executor.py`, `workspace/context.py`, and only proven lifecycle consumers
- **Sequencing/depends-on**: IC-02; conditional on RED
- **Risks**: Cross-placement rollback is error-prone; prefer preflight ordering. Preserve review locks and healthy behavior.

### IC-04 — Lifecycle missing-authority diagnostics

- **Purpose**: If branch-plus-worktree absence is RED, prevent missing-directory Git probes and return one actionable structured refusal from the resolved workspace.
- **Relevant requirements**: FR-005, FR-006, FR-008, FR-009, NFR-004, C-008
- **Affected surfaces**: `src/specify_cli/lanes/lifecycle_sync.py` and focused integration tests
- **Sequencing/depends-on**: IC-02; conditional on RED
- **Risks**: Lifecycle path recomposition would preserve split authority; no directory fabrication or arbitrary branch creation.

### IC-05 — Cross-surface regression evidence

- **Purpose**: Prove healthy behavior, structured output, clean checkouts, correct commit placement, and exact refusal deltas after conditional fixes.
- **Relevant requirements**: FR-002, FR-004, FR-005, FR-008, NFR-002, NFR-003
- **Affected surfaces**: focused CLI/integration suites, Ruff, mypy, architectural gates
- **Sequencing/depends-on**: IC-02 and any implemented IC-03/IC-04
- **Risks**: Passing focused tests without marker/authority guards can miss CI routing or split-placement regressions.

## Execution Strategy

1. Land IC-01 as a test-only commit and capture the planning-base RED/GREEN matrix.
2. Stop production implementation if all exact #2626 arms are green; update Mission evidence only.
3. For each RED, write its owner and expected delta into the disposition matrix before editing production code.
4. Implement the smallest conditional concern, keeping readiness pre-mutation and passing one resolved workspace through the call path.
5. Run IC-05, independent WP review, Mission acceptance/review, and keep PR #2641 DRAFT.

## Rejected Alternatives

- **Fallback commit in the primary checkout**: placement, not directory availability, owns artifacts.
- **One global stale-workspace wrapper**: commands have distinct owners and workspace requirements.
- **Rollback-first design**: readiness can be established before mutation; compensation is a last resort.
- **Delete/rewrite stale context automatically**: disagreement is an authority conflict, not implicit permission.
- **Broaden to #2160/#2367/#2392**: requires exact same-seam RED evidence and owner coordination.

## Post-Design Charter Re-check

PASS: the design preserves canonical authorities, uses RED-first evidence, keeps one-issue scope, assigns new branches focused tests, and retains the DRAFT/operator-only landing boundary.
