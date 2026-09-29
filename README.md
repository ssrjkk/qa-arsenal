# qa-arsenal

[![CI](https://github.com/ssrjkk/qa-arsenal/actions/workflows/ci.yml/badge.svg)](https://github.com/ssrjkk/qa-arsenal/actions)

Unified QA test suites for multiple platforms, consolidated from five separate repositories
into one monorepo organized by target.

## Structure

```
qa-arsenal/
├── hh/                      # hh.ru (headhunter)
│   ├── api/                 #   REST API tests   — Python/pytest (~67 tests)
│   └── ui/                  #   E2E UI tests     — TypeScript/Playwright (Page Object Model)
├── guap/                    # guap.ru
│   ├── python/              #   API + UI + load + SQL — Python/pytest (~30 tests)
│   └── go/                  #   API tests + SQL tasks — Go (~40 tests)
└── amocrm/                  # amoCRM — API, DB, Kafka, load, UI, cross-browser (~230 tests)
```

Each target directory is self-contained: it carries its own dependencies, config, fixtures,
CI workflows and Docker files, so a target can be run without touching the others.

## Quick start

```sh
# run everything
make test

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

All targets require their respective `.env` (see each directory's `.env.example`).

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
require a `.env` with credentials and are run **locally** (`make test`, see per-target READMEs)
or on a schedule with secrets. In CI without those credentials they are excluded, so the
pipeline stays green and signals real problems only.

## License

MIT