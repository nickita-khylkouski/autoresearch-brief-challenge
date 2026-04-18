# AutoResearch Brief Challenge

This package implements a local-first benchmark kit for scaffold optimization on a frozen corpus.

Read these in order:

1. [../README.md](../README.md) for the fast commands
2. [../TOURNAMENT.md](../TOURNAMENT.md) for the tournament format
3. [../submissions/template](../submissions/template) for the competitor bundle shape
4. [../tasks/leaderboard_manifest.json](../tasks/leaderboard_manifest.json) for official split sizes

Core properties:

- deterministic local corpus tools
- visible `dev` split in the public starter repo
- strict JSON outputs
- hard task budgets
- network-blocked evaluation
- bundle validation before submission

Main modules:

- `corpus.py`: frozen corpus search and reranking
- `tool_harness.py`: fixed tool API and budget accounting
- `evaluator.py`: split evaluation and run artifact emission
- `scoring.py`: correctness, citation, and evidence-group scoring
- `validation.py`: submission bundle checks
