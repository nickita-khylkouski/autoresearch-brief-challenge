# Workshop Curriculum and Slide Plan

This document describes **the curriculum** — the specific things the workshop teaches — and the fifteen slides that frame each one. It is paired with the lab notebook at [`notebooks/workshop_colab.ipynb`](../notebooks/workshop_colab.ipynb), which is where each claim becomes real. The slides exist to set the audience up for the lab and to make explicit what they have just lived through.

Reading order for an instructor:

1. **The curriculum** — the specific claims the workshop transmits. This is the heart of the document.
2. **How the slides and the lab divide the work** — what each medium teaches and what each cannot.
3. **The fifteen slides** — specs for each, kept as a supporting reference.
4. **The slide-generation prompt** — paste into any deck tool to produce a draft.

---

## The curriculum — what the workshop actually teaches

The workshop transmits **four core takeaways** the audience must be able to state in their own words next week, and **six supporting claims** that frame the takeaways with context, contrast, and constraint. Every slide and every lab section is in service of one of these ten claims; anything that serves none of them is cut.

### Four core takeaways

**1. The pattern, in one sentence.**
*An agent + a measurable objective + a bounded edit surface + an accept-or-reject step.* Take any one away and the loop stops working. The whole workshop is a working demonstration of this sentence — every other claim is in service of it. Karpathy uses it for language-model training; MiniMax reports running it on M2.7 during training; Shopify applies it to build-time optimisation. Same shape, many domains.
*Carried by:* Slides 3, 6, 7 · Lab section "The loop — many small evaluations, not one large prompt."

**2. The architecture of a tool-calling agent, in four files.**
A tool-calling agent is not one piece of software. It decomposes into four reusable layers — *Gateway, Context, ReAct, Tools* — each with one responsibility. The entire blueprint reads in an afternoon and is portable across deployments.
*Carried by:* Slide 4 · Lab section "How a tool-calling agent is structured."

**3. Tool descriptions are part of the model's prompt, not internal documentation.**
From the model's perspective, each tool is a JSON object whose `description` field is concatenated into the conversation. Rewriting that field is rewriting the prompt. This is the lever you actually pull to steer a tool-calling agent — and it is invisible until you see the before/after schema.
*Carried by:* Slide 5 (announced); Lab section "Tools are descriptions the model reads."

**4. The loop optimises whatever you measure — even if you measured wrong.**
This is the load-bearing safety claim. Loops without guardrails optimise the wrong thing, sometimes silently. The metric you pick determines the *ceiling* of your loop; the guardrails you ship determine whether the ceiling is the right one. Six failure modes (metric gaming, overfitting, hidden regressions, compute runaway, broad permissions, secret leakage) each have a mitigation. Guardrails are part of the design, not an afterthought.
*Carried by:* Slide 9 · Reinforced implicitly in lab extensions.

### Six supporting claims

**A. Iteration speed is the bottleneck, not ideas.**
A research engineer runs three to five experiments a day; an overnight loop runs a hundred. The slow part is the mechanical work between thoughts — and it is automatable. Automate it, and thinking compounds.
*Carried by:* Slide 2 (the outcome makes this concrete); narrated over Slide 6 during the wait window.

**B. A loop is qualitatively different from a single prompt.**
A one-shot agent has to be right on the first try; a wrong guess ends the run. A loop lets reality correct each attempt through evidence. *This is the difference between a chatbot and an engineering system.*
*Carried by:* Slide 6.

**C. A loop is also qualitatively different from random search.**
The agent reads the code, changes *mechanisms* (not just settings), debugs failures, and can rewrite the experiment's own structure. The loop converges; it does not just sample.
*Carried by:* Slide 6 (companion to claim B).

**D. The agent gets power from being boxed in.**
A narrow edit surface is not a limitation — it is the property that makes the agent's work cheap to evaluate and safe to merge. Constraint enables compounding. The chess agent edits four files; the rest of the repository is read-only.
*Carried by:* Slide 4 · Lab §3 (the `EDITABLE_FILES` constraint shows up directly in `propose_patch`).

**E. The same pattern transfers to wherever you have an automatic metric.**
Karpathy's val_bpb. MiniMax's internal coding-agent eval. Shopify's build-time benchmarks. The chess bot's estimated Elo. The pattern is metric-shaped; the metric is what specialises it to a domain.
*Carried by:* Slide 8 · Lab take-home.

**F. The human role shifts to *choose, constrain, judge*.**
Pick the metric. Define the boundary. Approve the winners. The human does not handle each iteration; the human decides what *winning* means in the first place. Loop designers beat prompt engineers.
*Carried by:* Slide 9 footer (paired with the guardrails frame); Slide 13 recap; Slide 14 take-home.

---

## How the slides and the lab divide the work

A useful rule when deciding whether something belongs on a slide or in the notebook: **slides teach the concept; the lab teaches the mechanics.** If the audience can verify it by running a cell, it does not belong on a slide.

| Medium | What it teaches | What it cannot teach |
|---|---|---|
| **Slides** | The pattern in the abstract; the architecture as a blueprint; what to do at work; the limits | What it *feels like* to read a trace, watch a curve climb, or rewrite a tool description and see the JSON change |
| **The lab** | The mechanics; the trace structure; how a tool-call schema is actually shaped; what an accepted patch looks like; what the eval is doing | Why this pattern matters beyond chess; how it generalises; what fails when it goes to production |

This is why the session is ~40 minutes lab and ~20 minutes slides. The split is not arbitrary: the slides cover what *cannot* be taught by running a cell, and stay out of the way otherwise.

**When each slide appears:**

- **Before code runs** — Slides 1–5 set the frame, the outcome, the architecture, and the hands-on plan.
- **During the wait window** — Slides 6–8 carry the narrative while the audience's five-iteration loops run for three to five minutes.
- **After the work is done** — Slides 9–15 land the limits, the production path, the conceptual recap, the take-home, and the sources.

---

## The fifteen slides

Each slide is described with three lines: the **concept** it teaches, the **misconception** it corrects, and the one sentence the audience should walk away holding in their head.

### Slide 1 — Title

- **Concept:** The session frame in one screen — what we are doing together for the next sixty minutes.
- **Misconception this corrects:** *(none — this is the opening; no misconception to correct yet.)*
- **Body:**
  - Title: **Building AI Coding Agents with OpenClaw and MiniMax**
  - Subtitle: *A hands-on lab on tool-calling agents and self-improving research loops*
  - Byline: *MiniMax × AI Valley · sixty minutes · hands-on lab*
- **One-line take-away:** *For the next hour we are going to build an agent that improves a chess bot by editing its own code — and you will run it on your machine, not watch it on the screen.*

### Slide 2 — The outcome, before the explanation

- **Concept:** What you will have at the end of the session.
- **Misconception this corrects:** *AI demos are something I watch the presenter do; this will be the same.*
- **Visual:** A real Elo curve climbing roughly 630 → 1280 across a few iterations — a curve the attendee will reproduce on their own machine.
- **One-line take-away:** *By the end of this session, you will have a chart like this from your own machine — not from the presenter's.*

### Slide 3 — Three ingredients of a modern coding agent

- **Concept:** A working agent system is three independent components, not one.
- **Misconception this corrects:** *An "AI agent" is one indivisible thing.*
- **Body:**

  | Component | What it is | What it gives you |
  |---|---|---|
  | **Architecture** (OpenClaw) | Four reusable layers — Gateway, Context, ReAct, Tools | A blueprint you can implement once and reuse |
  | **Model** (MiniMax) | A model that reliably emits structured tool calls | The primitive the layers compose around |
  | **Loop** (AutoResearch) | Agent + objective evaluator + accept-or-reject | A way to compound small ideas into measurable progress |

- **One-line take-away:** *The architecture, the model, and the loop are three separate decisions you can mix and match.*

### Slide 4 — Four layers, four files

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

### Slide 5 — What you will actually do (the four hands-on tasks)

- **Concept:** A concrete list of the four things attendees will type, run, and inspect with their own hands — surfaced *before* they open the notebook so they walk in knowing exactly what they are about to do.
- **Misconception this corrects:** *This is going to be a conceptual session; I'll watch and nod.*
- **Body — four tasks, what you produce, why it teaches what:*

  | You will | And produce | Which teaches you |
  |---|---|---|
  | Run one full agent iteration end-to-end | A tool-call trace you can read line by line | How a tool-calling agent actually moves — three rounds, model → tool → model |
  | Rewrite one tool's description in memory | Before/after JSON of the schema the model receives | Tool descriptions are part of the model's prompt, not internal documentation |
  | Run a five-iteration self-improving loop | Your own Elo curve, on your own machine | How an evaluator + accept/reject step compounds small patches into measurable progress |
  | Pick one extension — change the system prompt, add a new tool, or bias the agent's heuristic | A modified agent that behaves measurably differently from your neighbour's | Which lever to pull when you need to steer a tool-calling agent |

- **One-line take-away:** *Four concrete artefacts you produce with your own hands. None of them are demos you watch.*

### Slide 6 — Why loops beat one-shots *(narrate during the wait window)*

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

### Slide 7 — The metric is the load-bearing decision

- **Concept:** Everything else in the loop is downstream of the metric.
- **Misconception this corrects:** *The model is the important part; the eval is plumbing.*
- **Body:** Centre the literal `estimated_elo`. Four supporting claims:
  - Runs without human judgement.
  - Reproducible — the same patch always scores the same.
  - A number, not an opinion.
  - The model can fake everything else about a patch — explanation, commit message, prose. It cannot fake this.
- **One-line take-away:** *The quality of your metric determines the ceiling of your loop. Pick it deliberately.*

### Slide 8 — The same pattern, at frontier scale

- **Concept:** What runs on the attendee's laptop is the small version of what MiniMax reports running on M2.7 during training.
- **Misconception this corrects:** *Self-improving AI is a futuristic claim, not a real engineering practice.*
- **Body:** Six-step horizontal pipeline — *Analyse failures → Build new skills → Modify scaffolding → Run evals → Update memory → Keep or revert.* Two reported figures: **+30%** on MiniMax's internal coding-agent eval, **100+** self-improvement rounds during training. *Footer:* self-reported by MiniMax; verify before citing externally.
- **One-line take-away:** *Your edit surface is four files. Theirs is the model's own scaffolding. The pattern is the same.*

### Slide 9 — Can you do this at work? Six failure modes, six mitigations

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

### Slide 10 — What OpenClaw actually is, and what the Gateway adds

- **Concept:** OpenClaw is a **self-hosted gateway** for AI agents that talk to users on messaging platforms (WhatsApp, Slack, Discord, CLI). The four-layer architecture you ran in this notebook is OpenClaw's *blueprint*; the Gateway is the *runtime* that hosts that blueprint behind a service boundary.
- **Misconception this corrects:** *OpenClaw is a vague architectural pattern with no actual product behind it.* It is a deployable system; the workshop just chose not to put a stateful service on the on-stage critical path.
- **Body — what the Gateway adds beyond what you ran today:**

  | What you had in-process | What the Gateway adds |
  |---|---|
  | One model client called from your Python kernel | Hosts the agent behind an HTTP service boundary; the Gateway owns the model call |
  | Tools dispatched as local function calls | Tool dispatch invoked over RPC; your handler stays the same |
  | Stdout / a notebook cell as the "interface" | Channel adapters for WhatsApp, Slack, Discord, CLI, or your own |
  | One in-memory `history` list | Session management, routing, and per-user state |

- **One-line take-away:** *OpenClaw is where this agent goes when it stops being a notebook and starts being a service that users talk to.*

### Slide 11 — From notebook to Gateway: four mechanical steps

- **Concept:** The migration is a checklist, not a redesign — exactly because you built against the architectural seams, not around them.
- **Misconception this corrects:** *Production deployment means rewriting the agent.*
- **Body — the four steps, in order:**

  1. **Register your tools with the Gateway.** Your existing `openai_tool_payload()` already emits the JSON-schema function format the Gateway expects — pass the list to the Gateway's tool-registration endpoint as-is.
  2. **Replace `MiniMaxClient.chat_with_tools` with a Gateway session.** The Gateway now owns the model call; your code becomes the tool-execution side of the loop.
  3. **Move `dispatch()` behind an HTTP boundary.** The body of every tool handler stays the same; only the calling convention changes — local function call becomes RPC.
  4. **Pick a transport channel.** WhatsApp, Slack, Discord, CLI, or a custom adapter. The chess demo would naturally ship as a CLI; the choice is independent of every layer above.

- **Footer:** *See `docs/openclaw_mapping.md` for the file-by-file mapping — every concept on this slide has a literal location in the repo.*
- **One-line take-away:** *Three days of plumbing, not a rewrite. The seams you exercised today are what makes that true.*

### Slide 12 — Same agent, production runtime *(optional video closer)*

- **Concept:** Visual proof of the four steps above — the same agent, same five tools, running through the actual Gateway.
- **Misconception this corrects:** *That migration story sounds good in theory; show me it actually working.*
- **Body:** A 30–60 second clip of the agent running through the OpenClaw Gateway. If the clip is not recorded, omit this slide and refer to the migration guide verbally — the previous two slides carry the take-away on their own.
- **One-line take-away:** *The seam between "what you ran today" and "what production looks like" is a deployment step, not a rewrite — and here it is, running.*

### Slide 13 — What you now know (the conceptual recap)

- **Concept:** The ten claims the workshop transmits, rolled up into a single audience-facing statement before take-home. The first audience-facing slide on which the *curriculum itself* appears explicitly.
- **Misconception this corrects:** *I had a vivid hands-on hour but I'm not sure what to remember.*
- **Body — two columns:**

  **Left column (header: *"The four you must be able to state in one sentence"*):**
  1. **The pattern** — agent + measurable objective + bounded edit surface + accept-or-reject.
  2. **The architecture** — four reusable layers, four files: *Gateway, Context, ReAct, Tools*.
  3. **The interface** — tool descriptions are part of the model's prompt, not internal documentation.
  4. **The limit** — the loop optimises *whatever you measure*. Guardrails are part of the design.

  **Right column (header: *"And the six that frame them"*):**
  - **A.** Iteration speed is the bottleneck, not ideas. *(3–5/day human → 100/night loop.)*
  - **B.** A loop ≠ a single prompt. One-shot guesses; a loop lets reality correct each attempt.
  - **C.** A loop ≠ random search. It reads the code, changes mechanisms, debugs, rewrites the experiment.
  - **D.** The agent gets power from being boxed in. Constraint enables compounding.
  - **E.** The pattern transfers anywhere you have an automatic metric. *(Karpathy, MiniMax, Shopify, Codex.)*
  - **F.** The human role shifts to *choose, constrain, judge*. Loop designers beat prompt engineers.

- **Footer:** *"You can hand-write these ten lines in two minutes. That is what you took home."*
- **One-line take-away:** *Four claims you can state in a sentence each, six that explain why. If you can write the ten in two minutes, the workshop worked.*

### Slide 14 — Take this home

- **Concept:** The lab is the start, not the end.
- **Misconception this corrects:** *Workshops are a one-shot experience that ends when you leave the room.*
- **Body:** Repository URL, migration guide, the companion conceptual deck (`Auto Research.pptx`), follow-up channel, MiniMax credits, questions board for written follow-up.
- **One-line take-away:** *Everything you ran is yours to keep, modify, and extend.*

### Slide 15 — Sources and further reading

- **Concept:** Where this pattern came from, and where to read more after the session. The intellectual provenance of every claim the workshop made.
- **Misconception this corrects:** *This is a MiniMax workshop; the ideas are MiniMax's.* They are not. The pattern predates MiniMax by a wide margin; MiniMax is one prominent application of it.
- **Body — five sources, each with link and one-line role:**
  - **Karpathy. *AutoResearch.*** `github.com/karpathy/autoresearch` — reference implementation for AI-driven research loops; origin of the four-file `target/` + `eval.sh` pattern this workshop scales down.
  - **MiniMax. *M2.7 Official Blog.*** `minimaxi.com/news` (search "MiniMax M2") — MiniMax's own writeup of the self-evolution loop, the +30% / 100-rounds figures, and the M2.7 capabilities described in Slide 8.
  - **Shopify. *AI-Assisted Dev Loops.*** `shopify.engineering` (search "autoresearch") — applying autoresearch-style loops to engineering workflows (build time, parser speed, test runtime).
  - **Ralph Loop. *Worker/Reviewer Pattern.*** `simonwillison.net` — a contrasting agent pattern for tasks where quality cannot be reduced to a single number. Choose AutoResearch when you have a reliable metric; choose Ralph when quality requires judgement.
  - **Anthropic. *Agents and Tools.*** `docs.anthropic.com/en/docs/agents-and-tools` — Claude Code, tool use, and autonomous loop patterns.
- **Caveat line (footer):** *"All MiniMax M2.7 numbers are self-reported by MiniMax AI. Not independently audited. Verify before citing externally."*
- **One-line take-away:** *Five primary sources. The pattern is well-documented; this workshop is one entry point.*

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

You are generating a fifteen-slide deck for a sixty-minute hands-on workshop titled *"Building AI Coding Agents with OpenClaw and MiniMax."* The audience is forty to eighty software engineers at a developer conference. The session is a lab, not a talk: the audience spends roughly two-thirds of the time typing in a notebook. Your deck supplies framing, not content the lab already delivers.

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

**Generate exactly the following fifteen slides, in this order:**

**Slide 1 — Title**
- Title: **Building AI Coding Agents with OpenClaw and MiniMax**
- Subtitle: *A hands-on lab on tool-calling agents and self-improving research loops*
- Byline: *MiniMax × AI Valley · sixty minutes · hands-on lab*
- No other body content.

**Slide 2 — The outcome**
- Title: *By the end of this session, you will have a chart like this from your own machine.*
- Visual: an Elo curve climbing from roughly 630 to roughly 1280 over a small number of iterations.
- No other body text.

**Slide 3 — Three ingredients**
- Title: *Architecture · Model · Loop*
- Three-row table:

  | Ingredient | Project | What it gives you |
  |---|---|---|
  | Architecture | OpenClaw | Four-layer pattern: Gateway · Context · ReAct · Tools |
  | Model | MiniMax | A model that emits reliable structured tool calls |
  | Loop | AutoResearch | Agent + objective evaluator + accept-or-reject |

**Slide 4 — Four layers, four files**
- Title: *The architecture, on disk, in your cloned repo*
- Table mapping each layer to its file in `autoresearch_chess/agent/`:

  | Layer | File | What the lab uses |
  |---|---|---|
  | Gateway | `gateway.py` | `ChessAgent.run_iteration` |
  | Context | `context.py` | `build_initial_conversation` |
  | ReAct | `react.py` | `run_react_loop` |
  | Tools | `tools.py` | `TOOLS` (five tools) |

- Footer: *"The architecture is what teaches the pattern. The Gateway is one deployment of that pattern."*

**Slide 5 — What you will actually do**
- Title: *Four hands-on tasks. Four artefacts you produce yourself.*
- Three-column table:

  | You will | And produce | Which teaches you |
  |---|---|---|
  | Run one full agent iteration | A tool-call trace you can read line by line | How a tool-calling agent moves: model → tool → model |
  | Rewrite a tool's description | Before/after JSON of the schema the model sees | Tool descriptions are part of the model's prompt |
  | Run a five-iteration self-improving loop | Your own Elo curve, on your own machine | How accept/reject compounds small patches into measurable progress |
  | Pick one extension — prompt, new tool, or heuristic bias | A modified agent that behaves measurably differently | Which lever to pull when you need to steer a tool-calling agent |

- Footer: *"None of these are demos you watch. They are artefacts you produce."*

**Slide 6 — Why loops beat one-shots**
- Title: *One-shot agents guess. Research loops let reality correct them.*
- Two-column comparison:

  | One-shot agent | Research loop |
  |---|---|
  | Guesses once | Tries, scores, learns, retries |
  | Wrong guess ends the run | Each failure teaches the next attempt |
  | Cannot read the code it tests | Reads the code, understands what it does |
  | Cannot change the experiment | Can rewrite the experiment's own structure |

- Footer: *"Right now, on your laptop, the agent is doing the right column."*

**Slide 7 — The metric is the load-bearing decision**
- Title: *The quality of your metric determines the quality of the loop.*
- Large central element: the literal term `estimated_elo` rendered in monospace, with caption *"one number from one script, not a debate."*
- Four short bullets:
  - Fully automatic — no human judgement needed.
  - Reproducible — the same patch always scores the same.
  - Hard to argue with — a number, not an opinion.
  - The agent can fake everything else; it cannot fake this.

**Slide 8 — MiniMax M2.7: same pattern, frontier scale**
- Title: *Your laptop loop is a miniature of MiniMax's M2.7 self-evolution loop.*
- Horizontal pipeline (six boxes connected by arrows): *Analyse failures → Build new skills → Modify scaffolding → Run evals → Update memory → Keep or revert.*
- Two stat callouts:
  - **+30%** on MiniMax's internal coding-agent eval.
  - **100+** self-improvement rounds, no model retraining.
- Footer: *"Self-reported by MiniMax. Training-time scaffolding search, frozen into the released checkpoint."*

**Slide 9 — Six failure modes, six mitigations**
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

**Slide 10 — What OpenClaw actually is**
- Title: *OpenClaw is a self-hosted gateway for AI agents on messaging platforms.*
- Subtitle: *The four-layer architecture you just ran is OpenClaw's blueprint. The Gateway is the runtime that hosts it behind a service boundary.*
- Two-column table titled *"What you had in-process → What the Gateway adds":*

  | What you had in-process | What the Gateway adds |
  |---|---|
  | One model client called from your Python kernel | Hosts the agent behind an HTTP service boundary; Gateway owns the model call |
  | Tools dispatched as local function calls | Tool dispatch invoked over RPC; your handler is unchanged |
  | Stdout or a notebook cell as the "interface" | Channel adapters for WhatsApp, Slack, Discord, CLI, or your own |
  | One in-memory `history` list | Session management, routing, and per-user state |

- Footer: *"OpenClaw is where this agent goes when it stops being a notebook and starts being a service users talk to."*

**Slide 11 — From notebook to Gateway: four mechanical steps**
- Title: *The migration is a checklist, not a redesign.*
- Numbered list (each step one short paragraph):
  1. **Register your tools.** Your existing `openai_tool_payload()` already emits the JSON-schema function format the Gateway expects.
  2. **Replace the model client.** `MiniMaxClient.chat_with_tools` is swapped for a Gateway session; the Gateway now owns the model call.
  3. **Move dispatch behind an HTTP boundary.** The body of every tool handler stays the same; only the calling convention changes.
  4. **Pick a transport channel.** WhatsApp, Slack, Discord, CLI, or a custom adapter. The choice is independent of every layer above.
- Footer: *"See `docs/openclaw_mapping.md` for the file-by-file mapping. Three days of plumbing, not a rewrite."*

**Slide 12 — Same agent, production runtime *(video slot, optional)***
- Title: *Same agent. Same five tools. Production runtime.*
- Body: large placeholder for a 30–60 second clip of the agent running through the OpenClaw Gateway.
- One quote underneath:

  > "What you ran on your laptop today was the OpenClaw architecture in-process. Here is the same agent on the OpenClaw Gateway. Same four steps you saw on the previous slide. Three days of work from where you are now."

**Slide 13 — What you now know**
- Title: *The ten claims you took with you.*
- Lead-in line under the title: *"You did not just run a chess agent. You ran a working demonstration of how to build AI systems that improve themselves."*
- Two-column layout.
- **Left column** headed *"The four you must be able to state in one sentence":*
  1. **The pattern** — agent + measurable objective + bounded edit surface + accept-or-reject.
  2. **The architecture** — four reusable layers, four files: Gateway, Context, ReAct, Tools.
  3. **The interface** — tool descriptions are part of the model's prompt, not internal documentation.
  4. **The limit** — the loop optimises whatever you measure. Guardrails are part of the design.
- **Right column** headed *"And the six that frame them":*
  - **A.** Iteration speed is the bottleneck, not ideas (3–5/day human → 100/night loop).
  - **B.** A loop is not a single prompt. One-shot guesses; a loop lets reality correct each attempt.
  - **C.** A loop is not random search. It reads the code, changes mechanisms, debugs failures, rewrites the experiment.
  - **D.** The agent gets power from being boxed in. Constraint enables compounding.
  - **E.** The pattern transfers anywhere you have an automatic metric (Karpathy, MiniMax, Shopify, Codex).
  - **F.** The human role: choose, constrain, judge. Loop designers beat prompt engineers.
- Footer: *"You can hand-write these ten lines in two minutes. That is what you took home."*

**Slide 14 — Take this home**
- Title: *Yours to keep, modify, and extend.*
- Link list:
  - Repository: `github.com/nickita-khylkouski/autoresearch-brief-challenge`
  - OpenClaw migration guide: `docs/openclaw_mapping.md`
  - Conceptual companion deck: `Auto Research.pptx`
  - Follow-up channel: *(placeholder)*
  - MiniMax credits: *(placeholder)*
  - Questions board: *(placeholder)*

**Slide 15 — Sources and further reading**
- Title: *Where this pattern came from, and where to read more.*
- Body — five sources, each with author/project, link, and one-line role:
  - **Karpathy. *AutoResearch.*** `github.com/karpathy/autoresearch` — reference implementation; the origin of the `target/` + `eval.sh` pattern.
  - **MiniMax. *M2.7 Official Blog.*** `minimaxi.com/news` (search "MiniMax M2") — MiniMax's writeup of the self-evolution loop and the +30% / 100-rounds figures.
  - **Shopify. *AI-Assisted Dev Loops.*** `shopify.engineering` (search "autoresearch") — autoresearch loops applied to engineering workflows.
  - **Ralph Loop. *Worker/Reviewer Pattern.*** `simonwillison.net` — a contrasting agent pattern for tasks where quality requires judgement, not a number.
  - **Anthropic. *Agents and Tools.*** `docs.anthropic.com/en/docs/agents-and-tools` — Claude Code, tool use, autonomous loop patterns.
- Footer / caveat (smaller text): *"All MiniMax M2.7 numbers are self-reported by MiniMax AI. Not independently audited. Verify before citing externally."*

**Output:** fifteen slides, in the order above, each with a clear title and the specified body. No agenda slide. No thank-you slide. No additional content.

---END PROMPT---
