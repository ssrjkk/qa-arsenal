# Security Policy

## Reporting a vulnerability

This repository contains QA test suites, including some that connect to real external APIs
(hh.ru, guap.ru, amoCRM) with credentials. If you find a **real** vulnerability — something that
could leak credentials, expose sensitive data, or compromise a system — please report it
**privately**:

- Open a private report via **GitHub Security Advisories** (the recommended path):
  `https://github.com/ssrjkk/qa-arsenal/security/advisories/new`
- Do **not** open a public issue for it.

Do not include live credentials, tokens or personal data in any report.

## What is in scope

- Code that reads, stores or transmits credentials (`.env` handling, API clients, CI secrets).
- Misconfiguration that could leak secrets (committed `.env`, secrets in Docker/k8s manifests).
- Logic errors in test frameworks that could cause unsafe behaviour.

## Out of scope

- Missing coverage or tests not passing (open these as normal issues).
- Integration tests failing against live APIs without configured credentials.
- General feature requests.

## Disclosure

We aim to acknowledge reports within 3 business days and to coordinate a fix before public
disclosure. As a rule, do not exploit or publicly demonstrate the issue before a fix is released.

## Credentials

- Real credentials must **never** be committed. Only `.env.example` files belong in the repo.
- CI runs only hermetic checks and does not require real credentials.
- If you suspect a real credential was committed, treat it as compromised and rotate it
  immediately, then report it via the channel above.