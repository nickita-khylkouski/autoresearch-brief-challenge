# TechEx Workshop Agenda — Building AI Coding Agents with OpenClaw and MiniMax

**Format:** 60 minutes | **Capacity:** 40–80 attendees | **Hosts:** MiniMax × AI Valley

This agenda supersedes the 50-minute "Presentation Plan" in `MINIMAX_AUTORESEARCH_CHESS_PRD.md` §19. It aligns the existing chess Elo demo to the workshop proposal: attendees build a tool-calling coding agent, then watch it self-improve through an AutoResearch loop.

## One-Line Pitch

Build a coding agent that calls tools, then put it inside an eval loop and watch it teach itself chess.

## Learning Objectives

By the end attendees will be able to:

1. Explain what a tool-calling agent loop is, in code.
2. Build a minimal MiniMax-powered agent that calls tools.
3. Recognize the AutoResearch pattern: agent + eval + constrained surface → compounding improvement.
4. Read a tool-call trace and explain why the agent made each decision.

## Pre-Workshop Setup (email to attendees ~48 hours before)

Required before arrival:

```bash
git clone https://github.com/nickita-khylkouski/autoresearch-brief-challenge
cd autoresearch-brief-challenge
cp .env.example .env
make setup
make stage-demo   # confirms toolchain works in mock mode
```

Optional (for live MiniMax calls during the workshop):

- Sign up for a MiniMax API key
- Add `MINIMAX_API_KEY=...` to `.env`

Anyone without a key uses mock mode and follows along identically; the presenter runs live calls on stage.

## 60-Minute Breakdown

### 0–10 min · Agent Anatomy (Intro)

Slides + one notebook cell.

- What modern AI coding workflows look like
- Three ingredients of an agent: model + tools + loop
- Why MiniMax models perform well at coding and tool calling
- Live: one MiniMax call with one tool, side-by-side with the JSON tool-call payload

**Notebook cell:** `notebooks/workshop.ipynb` §1 — "Hello, tool calling"

### 10–25 min · Wire the Chess Agent (Guided Build, Part 1)

Attendees follow along in the notebook. Each step is a runnable cell.

1. Look at the editable surface (`bot/evaluate.py`, `bot/search.py`, `bot/move_ordering.py`, `bot/config.py`)
2. Register four tools with MiniMax: `read_bot_file`, `list_bot_files`, `get_baseline_eval`, `propose_patch`
3. Run **one** agent iteration end-to-end
4. Open `iterations/001/agent_trace.jsonl` and read the agent's reasoning + tool calls
5. **Try this:** change one tool description, re-run, observe behavior change

**Notebook cell:** §2 — "Your first chess agent iteration"

### 25–50 min · Hit the Loop (Guided Build, Part 2 + AutoResearch reveal)

Run 5 iterations live. While it runs (~3–5 min), narrate:

- AutoResearch = agent + objective eval + constrained edit surface + accept/reject
- The eval is the only thing the agent cannot fake
- Bad ideas are cheap; good ideas compound
- This is a miniature of how MiniMax-style self-improvement loops work

After the run finishes:

1. Open `progress.png` — watch the Elo curve climb
2. Inspect one accepted patch and one rejected patch + reason
3. **Try this:** edit `prompt_builder.py` to bias the agent toward a different heuristic, re-run

**Notebook cell:** §3 — "AutoResearch in action"

### 50–60 min · Q&A and What to Build Next

Open discussion. Talking points if quiet:

- Best practices for tool design (read-only vs. terminal, clear schemas)
- What other domains map to this loop (retrieval, prompt search, parameter golf, code refactors)
- How to swap MiniMax for another tool-calling model
- Where the agent breaks (and why constraints exist)

## Stage-Reliability Plan

| Failure | Mitigation |
|---|---|
| Bad Wi-Fi | `make stage-demo` (mock mode) covers everything except the live segment |
| MiniMax rate limit | Multi-key rotation already in `minimax_client.py`; fall through to mock |
| Live call totally fails | `make replay-best` instantly drops in a captured successful run |
| Attendee setup broken | They watch the presenter notebook; can run it later from clone |
| Notebook kernel dies | CLI fallback: `make live-demo` / `make replay-best` from terminal |

## Hand-Off Artifacts (what attendees leave with)

- A cloned repo with a working agent on their machine
- One accepted patch they can read line-by-line
- A full tool-call trace they can step through
- A starting point for their own AutoResearch experiments

## Dependencies Before Workshop Date

Listed in `#1` (tool calling) and `#2` (OpenClaw-style architecture). The notebook expansion is `#3`. All three must land for this agenda to be deliverable.

- [ ] Issue #1 — tool-calling agent loop
- [ ] Issue #2 — OpenClaw-compatible architecture (Option A)
- [ ] Issue #3 — workshop notebook expansion
- [ ] Pre-workshop setup email sent 48h before
- [ ] Dry-run on a fresh laptop with no API key (mock-only path)
- [ ] Dry-run on stage hardware with live MiniMax key
- [ ] Confirm sponsor expectations re: "OpenClaw" framing

## Open Questions

- **Sponsor framing:** does "OpenClaw" in the proposal title require a literal OpenClaw Gateway runtime, or is "OpenClaw-compatible architecture" acceptable? See `#2`.
- **Attendee API keys:** do TechEx / MiniMax want to issue temporary keys for the room, or do attendees rely on mock mode?
- **Recording:** is the session recorded? If so, the notebook becomes a permanent reference and should be polished accordingly.
