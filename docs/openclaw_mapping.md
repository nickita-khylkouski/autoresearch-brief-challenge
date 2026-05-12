# OpenClaw Mapping

The chess demo uses an OpenClaw-compatible agent architecture without depending on the OpenClaw Gateway runtime. This document shows the mapping so attendees can port the same tool surface into a real OpenClaw Gateway deployment after the workshop.

## Why "compatible" and not "running on"

OpenClaw is a self-hosted gateway designed for messaging-platform UIs (WhatsApp, Slack, Discord, etc.). Running it would add a stateful service to the critical path of a 60-minute on-stage demo, which conflicts with `MINIMAX_AUTORESEARCH_CHESS_PRD.md` §4.2 ("complete a short demo iteration in under 2 minutes in stage mode"). We adopt OpenClaw's **architectural seams and tool-schema conventions** so attendees see the right shape, and document the Gateway deployment as the natural next step.

## Workshop strategy: closer clip, not live Gateway

The TechEx workshop honors the OpenClaw partnership branding without taking on the stage-reliability cost of running the Gateway live. The plan, locked with the sponsor:

- **Live demo (minutes 0–50):** runs the in-process compatible architecture below. Three stage fallbacks (live MiniMax → mock MiniMax → captured replay).
- **Closer (minutes 58–60):** plays a 30–60 second pre-recorded clip of the actual OpenClaw Gateway running the same agent with the same four tools. Zero stage risk, full partnership-branding visibility, lands the production deployment story right before attendees leave.

The clip is the marketing artifact; the in-process implementation is the teaching artifact. Both are real. The migration path between them is documented below.

## Architectural seams

| OpenClaw concept | This repo | File |
|---|---|---|
| Gateway (entry, session, routing) | `ChessAgent` | `autoresearch_chess/agent/gateway.py` |
| Context assembly (system prompt + history + memory) | `build_initial_conversation`, `Conversation` | `autoresearch_chess/agent/context.py` |
| ReAct loop (model ↔ tools dispatch) | `run_react_loop` | `autoresearch_chess/agent/react.py` |
| Tool layer (function-shaped capabilities) | `Tool`, `TOOLS`, `dispatch` | `autoresearch_chess/agent/tools.py` |
| Skill/prompt system | `SYSTEM_PROMPT` template | `autoresearch_chess/agent/context.py` |
| Memory | `history` parameter threaded into `ToolContext` | `autoresearch_chess/agent/tools.py` |

## Tool schemas

Tools use the JSON-schema function format that both OpenAI and OpenClaw consume. Each `Tool.to_openai_format()` returns:

```json
{
  "type": "function",
  "function": {
    "name": "read_bot_file",
    "description": "Read the current contents of one editable bot file.",
    "parameters": {
      "type": "object",
      "properties": {"path": {"type": "string", "enum": ["bot/config.py", ...]}},
      "required": ["path"],
      "additionalProperties": false
    }
  }
}
```

This is the same shape OpenClaw expects when registering tools with a running Gateway.

## ReAct loop shape

`run_react_loop` (`autoresearch_chess/agent/react.py:42`) mirrors OpenClaw's ReAct cycle:

```
1. call model with (messages, tools)
2. if response has tool_calls:
     for each call: dispatch → append tool result to messages
     loop
3. if response is plain text:
     try to extract a fallback patch; otherwise stop
4. if a tool flagged terminal: stop
```

A bounded `max_rounds` prevents runaway loops. Each round is persisted to `iterations/NNN/agent_trace.jsonl` for inspection.

## What changes for a Gateway-backed deployment

To migrate the demo onto a real OpenClaw Gateway:

1. **Register the tools with the Gateway** — `openai_tool_payload()` in `autoresearch_chess/agent/tools.py` already produces the right schemas; pass that list to the Gateway's tool-registration endpoint.
2. **Replace `MiniMaxClient.chat_with_tools`** with a Gateway-driven session. The Gateway owns the model call; our code becomes the tool-execution side of the loop.
3. **Move tool dispatch behind an HTTP boundary** — the Gateway invokes our tools over RPC instead of in-process. `dispatch` in `tools.py` stays the same; only the calling convention changes.
4. **Pick a transport channel** — WhatsApp, Slack, CLI, or a custom adapter. The chess demo is naturally a CLI; the rest of OpenClaw's channel infrastructure is not exercised by this workload.

The architectural separation in `agent/` is designed to make this swap mechanical: nothing outside `gateway.py` knows whether the model call is in-process or going through a Gateway.

## Out of scope

- Messaging-channel adapters (WhatsApp, Slack, etc.) — not relevant to the Elo demo
- OpenClaw memory/scheduling features — covered well enough by `history` + the per-iteration trace
- Authentication and multi-user session handling — single-presenter demo
