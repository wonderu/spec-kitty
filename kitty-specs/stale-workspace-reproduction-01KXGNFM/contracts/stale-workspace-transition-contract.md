# Stale Workspace Transition Contract

## Inputs

- One canonical `ResolvedWorkspace` produced from persisted context and current lane assignment.
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
| `agent action review` | Workspace ready first, then review claim/status and PRIMARY WP evidence at owning placements | No claim event, WP mutation, ref movement, lock, created path, or dirt |

## Test Prohibitions

The acceptance witness may not patch or replace `resolve_workspace_for_wp`, `commit_for_mission`, `safe_commit`, status emission/materialization, or the CLI entry point. It serializes a real workspace context, clears relevant caches, and enters through Typer with a real temporary Git repository.

## Output

- Human mode: unmistakable success or actionable refusal; commit failure is never buried under overall success.
- JSON mode: exactly one parseable stdout document whose success/error agrees with durable state.
