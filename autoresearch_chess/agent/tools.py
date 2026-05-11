"""Tool layer for the chess agent.

Each tool is a pure function over the agent's environment (filesystem,
cached eval results, recent history). Tools are read-only or terminal —
the ReAct loop never grants the model a tool that mutates the working
tree mid-iteration. The terminal ``propose_patch`` tool ends the loop;
the resulting diff is then validated by the existing guardrails and run
in the sandboxed subprocess evaluator.

Tool schemas use the JSON-schema function format consumed by both the
OpenAI tool-call protocol and the OpenClaw Gateway.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ..guardrails import EDITABLE_FILES


ToolFn = Callable[[dict[str, Any], "ToolContext"], str]


@dataclass
class ToolContext:
    """Bundle of read-only state tools may inspect."""

    root: Path
    baseline_eval: dict[str, Any]
    best_eval: dict[str, Any]
    history: list[dict[str, Any]]
    final_patch: str | None = field(default=None)


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    schema: dict[str, Any]
    handler: ToolFn
    terminal: bool = False

    def to_openai_format(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.schema,
            },
        }


def _list_bot_files(_: dict[str, Any], ctx: ToolContext) -> str:
    return json.dumps(sorted(EDITABLE_FILES))


def _read_bot_file(args: dict[str, Any], ctx: ToolContext) -> str:
    rel = str(args.get("path", "")).strip()
    if rel not in EDITABLE_FILES:
        return json.dumps({"error": f"not_editable:{rel}", "editable": sorted(EDITABLE_FILES)})
    target = ctx.root / rel
    if not target.exists():
        return json.dumps({"error": f"missing:{rel}"})
    return json.dumps({"path": rel, "content": target.read_text(encoding="utf-8")})


def _get_baseline_eval(_: dict[str, Any], ctx: ToolContext) -> str:
    return json.dumps(
        {
            "baseline_estimated_elo": ctx.baseline_eval.get("estimated_elo"),
            "best_estimated_elo": ctx.best_eval.get("estimated_elo"),
            "label": ctx.baseline_eval.get("label", "estimated Elo"),
        }
    )


def _get_recent_history(args: dict[str, Any], ctx: ToolContext) -> str:
    try:
        limit = int(args.get("n", 3))
    except (TypeError, ValueError):
        limit = 3
    limit = max(1, min(limit, 10))
    return json.dumps(ctx.history[-limit:])


def _propose_patch(args: dict[str, Any], ctx: ToolContext) -> str:
    diff = str(args.get("unified_diff", ""))
    if not diff.strip():
        return json.dumps({"accepted": False, "error": "empty_diff"})
    ctx.final_patch = diff
    return json.dumps({"accepted": True, "note": "patch_queued_for_validation"})


TOOLS: list[Tool] = [
    Tool(
        name="list_bot_files",
        description="List the bot files the agent is allowed to edit.",
        schema={"type": "object", "properties": {}, "additionalProperties": False},
        handler=_list_bot_files,
    ),
    Tool(
        name="read_bot_file",
        description="Read the current contents of one editable bot file.",
        schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path of an editable bot file.",
                    "enum": sorted(EDITABLE_FILES),
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        handler=_read_bot_file,
    ),
    Tool(
        name="get_baseline_eval",
        description="Return baseline and current-best estimated Elo for the chess bot.",
        schema={"type": "object", "properties": {}, "additionalProperties": False},
        handler=_get_baseline_eval,
    ),
    Tool(
        name="get_recent_history",
        description="Return the last N iteration outcomes (accept/reject + reasons).",
        schema={
            "type": "object",
            "properties": {
                "n": {
                    "type": "integer",
                    "description": "Number of recent iterations to return (1-10).",
                    "minimum": 1,
                    "maximum": 10,
                }
            },
            "additionalProperties": False,
        },
        handler=_get_recent_history,
    ),
    Tool(
        name="propose_patch",
        description=(
            "Submit a unified diff that edits one or more editable bot files. "
            "Calling this tool ends the iteration. The patch is validated by "
            "the guardrails and then evaluated in a sandboxed subprocess."
        ),
        schema={
            "type": "object",
            "properties": {
                "unified_diff": {
                    "type": "string",
                    "description": "Unified diff patch text.",
                }
            },
            "required": ["unified_diff"],
            "additionalProperties": False,
        },
        handler=_propose_patch,
        terminal=True,
    ),
]


TOOLS_BY_NAME: dict[str, Tool] = {tool.name: tool for tool in TOOLS}


def openai_tool_payload() -> list[dict[str, Any]]:
    return [tool.to_openai_format() for tool in TOOLS]


def dispatch(name: str, arguments: dict[str, Any], ctx: ToolContext) -> tuple[str, bool]:
    tool = TOOLS_BY_NAME.get(name)
    if tool is None:
        return json.dumps({"error": f"unknown_tool:{name}"}), False
    try:
        result = tool.handler(arguments or {}, ctx)
    except Exception as exc:  # pragma: no cover - defensive
        result = json.dumps({"error": f"tool_exception:{type(exc).__name__}:{exc}"})
    return result, tool.terminal
