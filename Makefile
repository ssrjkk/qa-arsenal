# qa-arsenal — единый запуск всех QA-наборов
#
#   make test            — прогнать все таргеты
#   make test-hh-api     — hh.ru REST API (Python/pytest)
#   make test-hh-ui      — hh.ru E2E UI (Playwright/TypeScript)
#   make test-guap-py    — guap.ru (Python/pytest)
#   make test-guap-go    — guap.ru (Go)
#   make test-amocrm     — amoCRM (Python/pytest)
#   make deps            — установить зависимости всех таргетов

.PHONY: test test-hh-api test-hh-ui test-guap-py test-guap-go test-amocrm deps

test: test-hh-api test-hh-ui test-guap-py test-guap-go test-amocrm

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