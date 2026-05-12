# TechEx Workshop Agenda — Building AI Coding Agents with OpenClaw and MiniMax

**Format:** 60 minutes | **Capacity:** 40–80 attendees | **Hosts:** MiniMax × AI Valley

This agenda supersedes the 50-minute "Presentation Plan" in `MINIMAX_AUTORESEARCH_CHESS_PRD.md` §19. It aligns the existing chess Elo demo to the workshop proposal: attendees build a tool-calling coding agent on the OpenClaw architecture, then watch it self-improve through an AutoResearch loop.

## One-Line Pitch

Three ingredients of a modern coding agent: an architecture, a model, and a loop. OpenClaw gives us the architecture. MiniMax gives us the model. AutoResearch is what happens when you put them inside an eval loop and let the agent improve itself. Today we build all three.

## Framing Decisions (locked)

- **OpenClaw is in the title and stays there.** The live demo runs an OpenClaw-*compatible* architecture (gateway / context / react / tools as separate layers) rather than the OpenClaw Gateway runtime. The architecture is what teaches the pattern; the Gateway is one deployment of that pattern.
- **The workshop closes with a 30–60 second recorded clip of the actual Gateway running** the same agent with the same tools. That honors the OpenClaw partnership visibly without putting a stateful service on the on-stage critical path.
- **AutoResearch is the cutting-edge headline** — the differentiator that makes this a MiniMax workshop rather than a generic tool-calling tutorial. The 25–50 min block is where most of the wow lives.

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

Slides + one notebook cell. Sets up the three-ingredient frame the rest of the workshop fills in.

- **Slide 1 — the three-ingredient pitch.** Architecture (OpenClaw) + model (MiniMax) + loop (AutoResearch). State this in one sentence so it anchors the rest of the session.
- **Slide 2 — the OpenClaw architecture as code.** Show OpenClaw's four layers (Gateway, Context, ReAct, Tools) next to the four files in `autoresearch_chess/agent/` (`gateway.py`, `context.py`, `react.py`, `tools.py`). One-to-one mapping. Attendees see architecture-as-code in 30 seconds.
- **Slide 3 — why MiniMax for coding and tool calling.** Concrete tool-calling benchmarks, latency, JSON-schema reliability. This is load-bearing for the AutoResearch payoff — the loop only compounds if the model can tool-call reliably.
- **Live cell — "Hello, tool calling."** One MiniMax call with one tool, side-by-side with the JSON tool-call payload.

**Notebook cell:** `notebooks/workshop.ipynb` §1 — "Hello, tool calling" *(currently missing; add before the event)*

### 10–25 min · Wire the Chess Agent (Guided Build, Part 1)

We fill in OpenClaw's four layers, one file at a time. Each step is a runnable notebook cell.

1. **Tool layer** — `autoresearch_chess/agent/tools.py`. Four tools: `read_bot_file`, `list_bot_files`, `get_baseline_eval`, `propose_patch`. Point out the JSON-schema format that both MiniMax and OpenClaw consume.
2. **Context layer** — `autoresearch_chess/agent/context.py`. System prompt + conversation assembly.
3. **ReAct layer** — `autoresearch_chess/agent/react.py`. Bounded model ↔ tools loop.
4. **Gateway layer** — `autoresearch_chess/agent/gateway.py`. Entry point that wires the other three together.
5. Show the editable surface the agent will modify: `bot/evaluate.py`, `bot/search.py`, `bot/move_ordering.py`, `bot/config.py`.
6. Run **one** agent iteration end-to-end.
7. Open `iterations/001/agent_trace.jsonl` and read the agent's reasoning + tool calls.
8. **Try this:** change one tool description, re-run, observe behavior change.

**Notebook cell:** §2 — "Your first chess agent iteration"

### 25–50 min · Hit the Loop (AutoResearch reveal — the headline)

This is the cutting-edge moment. Frame it explicitly:

> "What you've built so far is a tool-calling agent. Every tutorial on the internet stops here. The interesting thing — and the reason this is in a MiniMax workshop and not a generic agent workshop — is what happens when you put this agent inside an eval loop with a constrained edit surface. Watch."

Run 5 iterations live (bumped from 2 in the current notebook — the Elo climb is more dramatic). While it runs (~3–5 min), narrate the AutoResearch principles:

- **AutoResearch = agent + objective eval + constrained edit surface + accept/reject**
- The eval is the only thing the agent cannot fake
- Bad ideas are cheap; good ideas compound
- This is a miniature of how MiniMax-style self-improvement loops work in production

After the run finishes:

1. Open `progress.png` — watch the Elo curve climb (captured run goes 629.6 → 1163.4 → 1276.1)
2. Inspect one accepted patch and one rejected patch + reason
3. **Try this:** edit `prompt_builder.py` to bias the agent toward a different heuristic, re-run

**Notebook cell:** §3 — "AutoResearch in action" *(bump `--iterations 2` to `--iterations 5` before the event)*

### 50–58 min · Q&A

Open discussion. Talking points if quiet:

- Best practices for tool design (read-only vs. terminal, clear schemas)
- What other domains map to this loop (retrieval, prompt search, parameter golf, code refactors)
- How to swap MiniMax for another tool-calling model
- Where the agent breaks (and why constraints exist)
- If asked about OpenClaw deployment: "The architectural seams make Gateway deployment mechanical — see `docs/openclaw_mapping.md`. We taught the shape today; here's what production looks like…" *(leads into the closer)*

### 58–60 min · The Closer — OpenClaw Gateway clip

Play the 30–60 second pre-recorded clip showing the same agent, same tools, running through the actual OpenClaw Gateway. Land the line:

> "What you saw today was the OpenClaw architecture running in-process so we could keep the demo on one machine. Here's the exact same agent on the actual OpenClaw Gateway. The migration is mechanical — see `docs/openclaw_mapping.md`. This is what production looks like, three days of work from where you are now."

The clip exists to honor the OpenClaw partnership branding visibly without putting a stateful service on the on-stage critical path. If the clip wasn't recorded in time, drop this segment and lean on `docs/openclaw_mapping.md` verbally — the workshop still delivers.

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
- A clear mental model of the OpenClaw four-layer architecture and how to migrate to the real Gateway (`docs/openclaw_mapping.md`)

## Dependencies Before Workshop Date

Already landed:

- [x] Issue #1 — tool-calling agent loop
- [x] Issue #2 — OpenClaw-compatible architecture (Option A — architectural seams only)
- [x] Sponsor framing decision — OpenClaw stays in the title; live demo runs the compatible architecture; closer clip shows the Gateway

Still needed before the event:

- [ ] Slide 1 — three-ingredient pitch (architecture + model + loop)
- [ ] Slide 2 — OpenClaw four-layer architecture mapped to `autoresearch_chess/agent/` files
- [ ] Slide 3 — "Why MiniMax for coding/tool calling" with concrete numbers (benchmarks, latency, JSON-schema reliability)
- [ ] Notebook §1 cell — "Hello, one tool call" (currently missing — first 10 min has only slides today)
- [ ] Notebook §2 cell — bump `--iterations 2` to `--iterations 5` for a more dramatic Elo climb
- [ ] Recorded **OpenClaw Gateway closer clip** (30–60 sec). Stretch goal — workshop still works without it; the clip is the partnership-branding artifact
- [ ] Pre-workshop setup email sent 48h before, with `make stage-demo` as the success criterion
- [ ] Colab fallback notebook (so attendees with broken local setup still have a runnable path)
- [ ] Dry-run on a fresh laptop with no API key (mock-only path)
- [ ] Dry-run on stage hardware with live MiniMax key
- [ ] Narration rehearsal for the 3–5 minute AutoResearch loop window

## Open Questions

- **Attendee API keys:** do TechEx / MiniMax want to issue temporary keys for the room, or do attendees rely on mock mode? Recommendation: default mock, optional live for attendees with their own keys — avoids "everyone hits rate limits at the same moment" as a stage failure mode.
- **Recording:** is the session recorded? If so, the notebook becomes a permanent reference and should be polished accordingly.
- **Gateway clip engineering bandwidth:** can we get 2–3 days of engineering to stand up the Gateway locally, register the four tools, and record the closer clip? If not, the workshop still delivers — the clip is the visible polish, not the substance.
