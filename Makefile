.PHONY: install test lint api web benchmark

install:
	python3 -m pip install -e ".[dev]"
	cd apps/web && npm install

test:
	python3 -m pytest

lint:
	ruff check .
	cd apps/web && npm run lint

api:
	uvicorn helios_api.main:app --app-dir apps/api --reload

web:
	cd apps/web && npm run dev

benchmark:
	python3 scripts/run_benchmarks.py
