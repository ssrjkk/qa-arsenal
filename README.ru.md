# qa-arsenal

> **Языки:** [English](README.md) · [Русский](README.ru.md)

[![CI](https://github.com/ssrjkk/qa-arsenal/actions/workflows/ci.yml/badge.svg)](https://github.com/ssrjkk/qa-arsenal/actions)

**Единая QA-автоматизация для пяти площадок в одном моно-репозитории.** API-, UI-, load-,
базовые и Kafka-наборы тестов, объединённые из пяти отдельных репозиториев: один пайплайн,
единые стандарты и одно место для ревью изменений.

---

## Почему здесь пять репозиториев

Этот репозиторий не начинался как моно-репо. Он — результат консолидации **пяти независимых
репозиториев**, которые велись по отдельности:

| Бывший репозиторий | Язык | Переехал в |
|--------------------|------|------------|
| `hh-api-tests` | Python | `hh/api` |
| `hh-playwright` | TypeScript | `hh/ui` |
| `guap-tests-python` | Python | `guap/python` |
| `guap-tests-go` | Go | `guap/go` |
| `amocrm-tests` | Python | `amocrm` |

Каждый таргет по-прежнему живёт в своей самодостаточной директории (свои зависимости,
фикстуры, Docker-файлы) и может разрабатываться и запускаться независимо. Моно-репо добавляет
общую ценность:

- **Один CI-пайплайн** — каждый таргет проверяется на каждый push/PR (`.github/workflows/ci.yml`).
- **Одна точка ревью** — сквозные изменения попадают в один pull request.
- **Единые соглашения** — корневой `Makefile`, `.gitignore`, `.gitattributes`, лицензия.
- **Одно место для поиска** — весь QA-портфель виден из одного README.

---

## Что внутри

| Таргет | Площадка | Покрытие | Стек |
|--------|----------|----------|------|
| `hh/api` | hh.ru | REST API, контракты, безопасность, производительность | Python 3.12, pytest, Pydantic v2, requests |
| `hh/ui` | hh.ru | E2E UI | TypeScript, Playwright, Page Object Model |
| `guap/python` | guap.ru | API, UI, load, SQL | Python, pytest, Selenium, k6 |
| `guap/go` | guap.ru | API, SQL-задачи | Go 1.21 |
| `amocrm` | amoCRM | API, БД, Kafka, load, UI, кроссбраузер | Python, pytest, Playwright, Locust, Selenium Grid |

```
qa-arsenal/
├── hh/                      # hh.ru (headhunter)
│   ├── api/                 #   REST API тесты   — Python/pytest (73: 46 unit + 27 integration)
│   └── ui/                  #   E2E UI тесты     — TypeScript/Playwright + vitest unit (18)
├── guap/                    # guap.ru
│   ├── python/              #   API + UI + load + SQL — Python/pytest (49: 19 unit + 30 integration)
│   └── go/                  #   API тесты + SQL-задачи — Go (48: 8 unit + 40 integration)
└── amocrm/                  # amoCRM — API, БД, Kafka, load, UI, кроссбраузер (228: 12 unit + 216 integration)
```

## Статус таргетов

| Таргет | Тестов | Hermetic в CI | Зрелость |
|--------|-------:|--------------:|----------|
| `hh/api` | 73 (46 unit + 27 integration) | 46 unit + контракты | зрелый — слоистая архитектура, моки, валидация |
| `hh/ui` | 18 (12 unit + 6 E2E) | 12 unit + typecheck + lint | растёт — E2E против живого/mock-приложения |
| `guap/python` | 49 (19 unit + 30 integration) | 19 unit | рабочий |
| `guap/go` | 48 (8 unit + 40 integration) | 8 unit + build + vet | рабочий |
| `amocrm` | 228 (12 unit + 216 integration) | 12 unit | зрелый — крупнейший, мульти-пайплайн (API/БД/Kafka/UI/load) |

## Известные ограничения (честно)

- **Интеграционные тесты требуют живых API и credentials** (`.env`). Они *не* выполняются в CI —
  CI проверяет только hermetic unit-тесты и здоровье сборки. Зелёный пайплайн **не** доказывает,
  что интеграционные наборы проходят; запускайте `make test` локально с реальным `.env`.
- **Нет гейта по покрытию** — у части таргетов есть конфиг coverage, но моно-репо не блокирует
  мержи по порогу покрытия.
- **`hh/ui` — самый тонкий таргет по E2E** — всего 6 E2E-спецификаций; unit-слой (12 тестов)
  и typecheck + lint идут в CI, но автоматического браузерного прогона нет.
- **Стиль кода различается между таргетами** — каждый строился независимо со своим стеком и
  конвенциями. Моно-репо стандартизует *интерфейс* (Makefile, CI, README), но не внутренности.
- **`amocrm` тяжёлый** — крупнейший набор; полный локальный запуск требует PostgreSQL, Kafka,
  Selenium Grid и Elasticsearch (см. его `docker-compose`).

---

## Быстрый старт

```sh
# прогнать все таргеты (нужны .env файлы и живые API)
make test

# hermetic-проверки без внешних зависимостей (то же, что CI)
make check

# отдельные таргеты
make test-hh-api      # hh.ru REST API
make test-hh-ui       # hh.ru E2E UI
make test-guap-py     # guap.ru Python
make test-guap-go     # guap.ru Go
make test-amocrm      # amoCRM

# установить все зависимости
make deps
```

Без `make`:

```sh
# hh.ru API (Python)
cd hh/api && pip install -r requirements.txt && pytest

# hh.ru UI (Playwright)
cd hh/ui && npm ci && npx playwright install --with-deps chromium && npm test

# guap.ru (Go)
cd guap/go && go test ./...

# guap.ru (Python)
cd guap/python && pip install -r requirements.txt && pytest

# amoCRM
cd amocrm && pip install -r requirements.txt && pytest
```

Каждому таргету нужен свой `.env` (скопируйте `.env.example` из директории и заполните
реальные значения). Полные инструкции по запуску — в README каждого таргета.

---

## CI

`.github/workflows/ci.yml` запускается на каждый push/PR и представляет собой **hermetic-проверку
здоровья** — ей не нужны реальные credentials:

| Джоба | Что выполняется |
|-------|-----------------|
| `hh/api` | 46 unit + контрактные тесты (`pytest -m "not integration"`) |
| `hh/ui` | 12 unit-тестов (`vitest run`) + typecheck + lint |
| `guap/python` | 19 unit-тестов + `pytest --collect-only` |
| `guap/go` | `go build ./...` + `go vet ./...` + `go test ./unit/...` |
| `amocrm` | 12 unit-тестов + `pytest --collect-only` |

Живые интеграционные тесты (реальные API hh.ru / guap.ru / amoCRM, Playwright против
работающего приложения) требуют credentials из `.env` и запускаются **локально** (`make test`)
или по расписанию с секретами. В CI без credentials они исключаются, поэтому пайплайн остаётся
зелёным и сигнализирует только о реальных проблемах.

---

## Участие

См. [CONTRIBUTING.md](CONTRIBUTING.md) — как добавить таргет, запускать проверки и что должно
быть в pull request. Сообщение об уязвимостях: см. [SECURITY.md](SECURITY.md).

## Лицензия

MIT — см. [LICENSE](LICENSE).