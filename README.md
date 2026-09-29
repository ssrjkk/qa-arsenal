# qa-arsenal

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

`.github/workflows/ci.yml` runs every target in a matrix on every push/PR: Python 3.12 for the
Python suites, Node 20 + Playwright for the UI suite, Go 1.21 for the Go suite. Each target also
keeps its own local workflows for the pipelines it needs (load, k8s, cross-browser).

## License

MIT