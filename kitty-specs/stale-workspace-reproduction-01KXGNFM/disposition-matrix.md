# Reviewed Disposition Matrix

**Mission**: `stale-workspace-reproduction-01KXGNFM`  
**Mission ID**: `01KXGNFMHQ4EFZHHZ6M4B56Q8C`  
**Issue**: #2626 (sole claimed issue)  
**Draft PR**: #2641  
**State**: schema checkpoint created during planning; rows remain blocked pending WP01 implementation and independent review

## Authorization Rule

This file becomes the sole row-specific production authorization checkpoint only
after WP01 is independently approved and the orchestrator records the immutable
baseline SHA, witness commit, reviewer, review reference, and complete rows below
with `spec-kitty spec-commit`. Until then, WP02–WP04 must not edit production code.

Spec Kitty 3.2.5 cannot finalize a `planning_artifact` WP owning canonical
`kitty-specs/` paths; upstream gap #2643 records that limitation. The explicit
orchestrator checkpoint is therefore mandatory and may not be replaced by an
implementation handoff or verbal summary.

## Review Metadata

| Field | Value |
|---|---|
| `origin/main` baseline SHA | PENDING WP01 |
| WP01 witness commit SHA | PENDING WP01 |
| independent reviewer | PENDING WP01 REVIEW |
| review reference | PENDING WP01 REVIEW |
| review verdict | PENDING WP01 REVIEW |
| reviewed at | PENDING WP01 REVIEW |

## Required Row Schema

Every applicable command/state arm must record: entry point; exact argv; state
classification; baseline SHA; test node ID; result/exit code; event/materialized
state delta; WP/tasks byte delta; PRIMARY/COORD/lane OIDs and commit path sets;
lock/path delta; checkout porcelain; reached owner; RED/GREEN; stop/continue;
authorized downstream WP; reviewer and review reference.

The ordinary `move-task` acceptance row must not use
`--skip-pre-review-gate`. That escape hatch may appear only as a separately
labelled negative control.

## Reviewed Rows

PENDING WP01 IMPLEMENTATION AND INDEPENDENT REVIEW. This placeholder is not
production authorization.
