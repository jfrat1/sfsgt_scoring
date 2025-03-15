.PHONY: test format lint

test: export PYTHONPATH=${PWD}/sources:${PWD}/tests
test:
	pipenv run test

format: export PYTHONPATH=${PWD}/sources:${PWD}/tests
format:
	pipenv run fix

lint: export PYTHONPATH=${PWD}/sources:${PWD}/tests
lint:
	pipenv run check


run_2024_refactor_dev_test: export PYTHONPATH=${PWD}/sources
run_2024_refactor_dev_test:
	pipenv run scoring_cli --dev-mode --season=2024_refactor_dev_test

run_2024_refactor_prod_test: export PYTHONPATH=${PWD}/sources
run_2024_refactor_prod_test:
	pipenv run scoring_cli --season=2024_refactor_prod_test