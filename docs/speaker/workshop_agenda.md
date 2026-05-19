# TechEx Workshop Agenda — Building AI Coding Agents with OpenClaw and MiniMax

**Format:** 60 minutes | **Capacity:** 40–80 attendees | **Hosts:** MiniMax × AI Valley

This agenda supersedes the 50-minute "Presentation Plan" in `MINIMAX_AUTORESEARCH_CHESS_PRD.md` §19. It is designed as a **hands-on lab, not a talk**: by minute 47 every attendee has run their own AutoResearch loop on their own laptop. The OpenClaw architecture is the teaching frame, MiniMax is the model, and AutoResearch is the headline payoff — distributed across the room, not performed from the stage.

## One-Line Pitch

Three ingredients of a modern coding agent: an architecture, a model, and a loop. OpenClaw gives us the architecture. MiniMax gives us the model. AutoResearch is what happens when you put them inside an eval loop and let the agent improve itself. Today every attendee builds and runs all three.

## Framing Decisions (locked)

- **OpenClaw is in the title and stays there.** The live demo runs an OpenClaw-*compatible* architecture (gateway / context / react / tools as separate layers) rather than the OpenClaw Gateway runtime. The architecture is what teaches the pattern; the Gateway is one deployment of that pattern.
- **The workshop closes with a 30–60 second recorded clip of the actual Gateway running** the same agent with the same tools. That honors the OpenClaw partnership visibly without putting a stateful service on the on-stage critical path.
- **AutoResearch is the cutting-edge headline — but it runs on every attendee's laptop, not just the presenter's.** The wow moment is 80 Elo curves climbing in parallel, not one on a projector.
- **Lab over talk.** ~40 minutes of attendee-hands-on-keyboard, ~20 minutes of framing / spectator / closer. Three explicit checkpoint beats keep the room synchronized.

## Learning Objectives

By the end attendees will have:

1. **Run a MiniMax-powered tool-calling agent on their own laptop** (the floor — 80%+ should clear this).
2. **Modified one tool description and observed the behavior change** (the median — 50%+ should clear this).
3. **Run their own 5-iteration AutoResearch loop and produced their own Elo curve** (the headline — 60%+ should clear this).
4. **Explained the OpenClaw four-layer architecture and read a tool-call trace** (the conceptual takeaway).

## Pre-Workshop Setup (email to attendees ~48 hours before)

Required before arrival:

```bash
git clone https://github.com/nickita-khylkouski/autoresearch-brief-challenge
cd autoresearch-brief-challenge
cp .env.example .env
make setup
make stage-demo   # success criterion — if this prints "READY", you're set
```

Optional (for live MiniMax calls during the workshop):

- Sign up for a MiniMax API key
- Add `MINIMAX_API_KEY=...` to `.env`

Anyone without a key uses mock mode and follows along identically. **Anyone whose local setup fails opens the Colab fallback notebook** (link in the same email) — same lab, no install required.

## 60-Minute Breakdown

The flow is: **punchline → frame → three lab steps with checkpoints → tiered extension → closer.**

| Time | Block | What attendees do |
|---|---|---|
| 0–3 | The punchline | Watch the finished agent |
| 3–8 | Architecture in one slide | See the four-layer frame |
| 8–20 | Lab Step 1–3 — Run the baseline | Run their own agent, read a trace · **Checkpoint 1** |
| 20–32 | Lab Step 4 — Modify one tool | Change a tool description, observe diff · **Checkpoint 2** |
| 32–47 | Lab Step 5 — AutoResearch on your laptop | Run their own 5-iter loop, compare curves · **Checkpoint 3** |
| 47–55 | Tiered extension | Pick beginner / intermediate / advanced |
| 55–58 | OpenClaw Gateway closer clip | Watch the Gateway clip |
| 58–60 | Resources & follow-up | Top-voted questions, links |

### 0–3 min · The punchline (show the finished agent first)

Before any theory, attendees see what they'll build.

- Display `progress.png` from a captured run — the Elo curve climbing 629.6 → 1163.4 → 1276.1.
- Presenter says: *"And one of those climbs came from a single accepted patch — we'll inspect one of yours in 30 minutes."*
- Land the line: *"By minute 47, every one of you will have a curve like this from your own laptop."*

### 3–8 min · Architecture in one slide

One slide, one frame. No deep dives.

- **OpenClaw four layers ↔ four files in `autoresearch_chess/agent/`:** Gateway → `gateway.py`, Context → `context.py`, ReAct → `react.py`, Tools → `tools.py`.
- **One sentence on MiniMax:** "We picked MiniMax because the loop only compounds if the model can tool-call reliably under JSON-schema constraints — you'll feel why in 25 minutes."
- **Tell attendees to pair with their neighbor.** Debugging in pairs at 80 people scales 2× with zero overhead.

### 8–20 min · Run the baseline · Lab Step 1–3

Attendees run their own agent end-to-end inside the workshop notebook. Presenter mirrors on stage.

1. Set the API key in Colab Secrets (or stay in mock mode — no behavior difference for the lab).
2. Run the §2 cell — `run_loop(iterations=1)` triggers one full agent iteration.
3. Run the next cell — it reads `iterations/001/agent_trace.jsonl` and prints the agent's reasoning + tool calls together.

**Checkpoint 1 (~min 18):** *"Thumbs up if your first tool call printed."* TAs converge on red hands. Pairs help neighbors. If >20% of the room is stuck, presenter pauses and announces the Colab fallback.

**Notebook cell:** §2 — "Lab Step 1–3 — Run the baseline" in `notebooks/workshop_colab.ipynb`

### 20–32 min · Modify one tool · Lab Step 4

Attendees touch the agent's behavior directly. Small change, observable effect.

1. In the §3 cell, pick a tool from the dropdown and type a new (weaker or stronger) description — e.g., make `propose_patch`'s description vague: *"does something to the file"*. The cell rewrites the description in memory (no file editing needed in Colab).
2. The cell prints before/after JSON — the exact tool schema MiniMax receives.
3. Run the re-run cell, read the trace, diff the behavior with the person next to you.

**Checkpoint 2 (~min 30):** *"Thumbs up if you modified a tool description and saw the schema diff above."*

This is where the MiniMax tool-calling story lands experientially: attendees see firsthand that tool descriptions shape behavior. No promotional framing required.

**Notebook cell:** §3 — "Lab Step 4 — Modify a tool, see the schema change"

### 32–47 min · AutoResearch on your laptop · Lab Step 5 (the headline)

This is the cutting-edge moment — and it runs on 80 laptops in parallel.

1. Each attendee runs the §4 cell (`iterations=5` slider) in the notebook. Takes ~3–5 minutes.
2. While the loop runs, the presenter's notebook runs the same cell on the projector as a **leader curve** — gives the room a synchronized reference.
3. Presenter narrates AutoResearch principles during the wait:
   - **AutoResearch = agent + objective eval + constrained edit surface + accept/reject**
   - The eval is the only thing the agent cannot fake
   - Bad ideas are cheap; good ideas compound
   - This is a miniature of how MiniMax-style self-improvement loops work in production
4. When done: the next cell displays your `progress.png` inline. Compare your Elo with your neighbor's. The cell after that inspects one accepted patch and one rejected patch.

**Checkpoint 3 (~min 46):** *"Hands up if your Elo went up. Up if it went down."* Both are valid — both teach. The variance across the room is itself the lesson.

**Notebook cell:** §4 — "Lab Step 5 — AutoResearch on YOUR laptop" (`iterations=5`)

### 47–55 min · Tiered extension

Three options. Attendees pick one. Beginners succeed; senior engineers stay engaged.

- **Beginner:** Edit the system prompt in `context.py` so the agent explains its patches more clearly. Re-run, observe the difference in trace.
- **Intermediate:** Add a 5th tool (`list_files()` skeleton provided in `notebooks/extensions/`). Wire it through and watch the agent discover it.
- **Advanced:** Modify the accept/reject criterion in `prompt_builder.py` — bias the agent toward a different heuristic (e.g., favor endgame improvements over opening). Compare Elo trajectories.

TAs roam. Attendees who finish early help neighbors.

### 55–58 min · The Closer — OpenClaw Gateway clip

Play the 30–60 second pre-recorded clip showing the same agent, same tools, running through the actual OpenClaw Gateway. Land the line:

> "What you ran on your laptop today was the OpenClaw architecture in-process. Here's the same agent on the actual OpenClaw Gateway. The migration is mechanical — see `docs/openclaw_mapping.md`. This is what production looks like, three days of work from where you are now."

If the clip wasn't recorded in time, drop this segment and lean on `docs/openclaw_mapping.md` verbally — the workshop still delivers.

### 58–60 min · Resources & follow-up (replaces open Q&A)

Open Q&A at 80 people produces three loud voices and 77 silent ones. Instead:

- Show the **questions board** link (Slido or shared doc) attendees have been adding to during the workshop. Presenter answers the top 2–3 voted questions; remaining questions get answered async in the follow-up channel.
- Resources slide: repo URL, Discord/community link, MiniMax credits, where to file PRs.

## Room Setup for 80 Attendees

The agenda assumes the following are in place. Without them the lab structure collapses.

| Resource | Why it matters at 80 |
|---|---|
| **4–5 TAs** (1 per ~15 attendees) | Without them, Checkpoints 1 & 2 have no recovery path. Brief on top-5 setup failures (Python version, M1 vs Intel, missing `.env`, kernel dead, port in use). |
| **Printed one-page lab handout** | The 5 lab steps + expected output + top-3 errors per step. At 80 people, saves more time than any slide. |
| **Colab fallback notebook** (promoted from optional → required) | At 80, ~10% will hit local-setup issues. Colab is their only path to participate. |
| **Pair-up at minute 5** | Turns 1:80 into effective 1:40 with zero overhead. |
| **Questions board** (Slido / shared doc) | Replaces open Q&A. Works at 80; open Q&A does not. |
| **Projector mirror of presenter machine** | During §32–47, the presenter's AutoResearch run is the "leader curve" attendees compare against. |

## Stage-Reliability Plan

| Failure | Mitigation |
|---|---|
| Bad Wi-Fi | `make stage-demo` (mock mode) covers everything except the live segment |
| MiniMax rate limit | Multi-key rotation already in `minimax_client.py`; fall through to mock |
| Live call totally fails | `make replay-best` instantly drops in a captured successful run |
| Attendee local setup broken | Colab fallback (one click, no install) |
| Notebook kernel dies | CLI fallback: `make live-demo` / `make replay-best` from terminal |
| >20% of room stuck at a checkpoint | Presenter pauses, TAs swarm; if not recovered in 3 min, all stuck attendees move to Colab |
| Half the room's AutoResearch loop fails at §32–47 | Presenter's projector loop is the canonical reference; failed attendees compare against it and inspect their trace files for the failure mode (still a teaching moment) |

## Hand-Off Artifacts (what attendees leave with)

- A cloned repo with a working agent **they ran themselves** (not just a presenter demo they watched)
- **Their own** Elo curve from their own AutoResearch run
- One accepted patch they modified or extended
- A full tool-call trace they can step through
- A clear mental model of the OpenClaw four-layer architecture and how to migrate to the real Gateway (`docs/openclaw_mapping.md`)
- Follow-up channel invite for continued questions

## Success Metrics

Concrete, post-event measurable:

- **≥80%** of attendees successfully run the baseline agent (Checkpoint 1)
- **≥50%** modify a tool and re-run (Checkpoint 2)
- **≥60%** complete a 5-iteration AutoResearch run on their own machine (Checkpoint 3)
- **≥15 attendees** join the follow-up channel or open a PR within 1 week

## Dependencies Before Workshop Date

Already landed:

- [x] Issue #1 — tool-calling agent loop
- [x] Issue #2 — OpenClaw-compatible architecture (Option A — architectural seams only)
- [x] Sponsor framing decision — OpenClaw stays in the title; live demo runs the compatible architecture; closer clip shows the Gateway

Still needed before the event (ordered by impact):

- [ ] **Recruit 4–5 TAs** and brief them on top-5 setup failures (highest-impact item — without TAs the lab structure degrades to presenter-led)
- [ ] **Promote Colab fallback from optional → required** — build, test, link in setup email
- [ ] **One-page printed lab handout** (5 steps × expected output × top-3 errors per step)
- [ ] **Questions board** (Slido or shared doc) link prepared, included in setup email
- [ ] Slide 1 — punchline (Elo curve + one accepted-patch clip, no architecture yet)
- [ ] Slide 2 — OpenClaw four-layer architecture mapped to `autoresearch_chess/agent/` files (the single frame slide)
- [ ] Notebook §1 cell — "Run the baseline" (with checkpoint pause built in)
- [ ] Notebook §2 cell — "Modify a tool, watch the trace change"
- [ ] Notebook §3 cell — `--iterations 5`; runs locally on each attendee laptop
- [ ] Notebook `extensions/` folder — beginner / intermediate / advanced skeletons
- [ ] Recorded **OpenClaw Gateway closer clip** (30–60 sec) — partnership-branding artifact
- [ ] Pre-workshop setup email sent 48h before, with `make stage-demo` AND Colab link
- [ ] Dry-run on a fresh laptop with no API key (mock-only path)
- [ ] Dry-run on stage hardware with live MiniMax key
- [ ] Narration rehearsal for the 3–5 minute AutoResearch loop window
- [ ] TA briefing 24h before — walk through top-5 setup failures and the checkpoint script

## Open Questions

- **TA recruitment:** can we get 4–5 helpers (MiniMax staff, AI Valley volunteers, advanced attendees identified in the setup email)? This is the single biggest lever for 80-person reliability. Without TAs, the agenda needs to fall back to a more presenter-led shape.
- **Colab fallback engineering:** is there capacity to build and test the Colab notebook before the event? At 80 people this has graduated from "nice to have" to "blocker."
- **Attendee API keys:** do TechEx / MiniMax want to issue temporary keys for the room? Recommendation: default mock, optional live for attendees with their own keys — avoids "everyone hits rate limits at the same moment" as a stage failure mode.
- **Recording:** is the session recorded? If so, the notebook + lab handout become permanent references and should be polished accordingly.
- **Gateway clip engineering bandwidth:** can we get 2–3 days of engineering to stand up the Gateway locally, register the four tools, and record the closer clip? If not, the workshop still delivers — the clip is the visible polish, not the substance.
