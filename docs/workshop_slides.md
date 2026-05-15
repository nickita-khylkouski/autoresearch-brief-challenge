# Workshop Slide Spec & Presenter Runbook

Companion to [`WORKSHOP_AGENDA.md`](../WORKSHOP_AGENDA.md) and [`notebooks/workshop_colab.ipynb`](../notebooks/workshop_colab.ipynb).

This doc defines:
1. The **9 slides** the workshop needs (no more, no less — the notebook IS the lab).
2. **Exactly when** each slide is shown, what the presenter says, and which notebook cell the room is on.
3. The **slide-generation prompt** at the bottom — paste into Gamma / Canva / Claude / GPT to produce the deck.

## Slide ↔ Agenda ↔ Notebook map

| # | Slide title | When (min) | Agenda section | Notebook cell |
|---|---|---|---|---|
| 1 | The Punchline — Your Target Curve | 0–3 | §"The punchline" | `41f2ce9c` + `c5ede446` (§0) |
| 2 | Three Ingredients · Architecture · Model · Loop | 3–5 | §"Architecture in one slide" | `ffdecbf0` (§1) |
| 3 | OpenClaw Four Layers ↔ Four Files | 5–8 | §"Architecture in one slide" | `ffdecbf0` + `3c6e90fa` (§1) |
| 4 | Why Loops Beat One-Shots *(§4 wait #1)* | ~35 | §"AutoResearch on your laptop" wait window | `295f3755` (§4) running in background |
| 5 | The Eval Is The Only Thing The Agent Can't Fake *(§4 wait #2)* | ~38 | same | same |
| 6 | MiniMax M2.7 — Same Loop, Frontier Scale *(§4 wait #3)* | ~41 | same | same |
| 7 | Guardrails — Can You Do This At Work? | 55–58 | §"The Closer" | `2311605f` (§6) |
| 8 | OpenClaw Gateway Closer Clip *(video slot, not a slide)* | 56–58 | same | same |
| 9 | Resources & Follow-Up | 58–60 | §"Resources & follow-up" | `324c06a9` (§7) |

**Optional adds** (use if room/timing allows):
- Checkpoint cards ×3 (visual cue at minutes 18, 30, 46 — could be projector overlays instead of deck slides)
- A pair-up reminder slide at minute 5

---

## Slide 1 — The Punchline

**When:** 0–3 min · **Notebook:** §0 (the captured Elo curve renders inline)

**Headline:** *By minute 47, you will have a curve like this from your own laptop.*

**Body (in the room sees):**
- Image: `artifacts/demo_replay/progress.png` (Elo curve climbing 629.6 → 1163.4 → 1276.1)
- Subhead: **5 iterations · 1 accepted patch climbed it most · ~3 minutes runtime**

**Presenter says:**
> "Before we explain anything, here's what every one of you will produce. This curve came from a captured run. One of those climbs came from a single accepted patch — we'll inspect one of yours in 30 minutes."

**Why this slide exists:** Anchors the target before any theory. Attendees sit through framing more patiently when they've seen the payoff.

---

## Slide 2 — Three Ingredients

**When:** 3–5 min · **Notebook:** §1

**Headline:** *Architecture · Model · Loop*

**Body (three-column table):**

| Ingredient | Project | What it gives us |
|---|---|---|
| Architecture | **OpenClaw** | Four-layer pattern: Gateway · Context · ReAct · Tools |
| Model | **MiniMax** | A model that tool-calls reliably under JSON-schema |
| Loop | **AutoResearch** | Agent + objective eval + constrained surface + accept/reject |

**Presenter says:**
> "Three ingredients of a modern coding agent. OpenClaw is how you structure the agent. MiniMax is the model inside it. AutoResearch is what happens when you put them in a loop with an eval. Today you build all three."

---

## Slide 3 — OpenClaw Four Layers ↔ Four Files

**When:** 5–8 min · **Notebook:** §1 cell `3c6e90fa` is what they see in the notebook

**Headline:** *The architecture, on disk, in your cloned repo*

**Body (two columns, file → role):**

| OpenClaw layer | File in `autoresearch_chess/agent/` | What the lab uses |
|---|---|---|
| Gateway (entry point) | `gateway.py` | `ChessAgent.run_iteration` |
| Context assembly | `context.py` | `build_initial_conversation` |
| ReAct runtime | `react.py` | `run_react_loop` |
| Tool layer | `tools.py` | `TOOLS` (5 tools) |

**Footer:** *"The architecture is what teaches the pattern. The Gateway is one deployment of that pattern — clip at minute 56."*

**Presenter says:**
> "Four layers, four files. You can read the entire OpenClaw architecture by opening four files in your cloned repo. Now pair up with your neighbor — at 80 people, two-person debugging scales 2× with zero overhead."

---

## Slide 4 — Why Loops Beat One-Shots *(§4 wait window, ~minute 35)*

**When:** ~35 min · **Notebook:** Lab Step 5 cell `295f3755` is running on attendee laptops; presenter narrates over the wait

**Headline:** *One-shot agents guess. Research loops let reality correct them.*

**Body (two-column comparison):**

| One-shot agent | Research loop |
|---|---|
| Guesses once | Tries, scores, learns, retries |
| If the guess is wrong, the loop ends | Each failed attempt teaches what not to try |
| Cannot read the code it tests | Reads the code, understands what it does |
| Cannot change the experiment | Can rewrite the experiment's own structure |

**Footer:** *"Right now, on your laptop, the agent is doing the right column."*

**Presenter says:**
> "While your loops run, here's why this works. Random search samples settings. AutoResearch reads the code, changes mechanisms, and learns from each failed attempt. The five-minute Elo eval on your machine is doing the same job that val_bpb does in Karpathy's reference repo."

**Adapted from:** Auto Research.pptx slides 12 + 13.

---

## Slide 5 — The Eval Is The Only Thing The Agent Can't Fake *(§4 wait window, ~minute 38)*

**When:** ~38 min · **Notebook:** §4 still running

**Headline:** *The quality of your metric determines the quality of the loop.*

**Body (large central number with annotations):**
- Big: `estimated_elo`
- Caption: *one number from one script, not a debate*
- Below: four short callouts
  - Fully automatic — no human judgment needed
  - Reproducible — same patch always scores the same
  - Hard to argue with — it's a number, not an opinion
  - The agent can fake everything else; it cannot fake this

**Presenter says:**
> "The single most important AutoResearch principle. The eval is the only thing the agent cannot fake. A patch can have a great-looking explanation, perfect commit message, beautiful diff — if it doesn't move the Elo, it gets rejected. Bad ideas are cheap. Good ideas compound."

**Adapted from:** Auto Research.pptx slide 8 (val_bpb → estimated_elo).

---

## Slide 6 — MiniMax M2.7 · Same Loop, Frontier Scale *(§4 wait window, ~minute 41)*

**When:** ~41 min · **Notebook:** §4 may be finishing

**Headline:** *The loop on your laptop is a miniature of MiniMax M2.7's self-evolution loop.*

**Body (six-step pipeline as a horizontal flow):**

`Analyze failures → Build new skills → Modify scaffolding → Run evals → Update memory → Keep or revert`

**Stat callout:**
- **+30%** on MiniMax's internal coding-agent eval
- **100+** self-improvement rounds, no model retraining
- Footnote: *Self-reported by MiniMax · training-time scaffolding search, frozen into the released checkpoint*

**Presenter says:**
> "What you're running now is the same five-step loop MiniMax reports running on itself during training. Your edit surface is four files; theirs is the model's own scaffolding. Your eval is Elo; theirs is internal coding-agent benchmarks. Same pattern, bigger box."

**Adapted from:** Auto Research.pptx slides 19 + 20.

---

## Slide 7 — Guardrails · Can You Do This At Work?

**When:** 55–58 min · **Notebook:** §6 closer

**Headline:** *Six failure modes, six mitigations*

**Body (two-column table):**

| What can go wrong | How to prevent it |
|---|---|
| Metric gaming — agent optimizes the score without improving the thing | Track multiple metrics; wins must not regress others |
| Overfitting — short-run wins that don't hold up | Hard gates: minimum-threshold checks block bad merges |
| Hidden regressions — primary metric up, something else quietly breaks | Secondary metrics in CI |
| Compute runaway — loop runs forever, burns budget | Budgets: max runs, max spend, automatic stop |
| Broad permissions — agent touches files it shouldn't | Constrained edit surface; isolated branches |
| Secret leakage — credentials visible to the agent | Strip secrets from the agent's environment |

**Footer:** *"The loop optimizes whatever you measure. Build guardrails on day one."*

**Presenter says:**
> "Every one of you is going to think 'can I do this at work?' Here's the honest answer. Six things go wrong, six fixes. Pick the metric carefully. Ship guardrails on day one. The loop optimizes whatever you measure — even if you measured wrong."

**Adapted from:** Auto Research.pptx slides 29 + 30 merged.

---

## Slide 8 — OpenClaw Gateway Closer Clip *(video, not a slide)*

**When:** 56–58 min · **Notebook:** §6 closer

**What plays:** 30–60 second pre-recorded clip — the same agent, same five tools, running through the actual OpenClaw Gateway.

**Presenter line (over the clip):**
> "What you ran on your laptop today was the OpenClaw architecture in-process. Here's the same agent on the actual OpenClaw Gateway. The migration is mechanical — see `docs/openclaw_mapping.md`. This is what production looks like, three days of work from where you are now."

**Fallback if clip not ready:** Drop this segment; lean on `docs/openclaw_mapping.md` verbally. The workshop still delivers.

---

## Slide 9 — Resources & Follow-Up

**When:** 58–60 min · **Notebook:** §7

**Headline:** *Take this home.*

**Body (link list):**
- 📂 **Repo:** `github.com/nickita-khylkouski/autoresearch-brief-challenge`
- 📖 **OpenClaw migration guide:** `docs/openclaw_mapping.md`
- 📊 **Conceptual companion deck:** `Auto Research.pptx` — Karpathy origin, MiniMax M2.7 case study, Ralph loops, Codex `/goal`, guardrails
- 💬 **Follow-up channel:** *[Slack/Discord link from setup email]*
- 🎁 **MiniMax credits:** *[link from setup email]*
- ❓ **Questions board:** *[Slido / shared doc — top-voted questions answered now]*

**Presenter answers the top 2–3 voted questions from the board.** Everything else goes async.

---

## Things that need to be in place before the workshop (slide-related)

These are the items from `WORKSHOP_AGENDA.md` §"Dependencies" that this slide spec depends on. Tick them off before dry-run:

- [ ] Slide 1 punchline — `artifacts/demo_replay/progress.png` rendered crisply at projector resolution
- [ ] Slide 3 architecture diagram — file paths verified against current `autoresearch_chess/agent/` layout
- [ ] Slides 4–6 (§4 wait narration) — presenter has rehearsed the 3–5 min narration so it lands while the room's loops are running
- [ ] Slide 8 — Gateway closer clip recorded (or this segment dropped from the runbook)
- [ ] Slide 9 — follow-up channel link, questions board URL, MiniMax credits link all populated
- [ ] All slides — readable from the back row at 80-person capacity (font size ≥28pt for body)
- [ ] Dry-run with someone who hasn't seen the agenda — they should be able to follow which minute we're on from the slides alone

---

## Notebook-side items the slides assume work

The slides reference specific notebook outputs. Verify these still produce the expected result:

- [ ] §0 cell `c5ede446` displays the captured `progress.png` cleanly
- [ ] §1 cell `3c6e90fa` prints the 5 tools, signatures of all four layers
- [ ] §2 cell `c69e55ba` completes one iteration in under 60s in mock mode
- [ ] §2 cell `25f736c6` prints a 3-round trace (`list_bot_files → read_bot_file → propose_patch`) in mock mode
- [ ] §3 cell `72f581ab` shows a visible JSON-schema diff before/after
- [ ] §4 cell `295f3755` completes 5 iterations in 3–5 minutes in mock mode
- [ ] §4 cell `deebef0f` renders a `progress.png` curve that climbs in mock mode
- [ ] §5 all three extensions (beginner / intermediate / advanced) succeed without errors
- [ ] §6 closer markdown renders correctly (clip slot is plain text)
- [ ] §7 archive cell `56d18800` produces a downloadable zip in Colab
- [ ] Stage-reliability `replay` cell `e29ec9a2` works as a fallback

---

# Slide-Generation Prompt (paste into Gamma / Canva / Claude / GPT)

The text below is self-contained — copy from `---BEGIN PROMPT---` to `---END PROMPT---` and paste into any slide generation tool.

---BEGIN PROMPT---

You are generating a **9-slide presentation deck** for a 60-minute hands-on technical workshop titled **"Building AI Coding Agents with OpenClaw and MiniMax."** Hosts: MiniMax × AI Valley. Audience: 40–80 software engineers, mixed seniority, at the TechEx conference.

**Critical framing constraints:**
- The workshop is a **hands-on lab, not a talk** — attendees spend ~40 of 60 minutes typing in a Colab notebook. Slides only carry framing material at specific moments. Do not pad.
- **No marketing language.** Tool descriptions and MiniMax capabilities are demonstrated experientially in the lab; slides state facts, not pitches.
- **One core idea per slide.** Maximum 5 bullets per slide.
- **Use the exact file paths, function names, and numbers** in this brief. Do not paraphrase technical content.

**Visual style:**
- Clean, technical, suitable for an 80-person room (body text ≥28pt).
- Dark theme acceptable.
- Borrow visual language from technical decks: large stat callouts, monospace code where shown, two-column comparison tables, horizontal pipeline flows.

**Generate exactly these 9 slides:**

---

**SLIDE 1 — The Punchline**
- Title: *By minute 47, you will have a curve like this from your own laptop*
- Visual: a chess-bot Elo curve climbing from ~630 to ~1280 over 5 iterations (placeholder line chart if no image)
- Subhead: **5 iterations · 1 accepted patch climbed it most · ~3 minutes runtime**
- No other body text

---

**SLIDE 2 — Three Ingredients**
- Title: *Architecture · Model · Loop*
- Three-column table:
  | Ingredient | Project | What it gives us |
  |---|---|---|
  | Architecture | OpenClaw | Four-layer pattern: Gateway · Context · ReAct · Tools |
  | Model | MiniMax | A model that tool-calls reliably under JSON-schema |
  | Loop | AutoResearch | Agent + objective eval + constrained surface + accept/reject |

---

**SLIDE 3 — OpenClaw Four Layers ↔ Four Files**
- Title: *The architecture, on disk, in your cloned repo*
- Table mapping layer → file (all files in `autoresearch_chess/agent/`):
  | Layer | File | What the lab uses |
  |---|---|---|
  | Gateway | `gateway.py` | `ChessAgent.run_iteration` |
  | Context | `context.py` | `build_initial_conversation` |
  | ReAct | `react.py` | `run_react_loop` |
  | Tools | `tools.py` | `TOOLS` (5 tools) |
- Footer line: *"The architecture is what teaches the pattern. The Gateway is one deployment — clip at minute 56."*

---

**SLIDE 4 — Why Loops Beat One-Shots**
- Title: *One-shot agents guess. Research loops let reality correct them.*
- Two-column comparison:
  | One-shot agent | Research loop |
  |---|---|
  | Guesses once | Tries, scores, learns, retries |
  | If wrong, the loop ends | Each failure teaches what not to try |
  | Cannot read the code it tests | Reads the code, understands what it does |
  | Cannot change the experiment | Can rewrite the experiment's structure |
- Footer: *"Right now, on your laptop, the agent is doing the right column."*

---

**SLIDE 5 — The Eval Is The Only Thing The Agent Can't Fake**
- Title: *The quality of your metric determines the quality of the loop*
- Large central element: the words `estimated_elo` rendered as a big monospace label, with caption *"one number from one script, not a debate"*
- Four short bullets below the central element:
  - Fully automatic — no human judgment needed
  - Reproducible — same patch always scores the same
  - Hard to argue with — it's a number, not an opinion
  - The agent can fake everything else; it cannot fake this

---

**SLIDE 6 — MiniMax M2.7 · Same Loop, Frontier Scale**
- Title: *The loop on your laptop is a miniature of MiniMax M2.7's self-evolution loop*
- Horizontal pipeline (six boxes connected by arrows):
  `Analyze failures → Build new skills → Modify scaffolding → Run evals → Update memory → Keep or revert`
- Two stat callouts to the right:
  - **+30%** on MiniMax's internal coding-agent eval
  - **100+** self-improvement rounds, no model retraining
- Small footer: *Self-reported by MiniMax. Training-time scaffolding search, frozen into the released checkpoint.*

---

**SLIDE 7 — Guardrails · Can You Do This At Work?**
- Title: *Six failure modes, six mitigations*
- Two-column table:
  | What can go wrong | How to prevent it |
  |---|---|
  | Metric gaming — agent optimizes the score, not the thing | Track multiple metrics; wins must not regress others |
  | Overfitting — short-run wins that don't hold up | Hard gates: minimum-threshold checks |
  | Hidden regressions — something quietly breaks | Secondary metrics in CI |
  | Compute runaway — loop runs forever | Budgets: max runs, max spend |
  | Broad permissions — agent touches files it shouldn't | Constrained edit surface; isolated branches |
  | Secret leakage — credentials visible to the agent | Strip secrets from agent's environment |
- Footer: *"The loop optimizes whatever you measure. Build guardrails on day one."*

---

**SLIDE 8 — OpenClaw Gateway Closer (video slot)**
- Title: *Same agent. Same five tools. Production runtime.*
- Body: large placeholder for a 30–60 second video clip
- One quote underneath:
  > "What you ran on your laptop was the OpenClaw architecture in-process. Here's the same agent on the OpenClaw Gateway. The migration is mechanical — `docs/openclaw_mapping.md`. Three days of work from where you are now."

---

**SLIDE 9 — Resources & Follow-Up**
- Title: *Take this home*
- Link list:
  - 📂 Repo: `github.com/nickita-khylkouski/autoresearch-brief-challenge`
  - 📖 OpenClaw migration guide: `docs/openclaw_mapping.md`
  - 📊 Conceptual companion deck: `Auto Research.pptx`
  - 💬 Follow-up channel: *(placeholder — add link)*
  - 🎁 MiniMax credits: *(placeholder — add link)*
  - ❓ Questions board: *(placeholder — add link)*

---

**Output format:** 9 slides, in the order above, each with a clear title and the specified body. No additional slides, no agenda slide, no thank-you slide.

---END PROMPT---
