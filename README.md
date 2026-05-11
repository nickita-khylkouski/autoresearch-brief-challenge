# AutoResearch Brief Challenge

[![CI](https://github.com/nickita-khylkouski/autoresearch-brief-challenge/actions/workflows/ci.yml/badge.svg)](https://github.com/nickita-khylkouski/autoresearch-brief-challenge/actions/workflows/ci.yml)

`AutoResearch Brief Challenge` is a local-first benchmark for improving an autoresearch scaffold on a frozen corpus.

This is a real benchmark starter kit, not a prompt demo. It gives competitors a visible development split, a fixed evaluator, a working baseline, reproducible local scoring, and a held-out tournament workflow without publishing the official leaderboard grading data.

## Why This Repo Exists

The challenge is designed around a simple idea: reward better research process, not model swapping.

You are meant to improve:

- retrieval strategy
- query expansion
- reranking
- memory policy
- critique and verification logic
- synthesis discipline

You are not meant to change:

- the frozen corpus
- the evaluator
- the official leaderboard grading logic

## Why It Is Benchmark-Shaped

The workflow here follows the pattern used by serious public benchmark repos such as [openai/mle-bench](https://github.com/openai/mle-bench) and [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench):

- a public starter repository
- a visible local development loop
- a fixed evaluator
- baseline implementations
- held-out leaderboard evaluation

That matters because competitors can iterate locally without making the official ranking gameable.

## Quickstart

Requirements:

- Python 3.11+

Fast path:

```bash
make seed
make validate-baseline
make eval-dev
make test
```

Equivalent direct commands:

```bash
python3 scripts/generate_autoresearch_challenge_seed.py
python3 validate_submission.py --submission submissions/baseline
python3 evaluate.py --split dev --submission submissions/baseline
python3 inspect_task.py --task-id dev_001
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Current baseline on the public `dev` split:

- `final_score`: `0.613333`
- `task_count`: `20`

## What You Can Do In This Repo

- inspect the benchmark format
- inspect a real visible task with `inspect_task.py`
- run the visible `dev` split locally
- validate a submission bundle before shipping it
- compare runs with leaderboard-style summaries
- improve the scaffold without touching benchmark internals

## What A Task Looks Like

Each task specifies:

- a question
- a task type
- a corpus pack
- a fixed output schema
- hard budgets for time, tool calls, tokens, search results, and citations

For example:

```bash
python3 inspect_task.py --task-id dev_001
```

That task asks:

> Which retrieval stack is strongest for multi-hop frozen-corpus questions when the system only gets ten tool calls?

And it exposes explicit budgets such as:

- `max_tool_calls = 10`
- `max_time_seconds = 15`
- `max_tokens = 2200`

## Scoring Model

Each task score combines:

- answer correctness against hidden facets
- citation validity against fixed support chunk sets
- evidence coverage across required evidence groups
- budget penalties when a scaffold exceeds limits

The evaluator writes run artifacts so you can debug why a score changed:

- `summary.json`
- `scores.json`
- `raw_outputs.json`

## Public Repo vs Official Tournament

This public GitHub repo includes only the visible `dev` split for local iteration.

The official tournament shape is:

- `dev`: 20 visible tasks
- `public_leaderboard`: 20 held-out tasks, maintainer-evaluated
- `private_leaderboard`: 40 held-out tasks, maintainer-evaluated

That split is deliberate. Public code should support meaningful local iteration without leaking the real leaderboard targets.

The public repo therefore contains:

- `tasks/dev.json`
- `tasks/_private/dev_hidden.json`

The `dev_hidden` file is included because `dev` is the visible split and must be fully scoreable locally. Held-out leaderboard grading data is not published in this repository.

See:

- [TOURNAMENT.md](./TOURNAMENT.md)
- [tasks/leaderboard_manifest.json](./tasks/leaderboard_manifest.json)

## Submission Workflow

1. Copy `submissions/template` to a new submission directory.
2. Edit prompt files and, if needed, `submission_impl.py`.
3. Run `python3 validate_submission.py --submission path/to/submission`.
4. Run `python3 evaluate.py --split dev --submission path/to/submission`.
5. Inspect the run artifact in `runs/...`.
6. Submit the bundle, local score artifact, and `writeup.md` to maintainers for held-out evaluation.

## Repo Layout

- `challenge/`: evaluator, corpus loader, scoring, sandboxing, validation
- `corpora/frozen_autoresearch_v1/`: frozen local corpus pack
- `tasks/dev.json`: visible development split
- `tasks/_private/dev_hidden.json`: visible grading targets for `dev`
- `submissions/baseline/`: working reference submission
- `submissions/template/`: competitor starter bundle
- `tests/`: standard-library test suite
- `TOURNAMENT.md`: public-vs-held-out tournament rules

## Useful Commands

```bash
python3 validate_submission.py --submission submissions/template
python3 evaluate.py --split dev --submission submissions/baseline
python3 evaluate.py --split dev --task-id dev_001 --submission submissions/baseline
python3 leaderboard.py --score-file runs/<run-id>/summary.json
python3 inspect_task.py --task-id dev_001
python3 inspect_run.py --run runs/<run-id>
```

## MiniMax AutoResearch Chess Demo

This repo also includes a local-first TechEx demo for explaining AutoResearch with a chess Elo loop. An OpenClaw-style tool-calling agent built on MiniMax inspects the editable bot files, considers recent history, and proposes small unified diffs. The backend evaluates each candidate with fixed local matches, and only estimated Elo improvements are kept.

The agent's full tool-call trace is persisted per iteration so attendees can see exactly what the model asked for and how it reasoned. See [`docs/openclaw_mapping.md`](./docs/openclaw_mapping.md) for how the agent modules map onto OpenClaw's gateway / context / react / tool-layer architecture.

The demo loop is:

```text
goal + constrained editable files + objective eval + MiniMax iterations = compounding improvement
```

Chess demo quickstart:

```bash
cp .env.example .env
# add MINIMAX_API_KEY to .env for live-demo, or use the mock/replay paths below
make setup
make eval
make stage-demo
make replay-best
make chess-test
```

Nickita's local development machine can run live MiniMax with:

```bash
MINIMAX_ENV_FILE=/Users/nickita/.claude-wafer/minimax.env make live-demo
```

Demo commands:

```bash
make setup       # create .venv and install chess demo dependencies
make eval        # evaluate the weak baseline chess bot
make stage-demo  # stage-safe mock MiniMax loop
make live-demo   # one live MiniMax-backed stage iteration
make replay-best # replay captured successful run without API/network
make chess-test  # run chess demo pytest suite
```

The captured replay in `artifacts/demo_replay/` shows estimated Elo rising from `629.6` to `1163.4` to `1276.1`. The score is always **estimated Elo**, not official chess Elo.

MiniMax may edit only:

- `bot/evaluate.py`
- `bot/search.py`
- `bot/move_ordering.py`
- `bot/config.py`

The evaluator, benchmark opponents, tests, artifacts, env files, and dependency files are guarded. Candidate evals run in a timed subprocess and are rejected on timeout, illegal moves, forbidden edits, crashes, or insufficient Elo improvement.

See [MINIMAX_AUTORESEARCH_CHESS_PRD.md](./MINIMAX_AUTORESEARCH_CHESS_PRD.md) for the full product spec.

## Integrity Guarantees

- deterministic local scoring
- strict JSON outputs
- network access blocked during evaluation
- hard task timeouts
- fixed support-set citation checks
- frozen local corpora
- reusable baseline for comparison

## Design Notes

This repo intentionally stays small and easy to run:

- no external services are required for the public starter
- the core loop is standard-library friendly
- CI reruns seed generation, validation, evaluation, and tests on every push

That makes it easy for other researchers to clone, understand, and modify without reverse-engineering a large framework first.
