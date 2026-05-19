"""ReAct loop for the chess agent.

Calls the model with tool schemas, dispatches any returned tool calls,
appends results back to the conversation, and repeats until the model
either calls the terminal ``edit_file`` tool or emits a final assistant
message containing a diff (fallback).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .context import Conversation
from .tools import ToolContext, dispatch, openai_tool_payload


@dataclass
class ReactTrace:
    rounds: list[dict[str, Any]] = field(default_factory=list)
    final_patch: str | None = None
    stop_reason: str = "max_rounds"

    def record(self, event: dict[str, Any]) -> None:
        self.rounds.append(event)


def _extract_patch_from_text(text: str) -> str | None:
    if not text:
        return None
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    if "diff --git" in stripped or stripped.startswith("--- "):
        return stripped + ("\n" if not stripped.endswith("\n") else "")
    return None


def run_react_loop(
    *,
    convo: Conversation,
    tool_context: ToolContext,
    chat_fn,
    max_rounds: int = 6,
) -> ReactTrace:
    """Run the ReAct loop until terminal tool or fallback patch text.

    ``chat_fn`` must accept ``(messages, tools)`` and return a dict shaped like
    an OpenAI assistant message: ``{"content": str|None, "tool_calls": [...]?, "meta": {...}}``.
    """

    trace = ReactTrace()
    tools_payload = openai_tool_payload()

    for round_index in range(1, max_rounds + 1):
        assistant = chat_fn(convo.messages, tools_payload)
        assistant_message: dict[str, Any] = {
            "content": assistant.get("content"),
        }
        if assistant.get("tool_calls"):
            assistant_message["tool_calls"] = assistant["tool_calls"]
        convo.add_assistant(assistant_message)

        event: dict[str, Any] = {
            "round": round_index,
            "assistant_content": assistant.get("content"),
            "tool_calls": [],
            "meta": assistant.get("meta", {}),
        }

        tool_calls = assistant.get("tool_calls") or []
        if not tool_calls:
            patch = _extract_patch_from_text(assistant.get("content") or "")
            if patch:
                trace.final_patch = patch
                trace.stop_reason = "patch_in_text"
            else:
                trace.stop_reason = "no_tool_call_no_patch"
            trace.record(event)
            return trace

        terminal_hit = False
        for call in tool_calls:
            name = call.get("function", {}).get("name", "")
            arguments_raw = call.get("function", {}).get("arguments", "{}")
            try:
                import json

                arguments = json.loads(arguments_raw) if isinstance(arguments_raw, str) else dict(arguments_raw or {})
            except Exception:
                arguments = {}
            result, terminal = dispatch(name, arguments, tool_context)
            convo.add_tool_result(call.get("id", f"call_{round_index}"), name, result)
            event["tool_calls"].append(
                {
                    "id": call.get("id"),
                    "name": name,
                    "arguments": arguments,
                    "result_preview": result[:400],
                    "terminal": terminal,
                }
            )
            if terminal:
                terminal_hit = True

        trace.record(event)

        if terminal_hit and tool_context.final_patch is not None:
            trace.final_patch = tool_context.final_patch
            trace.stop_reason = "edit_file_tool"
            return trace

    return trace
