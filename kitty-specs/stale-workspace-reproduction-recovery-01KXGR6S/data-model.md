# Data Model: Stale Workspace Recovery

## Entities

### PersistedWorkspaceContext

- `mission_slug`, `mission_id`, `wp_id`, `lane_id`
- recorded `worktree_path` and `branch_name`
- `lane_wp_ids` and execution mode
- provenance timestamp/version where present

Invariant: a record is evidence, not proof that its path or branch still exists.

### CurrentLaneAssignment

- lane identifier and WP membership from canonical lane metadata
- expected branch identity
- coordination topology/branch

Invariant: disagreement with persisted context is an authority conflict, not permission to choose whichever path exists.

### ResolvedWorkspace

- canonical path, branch, lane, execution mode, resolution kind, existence/readiness
- relationship to persisted context and current lane assignment

Invariant: resolved once before mutation and passed unchanged through readiness, recovery, and command execution.

### ArtifactPlacement

- PRIMARY: `tasks.md` and WP tracking files
- COORD status: event log and materialized status under coordinated topology
- owning ref/worktree and commit result

Invariant: physical placement remains partitioned; a transaction cannot move a PRIMARY file into COORD to simplify rollback.

### TransitionObservation

- exit/result envelope
- event-log and materialized-state before/after
- tracking-file bytes before/after
- ref HEADs and committed path sets before/after
- lock/path existence before/after
- checkout porcelain before/after

Invariant: success requires all intended deltas and clean placement; refusal requires zero durable deltas.

## Relationships

`PersistedWorkspaceContext` is reconciled with `CurrentLaneAssignment` to produce one `ResolvedWorkspace`. The command establishes readiness from that value before creating a `TransitionObservation` delta. State events write to COORD status placement while WP/tasks tracking writes remain PRIMARY; the final result is truthful only when every expected placement commit succeeds.

## State Classification

| Branch agrees/exists | Worktree exists | Classification | Allowed action |
|---|---|---|---|
| yes | yes | ready | proceed |
| yes | no | recoverable husk | reattach/recreate, then proceed |
| no | no | unavailable authority | refuse before mutation |
| disagrees | any | divergent authority | refuse before mutation |
