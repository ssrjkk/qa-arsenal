# qa-arsenal

> **Languages:** [English](README.md) · [Русский](README.ru.md)

[![CI](https://github.com/ssrjkk/qa-arsenal/actions/workflows/ci.yml/badge.svg)](https://github.com/ssrjkk/qa-arsenal/actions)

**Unified QA automation for five target platforms in one monorepo.** API, UI, load, database and
Kafka test suites, consolidated from five separate repositories so they share one pipeline, one
set of standards and one place to review changes.

---

## Why five repositories live here

This repo did not start as a monorepo. It is the result of consolidating **five independent
repositories** that were maintained separately:

| Former repository | Language | Moved to |
|-------------------|----------|----------|
| `hh-api-tests` | Python | `hh/api` |
| `hh-playwright` | TypeScript | `hh/ui` |
| `guap-tests-python` | Python | `guap/python` |
| `guap-tests-go` | Go | `guap/go` |
| `amocrm-tests` | Python | `amocrm` |

Each target still lives in its own self-contained directory (own dependencies, fixtures,
Docker files), so it can be developed and run independently. The monorepo only adds shared
value on top:

- **One CI pipeline** — every target is checked on each push/PR (`.github/workflows/ci.yml`).
- **One review surface** — cross-cutting changes land in a single pull request.
- **One set of conventions** — root `Makefile`, `.gitignore`, `.gitattributes`, license.
- **One place to discover** — the whole QA portfolio is visible from a single README.

---

## What is inside

| Target | Platform | Coverage | Stack |
|--------|----------|----------|-------|
| `hh/api` | hh.ru | REST API, contracts, security, performance | Python 3.12, pytest, Pydantic v2, requests |
| `hh/ui` | hh.ru | E2E UI | TypeScript, Playwright, Page Object Model |
| `guap/python` | guap.ru | API, UI, load, SQL | Python, pytest, Selenium, k6 |
| `guap/go` | guap.ru | API, SQL tasks | Go 1.21 |
| `amocrm` | amoCRM | API, DB, Kafka, load, UI, cross-browser | Python, pytest, Playwright, Locust, Selenium Grid |

```
qa-arsenal/
├── hh/                      # hh.ru (headhunter)
│   ├── api/                 #   REST API tests   — Python/pytest (~67 tests)
│   └── ui/                  #   E2E UI tests     — TypeScript/Playwright
├── guap/                    # guap.ru
│   ├── python/              #   API + UI + load + SQL — Python/pytest (~30 tests)
│   └── go/                  #   API tests + SQL tasks — Go (~40 tests)
└── amocrm/                  # amoCRM — API, DB, Kafka, load, UI, cross-browser (~230 tests)
```

---

## Quick start

```sh
# run every target (needs .env files + live APIs)
make test

# hermetic checks without any external dependencies (same as CI)
make check

# individual targets
make test-hh-api      # hh.ru REST API
make test-hh-ui       # hh.ru E2E UI
make test-guap-py     # guap.ru Python
make test-guap-go     # guap.ru Go
make test-amocrm      # amoCRM

# install all dependencies
make deps
```

Without `make`:

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

All targets require their own `.env` (copy each directory's `.env.example` and fill in real
values). Full run instructions live in each target's README.

---

## CI

`.github/workflows/ci.yml` runs on every push/PR and is a **hermetic health check** — it never
needs real credentials:

| job | what runs |
|-----|-----------|
| `hh/api` | unit + contract tests (`pytest -m "not integration"`) |
| `hh/ui` | typecheck (`tsc --noEmit`) + lint |
| `guap/python` | bytecode compile + `pytest --collect-only` |
| `guap/go` | `go build ./...` + `go vet ./...` |
| `amocrm` | bytecode compile + `pytest --collect-only` |

Live integration tests (real hh.ru / guap.ru / amoCRM APIs, Playwright against a running app)
require `.env` credentials and are run **locally** (`make test`) or on a schedule with secrets.
In CI without credentials they are excluded, so the pipeline stays green and signals real
problems only.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — how to add a target, run checks, and what a pull
request must satisfy.

## License

MIT — see [LICENSE](LICENSE).