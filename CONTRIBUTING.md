# Contributing to qa-arsenal

Thanks for contributing! This is a monorepo of QA test suites for five target platforms.
Each target lives in its own directory and is fully independent.

## Repository layout

```
hh/          hh.ru (headhunter)
  api/       Python/pytest REST API tests
  ui/        TypeScript/Playwright E2E tests
guap/        guap.ru
  python/    Python/pytest API + UI + load + SQL tests
  go/        Go API tests + SQL tasks
amocrm/      amoCRM API, DB, Kafka, load, UI, cross-browser tests
```

## Adding a new target

1. Create a self-contained directory: `mkdir <platform>`.
2. Include everything the target needs to run on its own: dependencies manifest, config,
   fixtures, Docker files, and a `README.md` with run instructions.
3. Provide a `.env.example` (never commit real credentials).
4. Add the target to:
   - `Makefile` — a `test-<target>` target and add it to `test` (and to `check` if it has
     hermetic checks);
   - `.github/workflows/ci.yml` — a job for its hermetic checks (unit tests or build + static
     analysis; integration tests that need live APIs belong behind `@pytest.mark.integration`
     or an equivalent marker so CI stays green without credentials).
5. Update the root `README.md` structure table and test counts.

## Running

```sh
make check     # hermetic checks, no external dependencies (same as CI)
make test      # full run — needs .env files and live APIs
```

See each target's `README.md` for its exact commands.

## Pull request checklist

- [ ] `make check` passes locally.
- [ ] New tests are added for the change (and marked `integration` if they hit a live API).
- [ ] No real credentials or secrets are committed (only `.env.example`).
- [ ] README updated if behaviour or structure changed.
- [ ] Commit message follows the conventional format (`feat(api):`, `fix(ui):`, `chore:`, ...).

## CI

`.github/workflows/ci.yml` runs hermetic checks on every push/PR. If a job fails, reproduce it
locally with the matching `make check` target before re-pushing.

## License

MIT — see [LICENSE](LICENSE).