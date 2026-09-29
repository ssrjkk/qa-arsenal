# hh-playwright By ssrjkk

![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue?logo=typescript&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-1.42-green?logo=playwright&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-20.x-brightgreen?logo=node.js&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker&logoColor=white)
![CI](https://github.com/ssrjkk/hh-playwright/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-yellow)

## Stack

- Playwright 1.42
- TypeScript 5.3
- Node.js 20

## Opportunities
- Многослойная архитектура
Чёткое разделение: API layer <-> Page Objects <-> Tests <-> Fixtures
- UI <-> API валидация
Создание через UI -> проверка через API -> подтверждение в интерфейсе
- Стабильные ожидания
Auto-wait Playwright + кастомные retry-логики для нестабильных интеграций
- Параллельное выполнение
Запуск до 4 воркеров, ускорение регресса с 4ч до ~30 мин
- Type-safe код
Полная типизация через TypeScript 5.3 + интерфейсы в src/types/
- Data Factory
Генерация тестовых данных с учётом бизнес-правил
- HTML + Allure отчёты
Детальная визуализация результатов, скриншоты, видео, логи
- CI/CD ready
GitHub Actions: автозапуск на PR, smoke на push, публикация артефактов
- Docker-first подход
Изолированное окружение, воспроизводимость на любой ОС

## Structure

```
src/
├── api/                  # API layer
│   ├── base.api.ts       # Base class with request wrapper
│   ├── auth.api.ts       # Auth endpoints
│   ├── users.api.ts      # Users endpoints
│   ├── todos.api.ts      # Todos endpoints
│   └── api.factory.ts
├── pages/                # Page Objects
│   ├── base.page.ts
│   ├── login.page.ts
│   ├── register.page.ts
│   └── todos.page.ts
├── fixtures/             # Playwright fixtures
├── helpers/              # Logger, validators
├── data/                 # DataFactory for test data
├── types/                # TypeScript interfaces
└── tests/
    ├── api/              # API tests
    └── ui/               # UI tests
```

## Run

```bash
npm install
npx playwright install chromium

# Start mock server
node mock-server.js

# Run tests
npm test
npm run test:smoke
npm run test:regression
npm run test:report
```

## Test Tags

- `@smoke` - Critical smoke tests
- `@regression` - Full regression suite
- `@api` - API tests
- `@e2e` - UI tests
- `@critical` - Must pass in CI

## CI/CD

GitHub Actions workflow runs on every push to main/develop.

## Docker

```bash
npm run docker:compose
```

## Contacts

- Telegram: @ssrjkk
- Email: ray013lefe@gmail.com
- GitHub: https://github.com/ssrjkk

