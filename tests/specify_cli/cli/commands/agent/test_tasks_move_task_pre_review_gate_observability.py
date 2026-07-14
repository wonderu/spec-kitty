"""Acceptance coverage for observable ``move-task --to for_review`` gates."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from specify_cli.agent_tasks_ports import (
    CommitArtifactResult,
    CommitStatusResult,
    MissionHandle,
    TasksPorts,
)
from specify_cli.cli.commands.agent import tasks_move_task
from specify_cli.cli.commands.agent.tasks import app
from specify_cli.core.commit_guard import GuardCapability
from specify_cli.review import pre_review_gate
from specify_cli.status import Lane, StatusEvent, TransitionRequest
from specify_cli.status.store import append_event
from tests.mocked_env import setup_mocked_env
from tests.specify_cli.cli.commands.agent.test_tasks_ports import (
    FakeFsReader,
    FakeGitOps,
    FakeRender,
)

pytestmark = pytest.mark.fast

_MISSION = "test-pre-review-observability"


@dataclass
class _RecordingCoordRouter:
    write_dir: Path
    status_calls: list[TransitionRequest] = field(default_factory=list)

    def feature_write_dir(self, mission: MissionHandle) -> Path:
        return self.write_dir

    def commit_status(
        self,
        request: TransitionRequest,
        *,
        capability: GuardCapability,
    ) -> CommitStatusResult:
        self.status_calls.append(request)
        return CommitStatusResult(event=None, skipped=False)

    def commit_artifact(
        self,
        mission: MissionHandle,
        paths: object,
        message: str,
        *,
        kind: object,
        policy: object,
    ) -> CommitArtifactResult:
        raise AssertionError("auto-commit is disabled in this acceptance test")


def _build_command_fixture(tmp_path: Path) -> tuple[TasksPorts, _RecordingCoordRouter]:
    feature_dir = tmp_path / "kitty-specs" / _MISSION
    tasks_dir = feature_dir / "tasks"
    tasks_dir.mkdir(parents=True)
    (tmp_path / ".kittify").mkdir()
    (tasks_dir / "WP01-test.md").write_text(
        "---\n"
        "work_package_id: WP01\n"
        "title: Observable gate\n"
        "execution_mode: code_change\n"
        "agent: testbot\n"
        "owned_files:\n  - src/example.py\n"
        "authoritative_surface: src/\n"
        "pre_review_test_scope: tests/example\n"
        "---\n\n# WP01\n\n## Activity Log\n",
        encoding="utf-8",
    )
    append_event(
        feature_dir,
        StatusEvent(
            event_id="test-WP01-in-progress",
            mission_slug=_MISSION,
            wp_id="WP01",
            from_lane=Lane.PLANNED,
            to_lane=Lane.IN_PROGRESS,
            at="2026-07-14T00:00:00+00:00",
            actor="test",
            force=True,
            execution_mode="worktree",
        ),
    )
    router = _RecordingCoordRouter(write_dir=feature_dir)
    return (
        TasksPorts(
            fs=FakeFsReader(),
            coord=router,
            git=FakeGitOps(),
            render=FakeRender(),
        ),
        router,
    )


def test_move_task_human_mode_emits_continuing_gate_liveness(tmp_path: Path) -> None:
    """The exact Typer entry point emits more than its one-shot start notice."""
    ports, router = _build_command_fixture(tmp_path)
    fake_clock = iter((0.0, 30.0, 60.0))

    def controlled_gate(
        scope: pre_review_gate.ScopeResult,
        *,
        repo_root: Path,
        baseline: Any,
        timeout: int = 300,
        progress_callback: Any = None,
        monotonic: Any = None,
        wait: Any = None,
    ) -> pre_review_gate.GateVerdict:
        del repo_root, baseline, timeout, wait
        if progress_callback is not None:
            clock = monotonic or (lambda: next(fake_clock))
            progress_callback(clock())
            progress_callback(clock())
        return pre_review_gate.GateVerdict(
            outcome=pre_review_gate.GateOutcome.UNVERIFIED_BASELINE,
            scope=scope,
            reason="controlled acceptance run",
        )

    with (
        setup_mocked_env(
            tmp_path,
            mission_slug=_MISSION,
            extra_patches={
                "_validate_ready_for_review": (True, []),
                "_check_unchecked_subtasks": [],
            },
        ),
        patch.object(tasks_move_task, "_default_move_task_ports", return_value=ports),
        patch.object(pre_review_gate, "evaluate_with_scope", side_effect=controlled_gate),
    ):
        result = CliRunner().invoke(
            app,
            [
                "move-task",
                "WP01",
                "--to",
                "for_review",
                "--mission",
                _MISSION,
                "--no-auto-commit",
            ],
        )

    assert result.exit_code == 0, result.output
    assert len(router.status_calls) == 1
    assert "running scoped tests at head" in result.output
    assert result.output.count("still running") >= 2

