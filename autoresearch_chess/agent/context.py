"""Context assembly for the chess agent.

Maps to OpenClaw's context-assembly stage: packages the system prompt,
prior conversation, and any memory snippets before each model call. The
ReAct loop appends tool calls and tool results to ``messages`` between
model turns.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from ..guardrails import EDITABLE_FILES, FORBIDDEN_FILES, FORBIDDEN_PREFIXES


SYSTEM_PROMPT = """You are MiniMax operating inside an AutoResearch chess loop.

Goal: improve the chess bot's estimated Elo by making one focused edit.

You have tools to inspect the editable code and recent run history. Call them
as needed. When you are ready, call `edit_file(path, old_str, new_str)` to
replace one verbatim chunk of an editable file with new text. That call ends
the iteration. The tool synthesizes a unified diff, validates it, and runs
the patched bot in a sandboxed evaluator.

Rules:
- You may edit only these files: {editable}.
- Do not edit forbidden files: {forbidden_files}.
- Do not edit paths under these prefixes: {forbidden_prefixes}.
- No new dependencies. No network, subprocess, filesystem tricks, or opponent
  special cases. Keep the bot legal and fast.
- Prefer one focused change. Keep `old_str`/`new_str` small and targeted.
- Optimize general chess strength through evaluation/search heuristics.

Scoring:
- Baseline estimated Elo: {baseline_elo}.
- Current best estimated Elo: {best_elo}.
- A patch is accepted only when the candidate evaluation improves on the best.

Using edit_file correctly:
- `old_str` must appear verbatim in the file exactly once. Include enough
  surrounding lines so the match is unique.
- Copy `old_str` from the `content` field of `read_bot_file`, NOT from the
  `numbered` field — line-number prefixes are display-only.
- `new_str` is the replacement text; it must differ from `old_str`.

Strategy hints:
- Call `list_bot_files` and `read_bot_file` first to see the current code.
- Call `get_recent_history` to learn what has already been tried.
- Then call `edit_file` with a small, targeted replacement."""


@dataclass
class Conversation:
    messages: list[dict[str, Any]] = field(default_factory=list)

    def add_system(self, content: str) -> None:
        self.messages.append({"role": "system", "content": content})

    def add_user(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, message: dict[str, Any]) -> None:
        self.messages.append({"role": "assistant", **message})

    def add_tool_result(self, tool_call_id: str, name: str, content: str) -> None:
        self.messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": name,
                "content": content,
            }
        )


def build_initial_conversation(
    *, baseline_eval: dict[str, Any], best_eval: dict[str, Any]
) -> Conversation:
    convo = Conversation()
    system = SYSTEM_PROMPT.format(
        editable=", ".join(sorted(EDITABLE_FILES)),
        forbidden_files=", ".join(sorted(FORBIDDEN_FILES)),
        forbidden_prefixes=", ".join(FORBIDDEN_PREFIXES),
        baseline_elo=baseline_eval.get("estimated_elo"),
        best_elo=best_eval.get("estimated_elo"),
    )
    convo.add_system(system)
    convo.add_user(
        "Begin. Inspect the editable bot files, consider the recent history, "
        "then call edit_file with a small, targeted change that should improve "
        "estimated Elo."
    )
    return convo


def summarise_history(history: list[dict[str, Any]]) -> str:
    return json.dumps(history[-5:], ensure_ascii=True, indent=2)
