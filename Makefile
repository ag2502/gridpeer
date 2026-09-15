.PHONY: setup lint test run-sim clean

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]"
	@echo "Run 'source .venv/bin/activate' to activate the environment."

lint:
	. .venv/bin/activate && ruff check .

test:
	. .venv/bin/activate && pytest

run-sim:
	. .venv/bin/activate && python -m dashboard.orchestrator

clean:
	rm -rf .venv .pytest_cache .ruff_cache **/__pycache__
