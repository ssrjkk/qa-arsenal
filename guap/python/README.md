# Guap.ru Tests (Python) By ssrjkk

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.1-green?logo=pytest&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.x-orange)
![k6](https://img.shields.io/badge/k6-load%20testing-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker&logoColor=white)
![CI](https://github.com/ssrjkk/guap-tests-python/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-65%25-yellow)
![Tests](https://img.shields.io/badge/tests-API%2BUI%2Bload-brightgreen)
![Run](https://img.shields.io/badge/run-~45sec-blue)

---

## Зачем этот проект

Автоматизирует проверку ключевых сценариев образовательного портала ГУАП:

| Сценарий | Тип теста | Зачем |
|----------|-----------|-------|
| Авторизация студента | UI + API | Проверка входа и сессии |
| Просмотр расписания | API + DB | Валидация данных: фронт <-> бэк <-> БД |
| Проверка личных данных | API | Контроль целостности профиля |
| Нагрузка на эндпоинты | k6 | Оценка деградации при росте запросов |

---

## Быстрый старт

```bash
# Клонировать
git clone https://github.com/ssrjkk/guap-tests-python.git 
cd guap-tests-python

# Установить зависимости
pip install -r requirements.txt

# Запустить тесты
pytest api_tests -v          # API-тесты
pytest ui_tests -v           # UI-тесты (требуется браузер)
pytest -m smoke              # Smoke-тесты

# Сгенерировать отчёт
pytest --alluredir=allure-results
allure serve allure-results
```

---

## Архитектура

```
.
├── api_client/                 # HTTP-клиент с retry, логированием, таймаутами
│   ├── base.py                 # BaseApiClient
│   ├── clients.py              # Эндпоинты: GuapApiClient
│   └── schemas.py              # Валидация схем ответов
├── api_tests/                  # API-тесты
│   ├── conftest.py             # Фикстуры: api_client, http_session
│   └── test_api_clients.py
├── ui_tests/                   # UI-тесты (Selenium)
│   ├── conftest.py             # Фикстуры: driver, page, wait
│   ├── pages/                  # Page Objects
│   │   ├── base_page.py
│   │   ├── guap_page.py
│   │   └── metro_page.py
│   └── test_pages.py
├── load_tests/                 # k6-скрипты для нагрузочного тестирования
│   ├── api_basic.js
│   └── api_crud.js
├── sql_tasks/                  # SQL-запросы для валидации данных
│   └── guap_db_queries.sql 
├── tests_data/                 # Тестовые данные и factories
│   └── factories.py
├── config/                     # Конфигурация из .env
│   └── settings.py
├── conftest.py                 # Глобальные фикстуры
└── .github/workflows/          # CI/CD
    └── ci.yml
```

---

## Стек

| Технология | Зачем |
|------------|-------|
| `pytest` | Оркестрация, фикстуры, маркеры `@smoke`, `@regression` |
| `requests` | HTTP-клиент с retry и логированием |
| `Selenium` | UI-автоматизация с Page Objects |
| `k6` | Нагрузочное тестирование |
| `Docker` | Воспроизводимое окружение |
| `GitHub Actions` | CI/CD: lint -> tests -> report |

---

## Запуск в Docker

```bash
docker build -t qa-tests .
docker run --rm qa-tests pytest api_tests -v
docker run --rm qa-tests pytest ui_tests -v
```

---

## CI/CD

GitHub Actions автоматически запускает:
1. **lint** - flake8 проверка стиля
2. **api-tests** - API тесты
3. **ui-tests** - UI тесты (с автоскриншотами при падениях)

---

## Качество кода

```bash
# Проверка стиля
flake8 . --max-line-length=120

# Все тесты
pytest -v

# По тегам
pytest -m smoke
pytest -m regression
pytest -m critical
```
---

## Пример теста

```python
# api_tests/test_api_clients.py
def test_api_student_by_id(api_client):
    """GET /api/students/:id - получение студента по ID"""
    response = api_client.get("/api/students/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data or "student_id" in data
```

```python
# ui_tests/pages/guap_page.py
class GuapMainPage(BasePage):
    def open_main(self):
        self.open("https://guap.ru")
    
    def is_header_visible(self):
        return self.is_visible(self.HEADER)
```
### Этапы и артефакты

| Этап | Триггер | Что делает | Артефакт |
|------|---------|-----------|----------|
| `lint` | каждый коммит | `flake8`, проверка стиля | - |
| `test:api` | каждый PR | Запуск API-тестов с `--alluredir` | `allure-results/` |
| `test:ui` | merge to develop | UI-тесты с автоскриншотами при падениях | `screenshots/failures/` |
| `test:load:k6` | по тегу `@load` | Нагрузочный сценарий на 50 виртуальных пользователей | `k6-report.json` |
| `report:allure` | после тестов | Генерация HTML-отчёта | `allure-report/` -> GitHub Artifact |
| `notify` | merge to main | Уведомление в Telegram при падении критичных тестов | - |

### Как посмотреть отчёт

1. Открой вкладку **Actions** в репозитории
2. Выбери последний успешный запуск
3. В разделе **Artifacts** скачай `allure-report`
4. Распакуй и открой `index.html` в браузере

Или локально:

```bash
# Сгенерировать отчёт из артефактов
allure generate allure-results -o allure-report --clean
allure open allure-report

````

## Контакты

- Telegram: @ssrjkk
- Email: ray013lefe@gmail.com
- GitHub: https://github.com/ssrjkk
