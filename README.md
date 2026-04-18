# AutoResearch Brief Challenge

`AutoResearch Brief Challenge` is a public starter repo for a scaffold-optimization benchmark on a frozen corpus.

This repo is meant to be cloned by competitors. It gives you a real local dev loop, a working baseline, a submission validator, and a held-out-style tournament workflow without exposing the official leaderboard grading data.

## What You Can Do With This Repo

- inspect the benchmark format
- run the visible `dev` split locally
- validate a submission bundle
- improve the scaffold instead of changing the model
- submit a bundle for maintainer-run leaderboard evaluation

## Quickstart

Requirements:

- Python 3.11+

```bash
python3 scripts/generate_autoresearch_challenge_seed.py
python3 validate_submission.py --submission submissions/baseline
python3 evaluate.py --split dev --submission submissions/baseline
python3 inspect_task.py --task-id dev_001
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Core Idea

This challenge rewards better research-process design, not model swapping.

You are meant to improve:

- retrieval strategy
- query expansion
- reranking
- memory policy
- critique / verification logic
- synthesis discipline

You are not meant to change:

- the frozen corpus
- the evaluator
- the official leaderboard grading logic

## Repo Layout

- `challenge/`: evaluator, corpus loader, scoring, sandboxing, validation
- `corpora/frozen_autoresearch_v1/`: frozen local corpus pack
- `tasks/dev.json`: visible development split
- `tasks/_private/dev_hidden.json`: visible dev grading data
- `submissions/baseline/`: working reference submission
- `submissions/template/`: starter bundle for competitors
- `tests/`: standard-library test suite
- `TOURNAMENT.md`: tournament rules and held-out split policy

## Commands

```bash
python3 validate_submission.py --submission submissions/template
python3 evaluate.py --split dev --submission submissions/baseline
python3 evaluate.py --split dev --task-id dev_001 --submission submissions/baseline
python3 leaderboard.py --score-file runs/<run-id>/summary.json
python3 inspect_task.py --task-id dev_001
python3 inspect_run.py --run runs/<run-id>
```

## Public Repo vs Official Tournament

This public GitHub repo includes only the visible `dev` split.

The official tournament shape is:

- `dev`: 20 visible tasks
- `public_leaderboard`: 20 held-out tasks, maintainer-evaluated
- `private_leaderboard`: 40 held-out tasks, maintainer-evaluated

That is deliberate. The public repo is for local iteration. The official rankings come from hidden evaluation.

See:

- [TOURNAMENT.md](./TOURNAMENT.md)
- [tasks/leaderboard_manifest.json](./tasks/leaderboard_manifest.json)

## Submission Workflow

1. Copy `submissions/template` to a new submission directory.
2. Edit prompts and optional `submission_impl.py`.
3. Run `python3 validate_submission.py --submission path/to/submission`.
4. Run `python3 evaluate.py --split dev --submission path/to/submission`.
5. Include your local run artifact and `writeup.md` when submitting to maintainers.

## Integrity Guarantees

- strict JSON outputs
- deterministic local scoring
- network access blocked during evaluation
- hard task timeouts
- fixed support-set citation checks
- reusable baseline for comparison

## Benchmark Lineage

This starter is shaped like the best public optimization-benchmark repos:

- visible local dev loop
- fixed evaluator
- baseline starter
- hidden leaderboard grading
- submission bundle discipline
