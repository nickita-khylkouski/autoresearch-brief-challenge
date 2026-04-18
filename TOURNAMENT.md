# Tournament Format

This challenge is intentionally modeled after the best parts of current public benchmark tournaments:

- fixed dataset plus fixed evaluation scripts
- baseline starter in the repo
- local visible development split
- maintainers-run public and private leaderboard evaluation
- submission bundles that include code, prompts, score artifacts, and a short write-up

Closest inspirations:

- OpenAI Parameter Golf: baseline repo, fixed evaluator, PR-style leaderboard updates
- OpenAI MLE-bench: visible prep and grading scripts, split-aware benchmark workflow
- SWE-rebench: public leaderboard discipline, explicit methodology, evolving benchmark culture

## Public Repo vs Official Evaluation

This public GitHub repo is the starter kit.

It includes:

- the full local `dev` split
- the corpus format
- the baseline
- the validator

It does not include the held-out leaderboard grading data.

Official maintainers keep these off-repo:

- `public_leaderboard`: 20 tasks
- `private_leaderboard`: 40 tasks

## Submission Rules

A valid submission bundle should include:

- `config.json`
- prompt files referenced by `config.json`
- optional `submission_impl.py`
- recommended `research.md`
- recommended `memory.md`
- recommended `results.jsonl`
- recommended `writeup.md`

Participants may change:

- prompts
- retrieval logic
- reranking policy
- memory policy
- critique / verification logic
- synthesis behavior

Participants may not change:

- corpus contents
- hidden evaluation files
- evaluator logic
- budget caps
- tool API surface

## Evaluation Flow

1. Participants iterate locally on `dev`.
2. They validate their bundle with `python3 validate_submission.py --submission ...`.
3. They include their local score artifact and write-up.
4. Maintainers run `public_leaderboard` and `private_leaderboard` centrally.
5. Ranking uses the single scalar `final_score`.

Public repo split sizes:

- `dev`: 20 tasks

Official tournament split sizes:

- `dev`: 20 tasks
- `public_leaderboard`: 20 tasks
- `private_leaderboard`: 40 tasks

## Anti-Cheating

- network access is blocked during evaluation
- task runtime is hard-capped per task
- corpora are frozen and local
- hidden evaluator specs remain separate from visible task files

## Why This Is Tournament-Shaped

This is not just a prompt demo. It has the same basic mechanics as a serious public benchmark:

- a fixed starter
- reproducible grading
- visible local dev split plus hidden leaderboard evaluation
- bundle validation
- leaderboard-ready artifacts
