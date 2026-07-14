# Reviewed Disposition Matrix

**Mission**: `stale-workspace-reproduction-recovery-01KXGR6S`  
**Mission ID**: `01KXGR6SRKX7C1RB77MAWN2R34`  
**Issue**: #2626 (sole claimed issue)  
**Draft PR**: #2641  
**State**: reviewed and authoritative for downstream conditional implementation

## Authorization Rule

This PRIMARY planning artifact is the sole row-specific production authorization
checkpoint. Only rows marked `RED/continue` authorize their named downstream WP.
Rows marked `GREEN/stop` prohibit production changes for that arm. A downstream
implementer must stop and request plan amendment/refinalization if the reached
owner differs from the reviewed owner below.

Spec Kitty 3.2.5 cannot finalize a `planning_artifact` WP owning canonical
`kitty-specs/` paths; upstream gap #2643 records that limitation. The explicit
orchestrator checkpoint is therefore mandatory and may not be replaced by an
implementation handoff or verbal summary.

## Review Metadata

| Field | Value |
|---|---|
| `origin/main` baseline SHA | `2d05c53d03ee794885954410ae6a63c29d432869` |
| WP01 witness commits | cycle 1 `1902ce530759b80e2bbaaa1b134fa8c73de8729e`; approved cycle 2 `ff7eca5e2c248730909d91cddde93c6c01232701` |
| independent reviewer | Reviewer Renata (`reviewer-renata`) |
| review reference | `ff7eca5e2c248730909d91cddde93c6c01232701` |
| approval event | `01KXGVAMKBG68FTJW1R1P10PVZ` |
| coordination status commit | `c2d41927e` |
| review verdict | APPROVED — two exact runs reproduced 5 GREEN / 7 intentional RED; Ruff passed |
| reviewed at | `2026-07-14T17:38:20.907471+00:00` |

## Required Row Schema

Every applicable command/state arm must record: entry point; exact argv; state
classification; baseline SHA; test node ID; result/exit code; event/materialized
state delta; WP/tasks byte delta; PRIMARY/COORD/lane OIDs and commit path sets;
lock/path delta; checkout porcelain; reached owner; RED/GREEN; stop/continue;
authorized downstream WP; reviewer and review reference.

The ordinary `move-task` acceptance row must not use
`--skip-pre-review-gate`. That escape hatch may appear only as a separately
labelled negative control.

## Evidence Legend

- Test module: `tests/specify_cli/cli/commands/agent/test_stale_workspace_transition_contract.py`; every node is
  `test_stale_workspace_transition_matrix[<entry>-<state>]`.
- Fixture Mission: `coord-topo-fixture-01KW2E7A`. All rows assert the real
  registered Typer entry point, exact argv, structured/stdout/stderr result,
  event-log bytes, materialized and independently reduced bytes, WP/tasks bytes,
  PRIMARY/COORD/lane OIDs and ordered commit path sets, review locks, worktree
  path existence, and porcelain for every checkout before the final RED assertion.
- `STATUS` means both `status.events.jsonl` and `status.json` on COORD. `WP`
  means `tasks/WP01-witness.md` on PRIMARY unless a row explicitly records the
  command's COORD/lane placement. `TASKS` means PRIMARY `tasks.md`.
- Every unavailable or divergent row executable-asserts monotonic elapsed time
  `<2s`. The scoped pre-review gate actually ran (`ran=True`) for `move-task`;
  its production result is truthfully `unverified_baseline`, not `no_coverage`.

## Reviewed Rows

| # | Entry/state and exact argv | Result and six-surface delta | Reached owner | Disposition / authorization |
|---|---|---|---|---|
| 1 | `mark-status-healthy`: `agent tasks mark-status T001 --status done --mission coord-topo-fixture-01KW2E7A --json` | exit 0; summary `updated=1`; STATUS/WP unchanged, TASKS changed; PRIMARY advances with only `tasks.md`; COORD/lane unchanged; no lock/path change; all checkouts clean | PRIMARY task tracking | `GREEN/stop`; none |
| 2 | `mark-status-recoverable`: same exact argv | exit 0; identical authoritative bytes/ref placement to row 1; missing lane path remains missing; all existing checkouts clean | PRIMARY task tracking | `GREEN/stop`; none |
| 3 | `mark-status-unavailable`: same exact argv | exit 0 `<2s`; identical authoritative bytes/ref placement to row 1; lane ref/path absent; all existing checkouts clean | PRIMARY task tracking | `GREEN/stop`; none |
| 4 | `mark-status-divergent`: same exact argv | exit 0 `<2s`; identical authoritative bytes/ref placement to row 1 despite persisted lane-z identity; registered lane-a remains clean | PRIMARY task tracking | `GREEN/stop`; none |
| 5 | `move-task-healthy`: `agent tasks move-task WP01 --to for_review --mission coord-topo-fixture-01KW2E7A --agent codex --json` | exit 0 `result=success`; gate ran, `outcome=unverified_baseline`, target `tests/witness_gate`; STATUS/materialized/reduced and WP change, TASKS unchanged; PRIMARY advances with WP only, COORD advances with STATUS only, lane unchanged; no lock/path change; all clean | move-task workspace readiness | `GREEN/stop`; none |
| 6 | `move-task-recoverable`: same exact argv | exit 0 with the same durable transition and exact placement as row 5 even though the registered worktree was missing; path remains missing; no locks; all existing checkouts clean | move-task workspace readiness | `RED/continue`; WP02 |
| 7 | `move-task-unavailable`: same exact argv | exit 0 `<2s` with the same durable transition and exact placement as row 5 despite absent lane branch and path; no locks; all existing checkouts clean | move-task workspace readiness | `RED/continue`; WP02 |
| 8 | `move-task-divergent`: same exact argv | exit 0 `<2s` with the same durable transition and exact placement as row 5 despite persisted lane-z versus registered lane-a; no locks; all checkouts clean | move-task workspace readiness | `RED/continue`; WP02 |
| 9 | `review-healthy`: `agent action review WP01 --agent codex --mission coord-topo-fixture-01KW2E7A` | exit 0; STATUS and WP bytes change, TASKS unchanged; PRIMARY ref does not advance, COORD advances with STATUS+WP, lane advances through STATUS/STATUS/WP/empty commits; one review lock added; lane path exists; PRIMARY WP is left dirty | review claim/commit routing | `RED/continue`; WP04; #2160-adjacent placement residual only |
| 10 | `review-recoverable`: same exact argv | exit 0; missing worktree is recreated; otherwise the exact bytes, ref movement/path sets, added lock, and dirty PRIMARY WP match row 9 | review claim/commit routing | `RED/continue`; WP04; #2160-adjacent placement residual only |
| 11 | `review-unavailable`: same exact argv | exit 1 `<2s` with raw `[Errno 2] No such file or directory`; STATUS/materialized/reduced unchanged after compensation, WP changes, TASKS unchanged; PRIMARY ref unchanged, COORD advances through STATUS+WP+WP commits, lane ref/path absent; no lock; PRIMARY/COORD remain dirty | review claim/commit routing | `RED/continue`; WP04 |
| 12 | `review-divergent`: same exact argv | exit 0 `<2s`; accepts registered lane-a despite persisted lane-z; otherwise the exact bytes, ref movement/path sets, added lock, existing lane path, and dirty PRIMARY WP match row 9 | review claim/commit routing | `RED/continue`; WP04 |

WP03 has no authorized row: WP01 reached the task-command/placement owner for
rows 6–8 and the review claim/commit-routing owner for rows 9–12. WP03 must
therefore execute its declared no-op/verification path and must not edit
production lifecycle code unless a later independently reviewed row reaches its
owner and this matrix is amended and recommitted.
