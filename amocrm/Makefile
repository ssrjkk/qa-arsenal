.PHONY: help install infra-up infra-down test-api test-db test-ui test-kafka test-all test-smoke allure clean lint typecheck

help:
	@echo "=== amoCRM QA Framework ==="
	@echo ""
	@echo "make install       - Install dependencies"
	@echo "make infra-up      - Start infrastructure"
	@echo "make infra-down    - Stop infrastructure"
	@echo "make test-api      - Run API tests"
	@echo "make test-db       - Run DB tests"
	@echo "make test-ui       - Run UI tests (Playwright)"
	@echo "make test-smoke    - Run smoke tests"
	@echo "make test-all      - Run all tests"
	@echo "make lint          - Run linter"
	@echo "make typecheck     - Run type check"
	@echo "make allure        - Open Allure report"
	@echo "make clean         - Clean artifacts"

install:
	pip install -r requirements.txt

infra-up:
	docker-compose up -d
	@echo "Waiting for services..."
	@sleep 15

infra-down:
	docker-compose down -v

test-api:
	pytest pipelines/api/ -v -m api -n auto

test-db:
	pytest pipelines/db/ -v -m db -n auto

test-ui:
	pytest pipelines/ui/ -v -m ui -n auto

test-smoke:
	pytest tests/ -v -m smoke -n auto

test-all:
	pytest tests/ pipelines/ -v -n auto

lint:
	ruff check .

typecheck:
	mypy api core config validators

allure:
	allure serve reports

clean:
	rm -rf reports/
	rm -rf logs/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete