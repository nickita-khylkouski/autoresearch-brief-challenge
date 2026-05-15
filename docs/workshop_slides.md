# Workshop Slide Design — Teaching Goals and Slide Plan

This document describes **what the workshop teaches** and the nine slides that support that teaching. It is paired with the lab notebook at [`notebooks/workshop_colab.ipynb`](../notebooks/workshop_colab.ipynb), which is where the audience actually does the work. The slides exist to frame the lab, not to duplicate it.

The reading order for an instructor preparing this session:

1. **Learning outcomes** — what an attendee should be able to do or believe after sixty minutes.
2. **The conceptual arc** — how the slides and the notebook together produce those outcomes.
3. **The nine slides** — each described as a teaching moment with one concept and one misconception it corrects.
4. **The slide-generation prompt** — paste into any deck-generation tool to produce a draft deck.

---

## Learning outcomes

By the end of the session, an attendee should be able to:

1. **State the AutoResearch pattern in one sentence** — *an agent + a measurable objective + a bounded edit surface + an accept/reject step* — and recognise it across different domains (chess bots, language-model training, build-time optimisation).
2. **Name the four layers of a tool-calling agent** (Gateway, Context, ReAct, Tools) and explain what each layer is responsible for.
3. **Explain why tool descriptions are part of the model's input**, not internal documentation, and predict what changes when one is rewritten.
4. **Describe what an eval-driven loop catches that a single prompt cannot**, and identify the limits of that approach — the entry point to the guardrails discussion.

Every slide and every notebook section is tied back to one of these outcomes. If a slide does not serve one of them, it should not exist.

---

## The conceptual arc

The workshop is structured as a small set of ideas. Each idea is introduced just before the audience experiences it firsthand. The slides do not duplicate experience — they frame it.

| Idea | Where the slide introduces it | Where the notebook makes it real |
|---|---|---|
| **The pattern** — loops with evaluators beat single prompts | Slide 1, Slide 4 | The notebook as a whole is a loop the attendee runs |
| **The architecture** — agents decompose into reusable layers | Slide 2, Slide 3 | Notebook section "How a tool-calling agent is structured" |
| **The interface** — tools are descriptions the model reads | *(no slide; learned directly in the lab)* | Notebook section "Tools are descriptions the model reads" |
| **The compounding** — value comes from many small evals | Slide 5, Slide 6 | Notebook section "The loop — many small evaluations" |
| **The limits** — what a loop cannot guarantee on its own | Slide 7 | Notebook extensions surface this implicitly |

The slides appear at three kinds of moments:

- **Before** an idea becomes real — Slides 1–3 introduce the outcome and the architecture before the attendees write any code.
- **During** a wait window — Slides 4–6 carry the narrative while the audience's five-iteration loops run for three to five minutes.
- **After** the work is done — Slides 7–9 land the limits, the production path, and the take-home.

---

## The nine slides

Each slide is described with three lines: the **concept** it teaches, the **misconception** it corrects, and the one sentence the audience should walk away holding in their head.

### Slide 1 — The outcome, before the explanation

- **Concept:** What you will have at the end of the session.
- **Misconception this corrects:** *AI demos are something I watch the presenter do; this will be the same.*
- **Visual:** A real Elo curve climbing roughly 630 → 1280 across a few iterations — a curve the attendee will reproduce on their own machine.
- **One-line take-away:** *By the end of this session, you will have a chart like this from your own machine — not from the presenter's.*

### Slide 2 — Three ingredients of a modern coding agent

- **Concept:** A working agent system is three independent components, not one.
- **Misconception this corrects:** *An "AI agent" is one indivisible thing.*
- **Body:**

  | Component | What it is | What it gives you |
  |---|---|---|
  | **Architecture** (OpenClaw) | Four reusable layers — Gateway, Context, ReAct, Tools | A blueprint you can implement once and reuse |
  | **Model** (MiniMax) | A model that reliably emits structured tool calls | The primitive the layers compose around |
  | **Loop** (AutoResearch) | Agent + objective evaluator + accept-or-reject | A way to compound small ideas into measurable progress |

- **One-line take-away:** *The architecture, the model, and the loop are three separate decisions you can mix and match.*

### Slide 3 — Four layers, four files

- **Concept:** The architecture is small enough that the entire blueprint fits in four files.
- **Misconception this corrects:** *Agent frameworks are mysterious internals you take on faith.*
- **Body:**

  | Layer | File | Responsibility |
  |---|---|---|
  | **Gateway** | `gateway.py` | Entry point — one in, one out |
  | **Context** | `context.py` | Assembles the conversation the model sees |
  | **ReAct** | `react.py` | Drives the model–tool–model–tool cycle until a stop condition |
  | **Tools** | `tools.py` | The five functions the model is allowed to call |

- **One-line take-away:** *You can read the entire agent in four files. There is no missing piece.*

### Slide 4 — Why loops beat one-shots *(narrate during the wait window)*

- **Concept:** A loop is *qualitatively* different from a single inference, not just *quantitatively* bigger.
- **Misconception this corrects:** *A loop is just "run it more times until you get a good answer."*
- **Body:**

  | One-shot agent | Research loop |
  |---|---|
  | Guesses once | Tries, scores, learns, tries again |
  | Wrong guess ends the run | Each failure narrows the next attempt |
  | Cannot inspect the code it tests | Reads the code, understands what it does |
  | Cannot change the experiment itself | Can rewrite its own scaffolding |

- **One-line take-away:** *A loop is not "more chances"; it is a feedback channel from reality back into the model.*

### Slide 5 — The metric is the load-bearing decision

- **Concept:** Everything else in the loop is downstream of the metric.
- **Misconception this corrects:** *The model is the important part; the eval is plumbing.*
- **Body:** Centre the literal `estimated_elo`. Four supporting claims:
  - Runs without human judgement.
  - Reproducible — the same patch always scores the same.
  - A number, not an opinion.
  - The model can fake everything else about a patch — explanation, commit message, prose. It cannot fake this.
- **One-line take-away:** *The quality of your metric determines the ceiling of your loop. Pick it deliberately.*

### Slide 6 — The same pattern, at frontier scale

- **Concept:** What runs on the attendee's laptop is the small version of what MiniMax reports running on M2.7 during training.
- **Misconception this corrects:** *Self-improving AI is a futuristic claim, not a real engineering practice.*
- **Body:** Six-step horizontal pipeline — *Analyse failures → Build new skills → Modify scaffolding → Run evals → Update memory → Keep or revert.* Two reported figures: **+30%** on MiniMax's internal coding-agent eval, **100+** self-improvement rounds during training. *Footer:* self-reported by MiniMax; verify before citing externally.
- **One-line take-away:** *Your edit surface is four files. Theirs is the model's own scaffolding. The pattern is the same.*

### Slide 7 — Can you do this at work? Six failure modes, six mitigations

- **Concept:** Loops without guardrails optimise the wrong thing, sometimes silently.
- **Misconception this corrects:** *Once I have a metric, I am done thinking about correctness.*
- **Body:**

  | What goes wrong | How to prevent it |
  |---|---|
  | Metric gaming — the score moves, the thing doesn't | Track multiple metrics; wins must not regress others |
  | Overfitting — short-run wins that don't last | Hard gates with minimum-threshold checks |
  | Hidden regressions — primary up, something else quietly breaks | Secondary metrics in CI |
  | Compute runaway — loop never stops | Budgets on runs and on spend |
  | Broad permissions — agent touches what it shouldn't | Constrain the edit surface; isolate the branch |
  | Secret leakage — credentials visible to the agent | Strip secrets from the agent's environment |

- **One-line take-away:** *The loop optimises whatever you measure — even if you measured wrong. Guardrails are part of the design, not an afterthought.*

### Slide 8 — Same agent, production runtime *(optional video)*

- **Concept:** The architecture the audience ran in-process today is the same architecture that deploys behind a service boundary.
- **Misconception this corrects:** *Notebook code and production code are different worlds.*
- **Body:** A 30–60 second clip of the same agent on the OpenClaw Gateway. If the clip is not recorded, omit this slide and refer to the migration guide verbally — the take-away still lands.
- **One-line take-away:** *The seam between "what you ran today" and "what production looks like" is a deployment step, not a rewrite.*

### Slide 9 — Take this home

- **Concept:** The lab is the start, not the end.
- **Misconception this corrects:** *Workshops are a one-shot experience that ends when you leave the room.*
- **Body:** Repository URL, migration guide, the companion conceptual deck (`Auto Research.pptx`), follow-up channel, MiniMax credits, questions board for written follow-up.
- **One-line take-away:** *Everything you ran is yours to keep, modify, and extend.*

---

## What the slides deliberately do not do

A teacher should not tell the audience what they have already experienced. The slides exist to introduce ideas just before they become real and to provide framing during attendee-driven work. The slides specifically do **not**:

- Explain how tool calling works internally — the audience sees it directly in the lab.
- Walk through the five tools — the notebook prints them.
- Show example diffs — the audience inspects their own.

If a slide repeats what the notebook already does experientially, cut it.

---

# Slide-generation prompt

Paste from `---BEGIN PROMPT---` to `---END PROMPT---` into any deck-generation tool (Gamma, Canva, Claude, GPT) to produce a draft deck.

---BEGIN PROMPT---

You are generating a nine-slide deck for a sixty-minute hands-on workshop titled *"Building AI Coding Agents with OpenClaw and MiniMax."* The audience is forty to eighty software engineers at a developer conference. The session is a lab, not a talk: the audience spends roughly two-thirds of the time typing in a notebook. Your deck supplies framing, not content the lab already delivers.

**Pedagogical constraints:**
- Each slide carries one concept and corrects one misconception.
- Slides never duplicate what the lab demonstrates experientially.
- Slides never mention logistics (time markers, hand-raising, pair-up, room layout).
- No promotional language. Tool capabilities are demonstrated by the lab, not claimed by slides.
- File paths, function names, and numerical figures are quoted exactly. Do not paraphrase technical content.

**Visual style:**
- Clean and technical. Legible from the back of an eighty-person room (body text at least 28 pt).
- Two-column tables where ideas contrast.
- One large central element where one number or one term should dominate.
- Horizontal pipeline diagrams for sequential processes.

**Generate exactly the following nine slides, in this order:**

**Slide 1 — The outcome**
- Title: *By the end of this session, you will have a chart like this from your own machine.*
- Visual: an Elo curve climbing from roughly 630 to roughly 1280 over a small number of iterations.
- No other body text.

**Slide 2 — Three ingredients**
- Title: *Architecture · Model · Loop*
- Three-row table:

  | Ingredient | Project | What it gives you |
  |---|---|---|
  | Architecture | OpenClaw | Four-layer pattern: Gateway · Context · ReAct · Tools |
  | Model | MiniMax | A model that emits reliable structured tool calls |
  | Loop | AutoResearch | Agent + objective evaluator + accept-or-reject |

**Slide 3 — Four layers, four files**
- Title: *The architecture, on disk, in your cloned repo*
- Table mapping each layer to its file in `autoresearch_chess/agent/`:

  | Layer | File | What the lab uses |
  |---|---|---|
  | Gateway | `gateway.py` | `ChessAgent.run_iteration` |
  | Context | `context.py` | `build_initial_conversation` |
  | ReAct | `react.py` | `run_react_loop` |
  | Tools | `tools.py` | `TOOLS` (five tools) |

- Footer: *"The architecture is what teaches the pattern. The Gateway is one deployment of that pattern."*

**Slide 4 — Why loops beat one-shots**
- Title: *One-shot agents guess. Research loops let reality correct them.*
- Two-column comparison:

  | One-shot agent | Research loop |
  |---|---|
  | Guesses once | Tries, scores, learns, retries |
  | Wrong guess ends the run | Each failure teaches the next attempt |
  | Cannot read the code it tests | Reads the code, understands what it does |
  | Cannot change the experiment | Can rewrite the experiment's own structure |

- Footer: *"Right now, on your laptop, the agent is doing the right column."*

**Slide 5 — The metric is the load-bearing decision**
- Title: *The quality of your metric determines the quality of the loop.*
- Large central element: the literal term `estimated_elo` rendered in monospace, with caption *"one number from one script, not a debate."*
- Four short bullets:
  - Fully automatic — no human judgement needed.
  - Reproducible — the same patch always scores the same.
  - Hard to argue with — a number, not an opinion.
  - The agent can fake everything else; it cannot fake this.

**Slide 6 — MiniMax M2.7: same pattern, frontier scale**
- Title: *Your laptop loop is a miniature of MiniMax's M2.7 self-evolution loop.*
- Horizontal pipeline (six boxes connected by arrows): *Analyse failures → Build new skills → Modify scaffolding → Run evals → Update memory → Keep or revert.*
- Two stat callouts:
  - **+30%** on MiniMax's internal coding-agent eval.
  - **100+** self-improvement rounds, no model retraining.
- Footer: *"Self-reported by MiniMax. Training-time scaffolding search, frozen into the released checkpoint."*

**Slide 7 — Six failure modes, six mitigations**
- Title: *Can you do this at work?*
- Two-column table:

  | What goes wrong | How to prevent it |
  |---|---|
  | Metric gaming — score moves, the thing doesn't | Track multiple metrics; wins must not regress others |
  | Overfitting — short-run wins that don't last | Hard gates with minimum-threshold checks |
  | Hidden regressions — something quietly breaks | Secondary metrics in CI |
  | Compute runaway — loop never stops | Budgets on runs and on spend |
  | Broad permissions — agent touches what it shouldn't | Constrain the edit surface; isolate the branch |
  | Secret leakage — credentials visible to the agent | Strip secrets from the agent's environment |

- Footer: *"The loop optimises whatever you measure. Build guardrails on day one."*

**Slide 8 — Same agent, production runtime *(video slot, optional)***
- Title: *Same agent. Same five tools. Production runtime.*
- Body: large placeholder for a 30–60 second clip.
- One quote underneath:

  > "What you ran on your laptop today was the OpenClaw architecture in-process. Here is the same agent on the OpenClaw Gateway. The migration is mechanical — three days of work from where you are now."

**Slide 9 — Take this home**
- Title: *Yours to keep, modify, and extend.*
- Link list:
  - Repository: `github.com/nickita-khylkouski/autoresearch-brief-challenge`
  - OpenClaw migration guide: `docs/openclaw_mapping.md`
  - Conceptual companion deck: `Auto Research.pptx`
  - Follow-up channel: *(placeholder)*
  - MiniMax credits: *(placeholder)*
  - Questions board: *(placeholder)*

**Output:** nine slides, in the order above, each with a clear title and the specified body. No agenda slide. No thank-you slide. No additional content.

---END PROMPT---
