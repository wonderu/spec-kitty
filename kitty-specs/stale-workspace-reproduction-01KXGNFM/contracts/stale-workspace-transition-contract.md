# Stale Workspace Transition Contract

## Inputs

- One canonical reconciled workspace classification produced from persisted context, current lane assignment, and branch inventory for entry points that require workspace readiness. `mark-status` does not resolve a lane workspace.
- Entry-point identity: `mark-status`, `move-task`, or `agent action review`.
- Pre-command snapshots for status, tracking files, refs/commit path sets, locks/paths, and checkout porcelain.

## Classification

| State | Contract |
|---|---|
| Workspace and agreeing lane branch exist | Proceed through existing healthy path. |
| Worktree absent; agreeing lane branch exists | Existing lifecycle may reattach/recreate, then proceed atomically. |
| Worktree and branch absent | Refuse before durable mutation with missing path/lane and supported recovery. |
| Persisted context disagrees with current lane assignment | Refuse before durable mutation; do not choose authority implicitly. |

## Entry-point Delta Matrix

| Entry point | Successful stale-record handling | Refusal |
|---|---|---|
| `mark-status` | PRIMARY tasks tracking commit only; no status/lane/worktree delta | Zero durable delta; structured non-zero result if its own commit cannot land |
| `move-task` | Expected status event/materialization plus PRIMARY WP commit; all owning refs clean | Zero durable delta when workspace readiness is required and unavailable; never success plus commit warning |
| `agent action review` | Workspace ready first, then claim/status and WP evidence at their canonical placements; current placement is measured, not presumed | No claim event, WP mutation, ref movement, lock, created path, or dirt; invocation-owned recovery resources are compensated on later failure |

## Test Prohibitions

The acceptance witness may not monkeypatch any production symbol, Git/subprocess call, root/target discovery, placement resolution, lifecycle sync, commit/status path, or CLI entry point. It may only use canonical fixture serialization, environment isolation, and cache clearing before entering the registered Typer surface with a real temporary Git repository and genuine Git worktrees.

## Disposition Record

Every entry-point × workspace-state row records baseline SHA, exact argv, prerequisites, classification, RED/GREEN, all six before/after surfaces, reached owner, and `stop`/`continue`. Production changes are authorized only for RED/continue rows.

If the review WP/status bundle is proven to land on the wrong authority, the row is a #2160-adjacent residual. The Mission records that relationship before implementation and uses the repository's canonical partition-aware commit seam; it does not claim that the current review coordination transaction already provides that behavior and does not close #2160.

## Output

- Human mode: unmistakable success or actionable refusal; commit failure is never buried under overall success.
- JSON mode: exactly one parseable stdout document whose success/error agrees with durable state.
