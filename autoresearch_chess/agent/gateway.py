"""Agent gateway — OpenClaw-style entry point.

OpenClaw's Gateway routes inbound messages, manages session state, and
hands a packaged context to the ReAct runtime. For the chess demo we
have a single in-process session per loop iteration. ``ChessAgent``
plays that gateway role: it builds the conversation, drives the ReAct
loop, and returns the final patch + trace.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..minimax_client import MiniMaxClient
from .context import build_initial_conversation
from .react import ReactTrace, run_react_loop
from .tools import ToolContext


@dataclass
class AgentResult:
    final_patch: str
    stop_reason: str
    trace: ReactTrace
    meta: dict[str, Any] = field(default_factory=dict)


class ChessAgent:
    def __init__(self, client: MiniMaxClient, *, max_rounds: int = 6) -> None:
        self.client = client
        self.max_rounds = max_rounds

    def run_iteration(
        self,
        *,
        root: Path,
        baseline_eval: dict[str, Any],
        best_eval: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> AgentResult:
        convo = build_initial_conversation(baseline_eval=baseline_eval, best_eval=best_eval)
        tool_ctx = ToolContext(
            root=root,
            baseline_eval=baseline_eval,
            best_eval=best_eval,
            history=list(history),
        )
        trace = run_react_loop(
            convo=convo,
            tool_context=tool_ctx,
            chat_fn=self.client.chat_with_tools,
            max_rounds=self.max_rounds,
        )
        return AgentResult(
            final_patch=trace.final_patch or "",
            stop_reason=trace.stop_reason,
            trace=trace,
            meta={"max_rounds": self.max_rounds},
        )
