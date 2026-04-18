.PHONY: help seed test eval-dev validate-baseline smoke inspect-example

help:
	@printf "Targets:\\n"
	@printf "  make seed              Regenerate deterministic public starter data\\n"
	@printf "  make validate-baseline Validate the baseline submission bundle\\n"
	@printf "  make eval-dev          Score the baseline on the public dev split\\n"
	@printf "  make inspect-example   Inspect the first visible task\\n"
	@printf "  make test              Run the test suite\\n"
	@printf "  make smoke             Run the full local verification loop\\n"

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
