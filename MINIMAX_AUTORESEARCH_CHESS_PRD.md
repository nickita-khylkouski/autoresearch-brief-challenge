# MiniMax AutoResearch Chess Elo Demo PRD

Status: Draft for Nickita and Victor
Audience: internal build planning for TechEx workshop/demo
Date: 2026-05-06
Primary goal: make a stage-safe, MiniMax-powered AutoResearch demo where a chess bot's estimated Elo improves over time.

## 1. Executive Summary

We are building a cloneable AutoResearch demo that teaches the core idea of autonomous eval-driven improvement. The demo should show MiniMax repeatedly improving a constrained chess bot, running objective evaluations, accepting only changes that improve estimated Elo, and plotting the best score as it rises.

This is not a general chess platform and not a full agent framework. It is a focused, reliable, local-first workshop repo. The intended experience is:

1. Presenter starts a local demo on stage.
2. A weak baseline chess bot is evaluated and assigned a low estimated Elo.
3. MiniMax receives a narrow optimization task and can edit only the chess bot implementation.
4. The backend runs fast local matches against fixed benchmark opponents.
5. The system accepts a candidate only when the evaluation improves.
6. A notebook/UI shows the best Elo curve climbing.
7. Attendees can clone the repo, add a MiniMax key, and reproduce the loop.

The product story is: "MiniMax M2.7 was shaped by autonomous research and self-improvement loops; here is a tiny version you can understand in 50 minutes."

## 2. Background

The reference video, "AutoResearch explained.." by Caleb Writes Code, demonstrates AutoResearch as a loop where an AI system improves an algorithm without direct human intervention between attempts. The video uses two examples:

- A restaurant inventory simulator where the policy improves served orders and working capital.
- A chess engine that starts around low Elo and improves dramatically after many experiments.

The important lesson from the video is not the exact domain. The important lesson is the structure:

- define the goal clearly;
- define the evaluation clearly;
- constrain what the model can edit;
- run experiments repeatedly;
- keep improvements;
- discard regressions.

MiniMax's M2.7 announcement gives us the sponsor-aligned framing. MiniMax describes model improvement as partly driven by autonomous research and engineering loops: systems that analyze failures, modify scaffolds, run evaluations, compare outcomes, and preserve useful improvements. Our workshop should make that abstract research story concrete.

Sources:

- YouTube reference demo: https://www.youtube.com/watch?v=5-ekc3eXNvs
- MiniMax M2.7 announcement: https://www.minimax.io/news/minimax-m27-en
- Current repo target: https://github.com/nickita-khylkouski/autoresearch-brief-challenge

## 3. Product Decision

The demo should focus only on chess Elo improvement.

Chess is the right workshop task because:

- it is visual;
- everyone understands "better at chess";
- it has a natural numeric score;
- the bot can be weak at first and visibly improve;
- local CPU evaluation is feasible;
- the editable surface can be tightly constrained;
- regressions are easy to detect;
- "Elo goes up" is a simple stage story.

We should not switch to restaurant optimization, retrieval benchmarks, OpenAI parameter golf, or a general AutoResearch benchmark before TechEx. Those can be mentioned as extensions, but they should not be the core build.

## 4. Goals

### 4.1 Product Goals

- Show how AutoResearch works through a concrete, repeatable chess optimization loop.
- Make MiniMax the visible model powering the loop.
- Let attendees run the demo locally with only a MiniMax key and standard dev tooling.
- Make the on-stage demo reliable even with bad Wi-Fi, rate limits, or noisy evals.
- Make the backend credible enough that technical attendees can inspect it and trust the score.
- Keep the UI/notebook simple enough that non-experts understand the process.

### 4.2 Technical Goals

- Run on a normal laptop without GPU.
- Complete a short demo iteration in under 2 minutes in stage mode.
- Keep a full audit trail of every attempt: prompt, patch, eval, accept/reject, score.
- Prevent the model from modifying the evaluator or cheating.
- Support multiple MiniMax API keys and graceful fallback when one key rate-limits.
- Provide a deterministic replay path for stage reliability.

### 4.3 Workshop Goals

- Fill a 50-minute session with an educational walkthrough plus live demo.
- Let attendees clone and run the project after the talk.
- Avoid making the session depend on everyone installing tools simultaneously.
- Give Victor and Nickita a crisp story that can be explained at a high level.

## 5. Non-Goals

- No hosted SaaS in v1.
- No user accounts.
- No online multiplayer.
- No global public leaderboard required for TechEx.
- No GPU dependency.
- No fine-tuning.
- No training a neural chess model.
- No perfect official Elo claims.
- No complex OpenClaw dependency in the critical path.
- No broad autonomous file editing.
- No "agent can change anything" demo.

## 6. Target Users

### 6.1 Primary Users

Nickita and Victor, presenting live at TechEx.

Needs:

- start demo quickly;
- explain it clearly;
- avoid stage failures;
- show MiniMax visibly;
- recover instantly if live calls fail.

### 6.2 Secondary Users

Workshop attendees/hackers.

Needs:

- clone repo;
- add MiniMax key;
- run one command;
- see numbers go up;
- understand the project structure;
- inspect accepted patches.

### 6.3 Tertiary Users

MiniMax/OpenClaw/sponsor-side viewers.

Needs:

- see MiniMax powering a real autonomous improvement loop;
- understand how this maps to research workflows;
- see that the demo is credible and not just a scripted animation.

## 7. Core User Stories

1. As a presenter, I can run `make stage-demo` and see a live estimated Elo curve updating within minutes.
2. As a presenter, I can switch to replay mode instantly if MiniMax or network calls fail.
3. As an attendee, I can clone the repo, add `MINIMAX_API_KEY`, and run a short local loop.
4. As an attendee, I can open a notebook and follow the AutoResearch loop step by step.
5. As a technical attendee, I can verify that MiniMax cannot edit the evaluator.
6. As a builder, I can inspect each accepted/rejected patch and understand why it won or lost.
7. As Victor/Nickita, we can present the system as a miniature version of MiniMax-style self-improvement loops.

## 8. Demo Narrative

The stage story should be this:

1. "We are going to make an AI improve a chess bot by itself."
2. "We are not going to tell it the winning heuristic."
3. "We will only give it a goal, an eval, and a constrained file surface."
4. "MiniMax proposes a code change."
5. "The backend plays games against benchmark opponents."
6. "If the bot improves, the change is kept."
7. "If it gets worse, the change is thrown away."
8. "Over time, the best Elo rises."

The audience should remember:

- AutoResearch is about eval loops, not magic prompts.
- The hard part is choosing the right task boundary and metric.
- MiniMax is useful because the loop requires many coding/reasoning attempts.

## 9. Product Surface

The repo should expose three ways to interact:

### 9.1 Notebook Walkthrough

File: `workshop.ipynb`

Purpose: educational walkthrough.

Sections:

1. What AutoResearch is.
2. Chess task definition.
3. Baseline bot.
4. Evaluation harness.
5. MiniMax patch proposal.
6. Accept/reject logic.
7. Elo progression chart.
8. Replay and debugging.

The notebook should not hide the loop. It should show enough internals that attendees understand the mechanism.

### 9.2 CLI

The CLI is the reliable path and should power the notebook/UI underneath.

Expected commands:

```bash
make setup
make eval
make train
make stage-demo
make replay-best
```

Recommended lower-level commands:

```bash
python -m autoresearch_chess.eval --bot bot/current.py
python -m autoresearch_chess.loop --iterations 20
python -m autoresearch_chess.replay --run artifacts/demo_run
python -m autoresearch_chess.ui
```

### 9.3 Local UI

The UI can be small. It exists to make the demo legible on stage.

Required views:

- current best estimated Elo;
- Elo over iteration chart;
- current candidate status;
- accepted/rejected count;
- latest patch summary;
- match/eval status;
- replay/live mode indicator.

Nice-to-have views:

- chess board preview;
- diff viewer;
- opponent breakdown;
- run timeline.

## 10. MiniMax Integration

### 10.1 Local Key Discovery

Local MiniMax credentials were found at:

```text
/Users/nickita/.claude-wafer/minimax.env
```

That file contains:

```text
MINIMAX_API_KEY=***MASKED***
MINIMAX_API_KEY_2=***MASKED***
MINIMAX_API_KEY_3=***MASKED***
MINIMAX_API_HOST=***MASKED***
MINIMAX_MODEL=***MASKED***
API_TIMEOUT_MS=***MASKED***
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=***MASKED***
```

There is also a key health/cooldown file:

```text
/Users/nickita/.claude-wafer/minimax_key_health.json
```

The current local claude-mini dry run defaults to:

```text
runtime=minimax
model=MiniMax-M2.7
```

The demo repo should support the same style:

```bash
MINIMAX_ENV_FILE=~/.claude-wafer/minimax.env make stage-demo
```

For public attendees, the repo should use `.env.example`:

```text
MINIMAX_API_KEY=
MINIMAX_API_HOST=https://api.minimaxi.chat
MINIMAX_MODEL=MiniMax-M2.7
```

If MiniMax requires a group/account identifier for direct API access, add:

```text
MINIMAX_GROUP_ID=
```

### 10.2 Key Rotation

The local setup has three MiniMax key entries. The backend should support:

- `MINIMAX_API_KEY`
- `MINIMAX_API_KEY_2`
- `MINIMAX_API_KEY_3`
- optionally `MINIMAX_API_KEYS` as a comma/newline-separated list

On rate limit:

- mark key as temporarily unavailable;
- rotate to next key;
- log the cooldown;
- never print the key value.

### 10.3 Prompt Contract

MiniMax should receive:

- objective: improve estimated Elo;
- editable files list;
- forbidden files list;
- latest eval results;
- previous accepted changes;
- constraints on runtime and dependencies;
- instruction to return a patch and summary.

MiniMax should not receive:

- hidden eval internals beyond high-level score components;
- ability to edit evaluator;
- API keys inside prompt;
- full `.env`;
- unrelated project files.

## 11. AutoResearch Loop

The core loop:

1. Load current best bot.
2. Run baseline eval if no score exists.
3. Build a research prompt for MiniMax.
4. Ask MiniMax for one candidate patch.
5. Apply patch to a temporary candidate worktree/copy.
6. Run syntax/type checks.
7. Run fast smoke matches.
8. Run full configured eval.
9. Compare candidate score against current best.
10. Accept candidate if improvement exceeds threshold.
11. Reject and discard candidate otherwise.
12. Save artifacts.
13. Update chart/UI.
14. Repeat.

### 11.1 Accept Criteria

A candidate should be accepted when:

- it passes syntax/import checks;
- it does not modify forbidden files;
- it does not add forbidden dependencies;
- it completes eval within timeout;
- estimated Elo improves by at least the configured threshold.

Recommended threshold:

- stage mode: `+5 Elo` or any statistically plausible improvement;
- serious mode: `+15 Elo` or confidence-adjusted improvement.

### 11.2 Reject Reasons

Reject if:

- invalid code;
- timeout;
- illegal file edit;
- evaluator changed;
- worse Elo;
- too noisy/no clear improvement;
- crashes on legal positions;
- illegal move generated;
- dependency not installed;
- excessive runtime.

### 11.3 Artifact Requirements

Every iteration writes:

```text
artifacts/runs/{run_id}/iterations/{iteration}/prompt.md
artifacts/runs/{run_id}/iterations/{iteration}/response.md
artifacts/runs/{run_id}/iterations/{iteration}/patch.diff
artifacts/runs/{run_id}/iterations/{iteration}/eval.json
artifacts/runs/{run_id}/iterations/{iteration}/decision.json
artifacts/runs/{run_id}/best/bot_snapshot.py
artifacts/runs/{run_id}/progress.jsonl
artifacts/runs/{run_id}/progress.png
```

## 12. Chess Bot Design

### 12.1 Recommended Implementation

Use Python for the first version.

Recommended libraries:

- `python-chess` for board legality and move generation.
- Optional local Stockfish binary only as an optional stronger benchmark, not required.

The bot should implement:

- legal move selection;
- static evaluation function;
- shallow minimax/alpha-beta search;
- move ordering;
- basic time/depth limits.

### 12.2 Baseline Bot

The baseline should be intentionally weak but not random.

Minimum baseline:

- prefers captures by material value;
- has shallow 1-ply search;
- uses crude piece values;
- ignores king safety, development, pawn structure, tactics beyond captures.

Starting estimated Elo target:

- around 600-900 estimated Elo.

This gives MiniMax room to improve quickly.

### 12.3 Editable Files

Recommended editable surface:

```text
bot/evaluate.py
bot/search.py
bot/move_ordering.py
bot/config.py
```

The agent may improve:

- piece-square tables;
- king safety;
- mobility;
- passed pawns;
- center control;
- pawn structure;
- capture ordering;
- alpha-beta pruning;
- quiescence search;
- depth/time constants;
- endgame heuristics.

### 12.4 Forbidden Files

```text
eval/
tournament/
autoresearch_loop/
artifacts/
tests/
.env
.env.example
README.md during eval
workshop.ipynb during eval
```

The model must not edit:

- scoring logic;
- benchmark opponents;
- match seeds;
- allowed/forbidden file config;
- previous artifact logs;
- MiniMax API handling;
- replay data.

## 13. Evaluation Design

### 13.1 Metric

Primary metric: estimated Elo.

Important wording: this is not official tournament Elo. It is a local estimate based on fixed benchmark games.

### 13.2 Opponent Ladder

Use fixed anchor opponents:

1. Random legal move bot: anchor 200.
2. Greedy material bot: anchor 600.
3. Baseline shallow minimax bot: anchor 900.
4. Improved heuristic bot: anchor 1200.
5. Optional Stockfish skill-level bot: anchor 1600+.

The candidate plays a fixed number of games against each anchor. Results are converted into estimated Elo.

### 13.3 Fast Stage Mode

Stage mode must prioritize visible progress.

Recommended:

- 4-8 games per opponent;
- fixed opening positions;
- fixed seeds;
- max move count;
- strict per-move time/depth limits;
- lower confidence threshold.

Target runtime:

- smoke eval: under 20 seconds;
- full stage eval: under 90 seconds.

### 13.4 More Reliable Local Mode

For attendees after the talk:

- 10-30 games per opponent;
- more opening seeds;
- optional Stockfish;
- better confidence reporting.

Target runtime:

- 2-10 minutes depending on machine.

### 13.5 Anti-Cheating

The evaluator should:

- hash forbidden files before and after eval;
- run candidate from a clean copy;
- block network access during eval if feasible;
- reject file reads outside allowed bot files if feasible;
- reject attempts to special-case opponent names or seeds;
- keep hidden test openings for final score.

For the workshop, anti-cheating mostly exists to preserve credibility. The model is not malicious, but the demo should teach correct harness design.

## 14. Backend Architecture

Recommended modules:

```text
autoresearch_chess/
  minimax_client.py
  prompt_builder.py
  patcher.py
  guardrails.py
  evaluator.py
  tournament.py
  elo.py
  loop.py
  replay.py
  artifacts.py
  ui_server.py

bot/
  current.py
  evaluate.py
  search.py
  move_ordering.py
  config.py

eval/
  opponents.py
  openings.py
  match_runner.py
  score.py

notebooks/
  workshop.ipynb

artifacts/
  demo_replay/
```

### 14.1 State Machine

Run states:

- `idle`
- `baseline_eval`
- `prompting_minimax`
- `patch_received`
- `guardrail_check`
- `candidate_eval`
- `accepted`
- `rejected`
- `error`
- `replay`
- `complete`

The UI and notebook should read from a shared `progress.jsonl` stream so they do not need to know backend internals.

### 14.2 Error Handling

If MiniMax call fails:

- retry with backoff;
- rotate key if rate-limited;
- save error artifact;
- continue if another key exists;
- otherwise offer replay mode.

If eval fails:

- reject candidate;
- save stack trace;
- continue loop.

If UI fails:

- CLI still works;
- notebook can still render progress from artifacts.

If all live paths fail:

- run `make replay-best`.

## 15. Stage Reliability Modes

### 15.1 Live Mode

MiniMax actively proposes patches during the presentation.

Pros:

- most impressive;
- real sponsor value;
- shows actual loop.

Cons:

- API/rate-limit/network risk;
- eval noise;
- possible bad patches.

### 15.2 Warm-Started Live Mode

Start from a known baseline plus a few precomputed accepted improvements. Let MiniMax continue from there.

Pros:

- curve already has momentum;
- less chance of flatline;
- still live.

Cons:

- must explain honestly that it is warm-started.

### 15.3 Replay Mode

Replay a previously captured successful run with real prompts, patches, evals, and artifacts.

Pros:

- stage-safe;
- deterministic;
- still educational.

Cons:

- less exciting than live generation.

Recommendation: open with live mode, but have replay mode one command away.

## 16. UI Requirements

The UI should be practical, not decorative.

### 16.1 Main Screen

Required elements:

- header: "MiniMax AutoResearch Chess"
- live/replay badge
- current best estimated Elo
- latest candidate estimated Elo
- iteration number
- accepted count
- rejected count
- line chart of best Elo over time
- log stream
- latest patch summary
- current status

### 16.2 Chart

Chart should show:

- grey dots for candidate scores;
- bright line for best accepted Elo;
- labels for accepted improvements;
- optional vertical markers for mode changes.

This should visually copy the useful part of the Caleb video: flatline, experiments, jump, flatline, jump.

### 16.3 Board Preview

Nice-to-have:

- show baseline vs current best game;
- animate or step through moves;
- highlight captures/checkmates/blunders.

Do not overbuild this before the backend works.

## 17. Notebook Requirements

The notebook should be the teaching artifact.

Suggested sections:

1. "The problem: make a weak chess bot better."
2. "The baseline bot."
3. "The evaluation harness."
4. "What MiniMax can edit."
5. "What MiniMax cannot edit."
6. "One iteration manually."
7. "The full loop."
8. "Reading the Elo curve."
9. "How to adapt this to your own problem."

The notebook should avoid giant code dumps. It should call CLI functions and show outputs.

## 18. README Requirements

README should answer:

- What is this?
- Why MiniMax?
- What is AutoResearch?
- What does the demo optimize?
- How do I run it?
- Where do I put my key?
- What does estimated Elo mean?
- What files can the agent edit?
- What happens if MiniMax rate-limits?
- How do I replay the stage demo?

Minimum quickstart:

```bash
git clone https://github.com/nickita-khylkouski/autoresearch-brief-challenge
cd autoresearch-brief-challenge
cp .env.example .env
# add MINIMAX_API_KEY
make setup
make stage-demo
```

For Nickita's local machine:

```bash
MINIMAX_ENV_FILE=/Users/nickita/.claude-wafer/minimax.env make stage-demo
```

## 19. Presentation Plan

Target: 50 minutes.

### 19.1 Time Breakdown

0-5 min: Hook
Show weak chess bot and ask: can MiniMax improve this without us hand-coding the heuristic?

5-10 min: AutoResearch concept
Explain goal, eval, constraints, iteration, accept/reject.

10-15 min: MiniMax M2.7 tie-in
Explain that serious model/research systems use similar autonomous improvement loops.

15-20 min: Chess harness
Show bot, evaluator, editable files, forbidden files.

20-35 min: Live loop
Run MiniMax. Show candidate patches, evals, accepted improvements, chart.

35-42 min: Notebook walkthrough
Show how attendees can clone and run.

42-47 min: Generalization
Explain how this applies to retrieval, parameter golf, routing, prompts, agents, code optimization.

47-50 min: Q&A / repo link / call to action.

### 19.2 Stage Script

Core lines:

- "The hard part is not asking the model to code. The hard part is giving it a scoreboard it cannot fake."
- "AutoResearch turns software development into repeated experiments."
- "MiniMax is not just answering once; it is operating inside a loop."
- "Bad ideas are cheap because the eval rejects them."
- "Good ideas compound because the harness keeps them."

## 20. OpenClaw Integration Ideas

OpenClaw should not block v1. It can be included in the story as optional.

Potential angles:

1. OpenClaw as an alternate runner:
   - same evaluator;
   - same editable files;
   - different agent backend.

2. OpenClaw as workshop framing:
   - "This is the kind of harness OpenClaw-style agents can use."

3. OpenClaw as extension challenge:
   - attendees can swap the MiniMax client for OpenClaw.

4. OpenClaw as leaderboard category:
   - MiniMax baseline vs OpenClaw runner later.

Recommendation: mention OpenClaw in final 5 minutes and README "future work", but do not integrate before the MiniMax path is stable.

## 21. Implementation Phases

### Phase 0: PRD and Demo Contract

Deliverables:

- this PRD;
- agreed demo scope;
- agreed stage fallback strategy.

Exit criteria:

- Nickita and Victor agree chess Elo is the demo;
- MiniMax is required;
- backend reliability is top priority.

### Phase 1: Chess Harness

Deliverables:

- baseline bot;
- legal move generation;
- match runner;
- fixed benchmark opponents;
- estimated Elo score;
- CLI eval command.

Exit criteria:

- baseline bot gets a stable low score;
- eval finishes locally;
- results saved to JSON.

### Phase 2: AutoResearch Loop

Deliverables:

- MiniMax client;
- prompt builder;
- patch application;
- allowed/forbidden file guardrails;
- accept/reject logic;
- artifact logging.

Exit criteria:

- one MiniMax-generated candidate can be evaluated;
- accepted improvements are kept;
- regressions are rejected.

### Phase 3: Stage Demo

Deliverables:

- `make stage-demo`;
- progress chart;
- replay mode;
- precomputed successful run;
- key rotation/rate-limit handling.

Exit criteria:

- stage mode runs from clean checkout;
- replay mode works without API;
- one command can recover from failure.

### Phase 4: Notebook and README

Deliverables:

- `workshop.ipynb`;
- `README.md`;
- `.env.example`;
- demo instructions.

Exit criteria:

- attendee can run from instructions;
- notebook explains the loop clearly.

### Phase 5: Optional UI Polish

Deliverables:

- local web UI;
- live chart;
- log stream;
- patch summaries;
- optional board preview.

Exit criteria:

- UI makes stage demo easier to follow;
- CLI remains the source of truth.

## 22. Acceptance Criteria

### Must Have

- Local run works with MiniMax key.
- Baseline bot evaluates successfully.
- MiniMax can propose a candidate patch.
- Guardrails block forbidden file edits.
- Eval returns estimated Elo.
- Best Elo chart updates.
- Accepted improvements persist.
- Rejected changes are discarded.
- Replay mode works without network.
- README includes exact setup steps.

### Should Have

- Multiple MiniMax keys supported.
- Rate-limit rotation.
- Notebook walkthrough.
- Stage mode under 2 minutes per iteration.
- Patch summaries shown in UI/notebook.
- Optional Stockfish benchmark if installed.

### Could Have

- Local web UI with chess board.
- Hosted static leaderboard.
- OpenClaw alternate runner.
- Attendee challenge mode.
- Exportable presentation screenshots.

## 23. Risks and Mitigations

### Risk: MiniMax rate limits during demo

Mitigation:

- use three local keys;
- rotate on cooldown;
- pre-run a warm-start;
- have replay mode.

### Risk: Elo score is noisy

Mitigation:

- fixed seeds;
- fixed openings;
- enough games in non-stage mode;
- use "estimated Elo" language;
- accept only clear improvements in serious mode.

### Risk: Agent edits evaluator

Mitigation:

- allowed-file list;
- forbidden-file hash checks;
- isolated candidate copy;
- reject illegal diffs.

### Risk: Live loop flatlines

Mitigation:

- weak baseline;
- easy first improvements;
- warm-start option;
- precomputed replay curve.

### Risk: Attendees cannot install dependencies

Mitigation:

- presenter-driven stage demo;
- notebook visible on screen;
- simple post-event clone path;
- optional Docker/devcontainer later.

### Risk: Too much chess detail

Mitigation:

- explain "scoreboard and loop";
- avoid deep chess theory;
- show chart and accept/reject events.

## 24. Security and Secret Handling

- Never commit `.env`.
- Never print API keys in logs.
- Mask keys in UI and artifacts.
- Store local keys only in ignored env files.
- Include `.env.example` with empty values.
- Document key rotation but not actual keys.
- If a key is pasted into chat or slides, rotate it.

Nickita's local MiniMax env file is usable for development but should not be copied into the repo:

```text
/Users/nickita/.claude-wafer/minimax.env
```

## 25. Recommended Defaults

Default model:

```text
MiniMax-M2.7
```

Default host:

```text
https://api.minimaxi.chat
```

Default stage config:

```text
iterations=8
games_per_opponent=4
opponents=random,greedy,baseline
max_eval_seconds=90
accept_threshold_elo=5
```

Default serious config:

```text
iterations=30
games_per_opponent=20
opponents=random,greedy,baseline,heuristic,stockfish_optional
max_eval_seconds=600
accept_threshold_elo=15
```

## 26. Definition of Done

The project is done enough for TechEx when:

- Nickita can run `make stage-demo` locally using `/Users/nickita/.claude-wafer/minimax.env`.
- Victor can run replay mode from a clean clone.
- A weak chess bot shows a low baseline estimated Elo.
- At least one captured run shows multiple accepted improvements.
- The chart clearly goes upward.
- The notebook explains the loop end to end.
- The README lets an attendee run the project with their own MiniMax key.
- The demo has a fallback if MiniMax/network fails.

## 27. Final Product Thesis

This demo should make AutoResearch feel obvious:

```text
Clear goal + constrained code surface + objective eval + MiniMax iterations = compounding improvement.
```

The audience does not need to remember the chess implementation. They need to remember that once the eval is good, the model can search the space of improvements on its own.
