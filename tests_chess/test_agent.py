from __future__ import annotations

import json
from pathlib import Path

from autoresearch_chess.agent import ChessAgent
from autoresearch_chess.agent.context import build_initial_conversation
from autoresearch_chess.agent.react import run_react_loop
from autoresearch_chess.agent.tools import (
    TOOLS_BY_NAME,
    ToolContext,
    dispatch,
    openai_tool_payload,
)
from autoresearch_chess.config import EvalConfig, LoopConfig, ROOT
from autoresearch_chess.guardrails import EDITABLE_FILES, validate_patch_text
from autoresearch_chess.loop import run_loop
from autoresearch_chess.minimax_client import MiniMaxClient, MiniMaxSettings


def _tool_ctx() -> ToolContext:
    return ToolContext(
        root=ROOT,
        baseline_eval={"estimated_elo": 600.0, "label": "estimated Elo"},
        best_eval={"estimated_elo": 600.0, "label": "estimated Elo"},
        history=[],
    )


def test_tool_schemas_match_openai_function_shape() -> None:
    payload = openai_tool_payload()
    assert payload, "expected at least one tool"
    for item in payload:
        assert item["type"] == "function"
        fn = item["function"]
        assert set(fn.keys()) == {"name", "description", "parameters"}
        assert fn["parameters"]["type"] == "object"


def test_dispatch_list_bot_files_returns_editable_set() -> None:
    result, terminal = dispatch("list_bot_files", {}, _tool_ctx())
    assert not terminal
    assert set(json.loads(result)) == EDITABLE_FILES


def test_dispatch_read_bot_file_rejects_non_editable() -> None:
    result, _ = dispatch("read_bot_file", {"path": "challenge/evaluator.py"}, _tool_ctx())
    assert "not_editable" in result


def test_dispatch_read_bot_file_returns_content() -> None:
    result, _ = dispatch("read_bot_file", {"path": "bot/config.py"}, _tool_ctx())
    payload = json.loads(result)
    assert payload["path"] == "bot/config.py"
    assert "SEARCH_DEPTH" in payload["content"]


def test_dispatch_propose_patch_is_terminal_and_stores_diff() -> None:
    ctx = _tool_ctx()
    diff = "diff --git a/bot/config.py b/bot/config.py\n--- a/bot/config.py\n+++ b/bot/config.py\n@@\n-X\n+Y\n"
    result, terminal = dispatch("propose_patch", {"unified_diff": diff}, ctx)
    assert terminal
    assert json.loads(result)["accepted"] is True
    assert ctx.final_patch == diff


def test_react_loop_terminates_on_propose_patch() -> None:
    """The mock client should drive a three-round dance ending in propose_patch."""

    client = MiniMaxClient(MiniMaxSettings(keys=[]), mock=True)
    convo = build_initial_conversation(
        baseline_eval={"estimated_elo": 600.0},
        best_eval={"estimated_elo": 600.0},
    )
    ctx = _tool_ctx()
    trace = run_react_loop(
        convo=convo,
        tool_context=ctx,
        chat_fn=client.chat_with_tools,
        max_rounds=6,
    )
    assert trace.stop_reason == "propose_patch_tool"
    assert trace.final_patch is not None
    tool_names_per_round = [
        [tc["name"] for tc in round_event["tool_calls"]] for round_event in trace.rounds
    ]
    assert tool_names_per_round == [
        ["list_bot_files"],
        ["read_bot_file"],
        ["propose_patch"],
    ]


def test_react_loop_respects_max_rounds() -> None:
    client = MiniMaxClient(MiniMaxSettings(keys=[]), mock=True)
    convo = build_initial_conversation(
        baseline_eval={"estimated_elo": 600.0},
        best_eval={"estimated_elo": 600.0},
    )
    ctx = _tool_ctx()
    trace = run_react_loop(
        convo=convo,
        tool_context=ctx,
        chat_fn=client.chat_with_tools,
        max_rounds=2,
    )
    assert trace.final_patch is None
    assert trace.stop_reason in {"max_rounds", "no_tool_call_no_patch"}


def test_agent_produces_patch_that_passes_guardrails() -> None:
    client = MiniMaxClient(MiniMaxSettings(keys=[]), mock=True)
    agent = ChessAgent(client)

    # Need to seed read_bot_file with the baseline config so the mock picks an
    # accepted diff. Reset bot/config.py to baseline content for the test.
    config_path = ROOT / "bot" / "config.py"
    original = config_path.read_text(encoding="utf-8")
    config_path.write_text(
        "SEARCH_DEPTH = 1\nMATERIAL_WEIGHT = 1.0\nMOBILITY_WEIGHT = 0.0\n"
        "KING_SAFETY_WEIGHT = 0.0\nUSE_PIECE_SQUARES = False\nCAPTURE_FIRST = True\n",
        encoding="utf-8",
    )
    try:
        result = agent.run_iteration(
            root=ROOT,
            baseline_eval={"estimated_elo": 600.0, "label": "estimated Elo"},
            best_eval={"estimated_elo": 600.0, "label": "estimated Elo"},
            history=[],
        )
    finally:
        config_path.write_text(original, encoding="utf-8")
    assert result.final_patch
    guard = validate_patch_text(result.final_patch)
    assert guard.ok, guard.reasons
    assert result.stop_reason == "propose_patch_tool"


def test_loop_writes_agent_trace_jsonl(tmp_path: Path) -> None:
    """End-to-end: stage loop with tool calling persists trace per iteration."""

    config_path = ROOT / "bot" / "config.py"
    original = config_path.read_text(encoding="utf-8")
    config_path.write_text(
        "SEARCH_DEPTH = 1\nMATERIAL_WEIGHT = 1.0\nMOBILITY_WEIGHT = 0.0\n"
        "KING_SAFETY_WEIGHT = 0.0\nUSE_PIECE_SQUARES = False\nCAPTURE_FIRST = True\n",
        encoding="utf-8",
    )
    try:
        summary = run_loop(
            LoopConfig(
                iterations=1,
                accept_threshold_elo=1.0,
                mock_minimax=True,
                run_id="pytest_agent_trace",
                eval_config=EvalConfig(games_per_opponent=1, max_plies=60),
                use_tool_calling=True,
            )
        )
        trace_path = Path(summary["run_dir"]) / "iterations" / "001" / "agent_trace.jsonl"
        assert trace_path.exists(), "agent_trace.jsonl was not written"
        lines = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(lines) == 3
        assert lines[0]["tool_calls"][0]["name"] == "list_bot_files"
        assert lines[1]["tool_calls"][0]["name"] == "read_bot_file"
        assert lines[2]["tool_calls"][0]["name"] == "propose_patch"
        assert summary["accepted"] == 1
    finally:
        config_path.write_text(original, encoding="utf-8")
        import shutil

        shutil.rmtree(ROOT / "artifacts" / "runs" / "pytest_agent_trace", ignore_errors=True)
