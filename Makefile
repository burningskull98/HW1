.PHONY: install test coverage lint run

install:
	poetry install

test:
	poetry run pytest tests/

coverage:
poetry run pytest -s --cov=tests --cov-report=html --cov-fail-under=90

lint:
	poetry run flake8 log_analyzer/

run:
	poetry run python -m log_analyzer.main.PHONY: install test coverage lint run

