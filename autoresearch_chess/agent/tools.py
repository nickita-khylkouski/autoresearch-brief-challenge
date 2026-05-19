"""Tool layer for the chess agent.

Each tool is a pure function over the agent's environment (filesystem,
cached eval results, recent history). Tools are read-only or terminal —
the ReAct loop never grants the model a tool that mutates the working
tree mid-iteration. The terminal ``edit_file`` tool ends the loop; the
resulting diff (synthesized by the tool from old_str/new_str) is then
validated by the existing guardrails and run in the sandboxed subprocess
evaluator.

Tool schemas use the JSON-schema function format consumed by both the
OpenAI tool-call protocol and the OpenClaw Gateway.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ..guardrails import EDITABLE_FILES
from ..patcher import compute_edit_diff


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
    raw = target.read_text(encoding="utf-8")
    numbered = "\n".join(
        f"{i:4d}: {line}" for i, line in enumerate(raw.splitlines(), 1)
    )
    return json.dumps({"path": rel, "content": raw, "numbered": numbered})


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


def _edit_file(args: dict[str, Any], ctx: ToolContext) -> str:
    path = str(args.get("path", "")).strip()
    old_str = args.get("old_str")
    new_str = args.get("new_str")
    if path not in EDITABLE_FILES:
        return json.dumps(
            {"ok": False, "error": f"not_editable:{path}", "editable": sorted(EDITABLE_FILES)}
        )
    if not isinstance(old_str, str) or not isinstance(new_str, str):
        return json.dumps({"ok": False, "error": "old_str_and_new_str_must_be_strings"})
    if not old_str:
        return json.dumps({"ok": False, "error": "old_str_empty"})
    diff_text, error = compute_edit_diff(ctx.root, path, old_str, new_str)
    if error or diff_text is None:
        return json.dumps({"ok": False, "error": error or "diff_synthesis_failed"})
    ctx.final_patch = diff_text
    preview = "\n".join(diff_text.splitlines()[:10])
    return json.dumps(
        {"ok": True, "path": path, "diff_preview": preview, "note": "patch_queued_for_validation"}
    )


TOOLS: list[Tool] = [
    Tool(
        name="list_bot_files",
        description="List the bot files the agent is allowed to edit.",
        schema={"type": "object", "properties": {}, "additionalProperties": False},
        handler=_list_bot_files,
    ),
    Tool(
        name="read_bot_file",
        description=(
            "Read the current contents of one editable bot file. Returns both "
            "the raw text (in `content`) and a line-numbered view (in `numbered`). "
            "When you later call `edit_file`, copy your `old_str` from the raw "
            "`content` field — do NOT include line-number prefixes."
        ),
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
        name="edit_file",
        description=(
            "Replace exactly one occurrence of `old_str` with `new_str` inside "
            "an editable bot file. `old_str` must appear in the file verbatim "
            "and exactly once — include enough surrounding context to make it "
            "unique. Calling this tool ends the iteration: the synthesized "
            "diff is validated by the guardrails and then evaluated in a "
            "sandboxed subprocess."
        ),
        schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path of an editable bot file.",
                    "enum": sorted(EDITABLE_FILES),
                },
                "old_str": {
                    "type": "string",
                    "description": (
                        "Exact verbatim text from the file to replace. Must "
                        "appear exactly once. Do not include line-number prefixes."
                    ),
                },
                "new_str": {
                    "type": "string",
                    "description": "Replacement text. Must differ from old_str.",
                },
            },
            "required": ["path", "old_str", "new_str"],
            "additionalProperties": False,
        },
        handler=_edit_file,
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
