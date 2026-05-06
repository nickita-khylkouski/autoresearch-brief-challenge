PYTHON ?= .venv/bin/python
MINIMAX_ENV_FILE ?= .env

.PHONY: help seed test eval-dev validate-baseline smoke inspect-example setup eval train stage-demo live-demo replay-best chess-test

help:
	@printf "Targets:\\n"
	@printf "  make seed              Regenerate deterministic public starter data\\n"
	@printf "  make validate-baseline Validate the baseline submission bundle\\n"
	@printf "  make eval-dev          Score the baseline on the public dev split\\n"
	@printf "  make inspect-example   Inspect the first visible task\\n"
	@printf "  make test              Run the test suite\\n"
	@printf "  make smoke             Run the full local verification loop\\n"
	@printf "  make setup             Create chess demo venv and install demo deps\\n"
	@printf "  make eval              Evaluate the chess demo baseline\\n"
	@printf "  make stage-demo        Run the stage-safe chess AutoResearch demo\\n"
	@printf "  make replay-best       Replay captured chess demo artifacts\\n"
	@printf "  make chess-test        Run the chess demo pytest suite\\n"

seed:
	python3 scripts/generate_autoresearch_challenge_seed.py

test:
	python3 -m unittest discover -s tests -p 'test_*.py' -v

eval-dev:
	python3 evaluate.py --split dev --submission submissions/baseline

validate-baseline:
	python3 validate_submission.py --submission submissions/baseline

inspect-example:
	python3 inspect_task.py --task-id dev_001

smoke: seed validate-baseline eval-dev test

setup:
	python3 -m venv .venv
	$(PYTHON) -m pip install -r requirements-chess.txt

eval:
	$(PYTHON) -m autoresearch_chess.eval --out artifacts/eval.json

train:
	MINIMAX_ENV_FILE="$(MINIMAX_ENV_FILE)" $(PYTHON) -m autoresearch_chess.loop --iterations 20

stage-demo:
	AUTORESEARCH_MOCK_MINIMAX=1 MINIMAX_ENV_FILE="$(MINIMAX_ENV_FILE)" $(PYTHON) -m autoresearch_chess.loop --stage --iterations 3

live-demo:
	MINIMAX_ENV_FILE="$(MINIMAX_ENV_FILE)" $(PYTHON) -m autoresearch_chess.loop --stage --iterations 1

replay-best:
	$(PYTHON) -m autoresearch_chess.replay --run artifacts/demo_replay

chess-test:
	$(PYTHON) -m pytest -q tests_chess
