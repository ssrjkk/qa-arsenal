# integration-tests

Unified QA suite for multiple platforms, consolidated from five separate repositories into
one monorepo organized by target.

## Structure

```
integration-tests/
├── hh/                      # hh.ru (headhunter)
│   ├── api/                 #   REST API tests   — Python/pytest
│   └── ui/                  #   E2E UI tests     — TypeScript/Playwright (Page Object Model)
├── guap/                    # guap.ru
│   ├── python/              #   API + UI + load + SQL — Python/pytest
│   └── go/                  #   API tests + SQL tasks — Go
└── amocrm/                  # amoCRM — API, DB, Kafka, load, UI, cross-browser
```

Each target directory is self-contained: it carries its own dependencies, config, fixtures,
CI workflows and Docker files, so a target can be run without touching the others.

## Quick start

```sh
# hh.ru API (Python)
cd hh/api
pip install -r requirements.txt
pytest

# hh.ru UI (Playwright)
cd hh/ui
npm ci
npx playwright test

# guap.ru (Go)
cd guap/go
go test ./...

# guap.ru (Python)
cd guap/python
pip install -r requirements.txt
pytest

# amoCRM
cd amocrm
pip install -r requirements.txt
pytest
```

All targets require their respective `.env` (see each directory's `.env.example`).

## CI

Each target ships its own `.github/workflows` (API/UI/load pipelines), Dockerfiles and
k8s manifests. Run them independently or wire them into a single pipeline via
`.github/workflows/`.

## License

MIT