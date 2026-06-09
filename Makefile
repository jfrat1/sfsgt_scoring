.PHONY: test format lint run_2024_refactor_dev_test run_2024_refactor_prod_test run_2025

python: export PYTHONPATH=${PWD}/sources:${PWD}/tests
python:
	uv run python

test: export PYTHONPATH=${PWD}/sources:${PWD}/tests
test:
	uv run pytest

format: export PYTHONPATH=${PWD}/sources:${PWD}/tests
format:
	uv run sh scripts/lint_fix.sh

lint: export PYTHONPATH=${PWD}/sources:${PWD}/tests
lint:
	uv run sh scripts/lint_check.sh

run_2024: export PYTHONPATH=${PWD}/sources
run_2024:
	uv run python sources/app/run_sfsgt_scoring.py --season=2024

run_2024_test: export PYTHONPATH=${PWD}/sources
run_2024_test:
	uv run python sources/app/run_sfsgt_scoring.py --season=2024_test

run_2025: export PYTHONPATH=${PWD}/sources
run_2025:
	uv run python sources/app/run_sfsgt_scoring.py --season=2025


run_2026: export PYTHONPATH=${PWD}/sources
run_2026:
	uv run python sources/app/run_sfsgt_scoring.py --season=2026


run_2026_test: export PYTHONPATH=${PWD}/sources
run_2026_test:
	uv run python sources/app/run_sfsgt_scoring.py --season=2026_test
