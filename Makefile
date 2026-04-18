.PHONY: seed test eval-dev validate-baseline

seed:
	python3 scripts/generate_autoresearch_challenge_seed.py

test:
	python3 -m unittest discover -s tests -p 'test_*.py' -v

eval-dev:
	python3 evaluate.py --split dev --submission submissions/baseline

validate-baseline:
	python3 validate_submission.py --submission submissions/baseline
