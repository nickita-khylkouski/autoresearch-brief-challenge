"""OpenClaw-style tool-calling agent for the chess AutoResearch loop.

See ``docs/openclaw_mapping.md`` for how these modules map onto OpenClaw's
gateway / context / react / tool-layer architecture.
"""

from .gateway import AgentResult, ChessAgent

__all__ = ["AgentResult", "ChessAgent"]
