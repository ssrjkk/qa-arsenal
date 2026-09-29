# qa-arsenal — единый запуск всех QA-наборов
#
#   make test            — прогнать все таргеты (нужны .env и реальные API)
#   make check           — hermetic-проверки без внешнего окружения (как CI)
#   make test-hh-api     — hh.ru REST API (Python/pytest)
#   make test-hh-ui      — hh.ru E2E UI (Playwright/TypeScript)
#   make test-guap-py    — guap.ru (Python/pytest)
#   make test-guap-go    — guap.ru (Go)
#   make test-amocrm     — amoCRM (Python/pytest)
#   make deps            — установить зависимости всех таргетов

.PHONY: test check test-hh-api test-hh-ui test-guap-py test-guap-go test-amocrm deps

test: test-hh-api test-hh-ui test-guap-py test-guap-go test-amocrm

# Быстрые проверки без внешнего окружения (то же, что .github/workflows/ci.yml).
check:
	cd hh/api && python -m pytest -m "not integration" -q
	cd hh/ui && npm run typecheck && npm run lint
	cd guap/python && python -m compileall -q api_client api_tests ui_tests && python -m pytest --collect-only -q
	cd guap/go && go build ./... && go vet ./...
	cd amocrm && python -m compileall -q pipelines src tests && python -m pytest --collect-only -q

test-hh-api:
	cd hh/api && python -m pytest

test-hh-ui:
	cd hh/ui && npm test

test-guap-py:
	cd guap/python && python -m pytest

test-guap-go:
	cd guap/go && go test ./...

test-amocrm:
	cd amocrm && python -m pytest

deps:
	cd hh/api && pip install -r requirements.txt
	cd hh/ui && npm ci
	cd guap/python && pip install -r requirements.txt
	cd guap/go && go mod download
	cd amocrm && pip install -r requirements.txt