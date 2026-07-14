# Tooling Friction Log

> Log every place the tooling fought you so it can feed the tooling-gap backlog.

## Entries

- 2026-07-14 — GitHub ticket intake through `mission create --from-ticket` required hosted Spec Kitty authentication even though `gh` was authenticated, so canonical ticket context could not be generated.
- 2026-07-14 — The canonical planning prompt passed `--mission` to `agent mission branch-context`, but the installed 3.2.5 command rejected that option.
- 2026-07-14 — Discarding an accidentally main-bound Mission created a retrospective commit on local main and left its scaffold untracked; local main had to be restored to `origin/main` before recreating the PR-bound Mission.
- 2026-07-14 — The PR-bound coordination worktree is registered as healthy but lacks the Mission directory, and workspace repair does not populate it; planning remains on the dedicated fix branch.
- 2026-07-14 — Two open-ended planning subagent attempts stalled without producing artifacts; the orchestrator resumed from verified code-truth findings.
- 2026-07-14 — Several open issue facets were already delivered on the planning base, requiring commit and focused-test reconciliation before scope could be trusted.
- 2026-07-14 — The repository shell did not expose `pytest` directly despite the documented command; validation required the managed `uv run pytest` entry point.
- 2026-07-14 — Post-plan code-truth review found the apparent pre-mutation hook was preceded by lane-deliverable auto-commit, and timeout was erased into `no_coverage`; the first plan had to be structurally revised before tasks.
- 2026-07-14 — `finalize-tasks` committed generated `tasks.md`, WP prompt, and lane metadata but omitted the authoritative `wps.yaml`; it must be committed separately through the planning artifact workflow.
- 2026-07-14 — A read-only post-tasks reviewer accidentally reran mutating finalization, creating timestamp-only commit `1490c745`; it was retained as non-destructive history and no further reviewer mutations were allowed.
