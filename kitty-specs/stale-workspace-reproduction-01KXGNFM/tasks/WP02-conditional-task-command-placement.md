---
work_package_id: WP02
title: Conditional task-command and placement remediation
dependencies:
- WP01
requirement_refs:
- FR-003
- FR-005
- FR-006
- FR-007
- FR-008
- FR-009
- NFR-002
- NFR-003
- C-001
- C-004
- C-005
- C-006
- C-008
tracker_refs: []
planning_base_branch: fix/stale-workspace-reproduction
merge_target_branch: fix/stale-workspace-reproduction
branch_strategy: Planning artifacts for this mission were generated on fix/stale-workspace-reproduction. During /spec-kitty.implement this WP may branch from a dependency-specific base, but completed changes must merge back into fix/stale-workspace-reproduction unless the human explicitly redirects the landing branch.
subtasks:
- T006
- T007
- T008
- T009
- T010
agent: codex
history: []
agent_profile: python-pedro
authoritative_surface: src/specify_cli/cli/commands/agent/
create_intent: []
execution_mode: code_change
model: ''
owned_files:
- src/specify_cli/cli/commands/agent/tasks_mark_status.py
- src/specify_cli/cli/commands/agent/tasks_move_task.py
- src/specify_cli/cli/commands/agent/tasks_parsing_validation.py
- src/specify_cli/coordination/commit_router.py
- tests/specify_cli/cli/commands/agent/test_tasks_mark_status.py
- tests/specify_cli/cli/commands/agent/test_tasks_mark_status_seam.py
- tests/specify_cli/cli/commands/agent/test_tasks_move_task_authority_staging.py
- tests/specify_cli/cli/commands/agent/test_tasks_move_task_placement.py
- tests/specify_cli/cli/commands/agent/test_tasks_move_task_seam.py
- tests/specify_cli/coordination/test_commit_router_placement.py
- tests/specify_cli/coordination/test_commit_router_partition.py
role: implementer
tags: []
---

# WP02 — Conditional Task-Command and Placement Remediation

## ⚡ Do This First: Load Agent Profile

Use `/ad-hoc-profile-load python-pedro` before reading or changing anything.
Adopt that profile's Python, test-first, locality, and verification discipline for
the entire work package.

- **Profile**: `python-pedro`
- **Role**: `implementer`
- **Agent/tool**: `codex`

Stop if the profile cannot be loaded.

## Objective

Consume the committed, independently reviewed disposition matrix. Change task-command or
placement code only for a row that is both `RED` and `continue` and whose reached
owner is one of this WP's declared paths. Preserve every GREEN arm unchanged.
If no owned row is RED, complete this package as an evidence-backed no-op.

This WP exists so a current defect in `mark-status`, ordinary `move-task`, or the
canonical placement router is actionable without silently broadening lifecycle
or review ownership. It is not authority for a general command refactor.

## Canonical Workspace Entry

Prepare the implementation workspace only through:

```bash
spec-kitty agent action implement WP02 --agent codex
```

Use the returned workspace path and branch. Do not guess a `.worktrees` path,
manually create a worktree, or edit from the repository-root planning checkout.
Confirm WP01 is approved or done and the committed disposition matrix has no
pending review metadata or pending rows before touching code.

## Owned Surface

The complete ownership allowlist is the `owned_files` frontmatter above. The
production candidates divide into:

- task transition entry points: `tasks_mark_status.py`, `tasks_move_task.py`;
- shared parsing/validation only if the reviewed call path reaches it;
- canonical placement: `coordination/commit_router.py`;
- existing focused tests for those exact seams.

Do not edit workspace context, lifecycle synchronization, review workflow,
Mission planning artifacts, status runtime modules, or unrelated tests. WP03 owns
lifecycle reconciliation. WP04 owns review action ordering and aggregate proof.

## Mandatory Activation Gate

For each reviewed matrix row relevant to this package, extract:

- exact command and state classification;
- baseline SHA and test node ID;
- RED/GREEN verdict;
- reached owner;
- six-surface delta;
- stop/continue decision;
- reviewer identity and review reference.

Then apply:

1. No RED/continue row in an owned path: do not edit production or tests; run the
   focused regression set and report byte-identical owned production paths.
2. RED/continue in an owned path: preserve the failing witness as the red-first
   evidence commit, then make the smallest owner-local fix.
3. RED/continue reaches an undeclared path: stop for plan amendment and task
   refinalization. Do not expand ownership ad hoc.
4. Contradictory, missing, or unreviewed matrix evidence: reject the package.

## Behavioral Invariants

### `mark-status`

`mark-status` is the workspace-free negative control. It may mutate canonical
tracking state without requiring a lane worktree, but must still preserve the
correct placement and atomic failure contract. Do not add workspace resolution
merely to make commands look uniform.

### Ordinary `move-task`

The acceptance path is:

```text
agent tasks move-task WP01 --to for_review --mission <slug> --agent codex --json
```

Do not use `--skip-pre-review-gate` as proof of the normal path. The skip option
returns before workspace resolution and is only a negative control.

### Placement

PRIMARY owns WP/task tracking and COORD owns status state in coordinated
topologies. If the reviewed row proves placement RED, adapt the existing command
to the canonical partition-aware commit seam. Do not hand-roll two commits, do
not write from the wrong checkout, and do not claim #2160 as solved.

### Failure Atomicity

Unavailable or divergent authority must fail before durable mutation. Evidence
must show:

- empty before/after ref ranges;
- byte-identical WP/tasks and status surfaces;
- no leaked lock;
- no fabricated directory or branch;
- clean relevant checkout porcelain.

A matching existing branch plus missing path may use existing canonical recovery
when the reviewed row authorizes it. An absent branch or divergent authority may
not fall back to the primary checkout.

## Red-First Discipline

When activated, keep a distinct test-remediation commit that fails on the
reviewed baseline for the same production reason. Do not weaken assertions after
the red commit. The implementation commit follows and contains only the minimum
owned production/test paths.

If WP01 already provides the exact failing acceptance node, reuse it as the
external witness and add focused owner tests only for branches the acceptance
module cannot isolate. Do not duplicate the full real-Git fixture across files.

## Subtasks

### T006 — Validate row authorization

Map each task-command/placement row to one owned path and confirm the matrix is
committed, complete, reviewed, and based on the recorded baseline.

### T007 — Preserve or add focused RED evidence

For activated rows, run the exact WP01 node and the smallest focused seam test.
Commit failing test evidence separately before production changes. For no-op,
record the exact green commands and production-file hashes.

### T008 — Implement the smallest owner-local correction

Change only the reached owner. Resolve workspace identity at most once where the
command actually requires it, and use the canonical placement seam for commits.

### T009 — Prove six-surface atomicity and placement

Run the WP01 entry-point rows plus focused placement and authority tests. Compare
ref OIDs, committed path sets, bytes, locks/paths, state events, and porcelain.

### T010 — Regression and handoff

Run focused tests, Ruff, mypy for changed modules, and relevant architectural
guards. Report activated rows, no-op rows, commits, commands, and residual risks
to the independent reviewer and WP03.

## Focused Verification

Use only tests relevant to activated owners, drawing from:

```bash
pytest -q tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py
pytest -q tests/specify_cli/cli/commands/agent/test_tasks_mark_status.py
pytest -q tests/specify_cli/cli/commands/agent/test_tasks_mark_status_seam.py
pytest -q tests/specify_cli/cli/commands/agent/test_tasks_move_task_authority_staging.py
pytest -q tests/specify_cli/cli/commands/agent/test_tasks_move_task_placement.py
pytest -q tests/specify_cli/cli/commands/agent/test_tasks_move_task_seam.py
pytest -q tests/specify_cli/coordination/test_commit_router_placement.py
pytest -q tests/specify_cli/coordination/test_commit_router_partition.py
ruff check <changed Python paths>
mypy <changed production Python paths>
```

Also run `git diff --check`, inspect changed path ownership, and confirm the lane
workspace is clean after commits. Do not use retry-to-green.

## Definition of Done

- The committed, independently reviewed matrix is the sole activation authority.
- The ordinary non-skipped `move-task` row is classified.
- Every activated RED has a distinct red-first evidence commit.
- Only its reached owned path changes.
- GREEN rows retain byte-identical production files.
- Failure rows have empty commit ranges and no durable side effects.
- Successful rows preserve canonical PRIMARY/COORD placement.
- The complete focused verification set for activated owners passes.
- An undeclared reached owner blocks for refinalization.

## Reviewer Guidance

Use a reviewer distinct from the implementer. Re-run the exact authorized WP01
nodes and focused owner tests; inspect commit ordering and path ownership rather
than trusting the handoff. Reject skip-gated `move-task` as acceptance evidence.
Reject any edit for a GREEN/stop row, any production path absent from the manifest,
or any command-local placement workaround. A valid no-op review proves the matrix
is GREEN for this ownership map and the declared production files are unchanged.
