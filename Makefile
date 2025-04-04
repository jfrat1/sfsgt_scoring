.PHONY: test format lint run_2024_refactor_dev_test run_2024_refactor_prod_test run_2025

python: export PYTHONPATH=${PWD}/sources:${PWD}/tests
python:
	pipenv run python

test: export PYTHONPATH=${PWD}/sources:${PWD}/tests
test:
	pipenv run test

format: export PYTHONPATH=${PWD}/sources:${PWD}/tests
format:
	pipenv run fix

lint: export PYTHONPATH=${PWD}/sources:${PWD}/tests
lint:
	pipenv run check

run_2024: export PYTHONPATH=${PWD}/sources
run_2024:
	pipenv run scoring_cli --season=2024

run_2024_test: export PYTHONPATH=${PWD}/sources
run_2024_test:
	pipenv run scoring_cli --season=2024_test

run_2025: export PYTHONPATH=${PWD}/sources
run_2025:
	pipenv run scoring_cli --season=2025
