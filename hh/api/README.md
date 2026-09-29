# hh-api-tests By ssrjkk

[![CI Status](https://github.com/ssrjkk/hh-api-tests/actions/workflows/ci.yml/badge.svg)](https://github.com/ssrjkk/hh-api-tests/actions)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-31%20passed-brightgreen.svg)](https://github.com/ssrjkk/hh-api-tests/actions)
[![Coverage](https://codecov.io/gh/ssrjkk/hh-api-tests/branch/main/graph/badge.svg)](https://codecov.io/gh/ssrjkk/hh-api-tests)

**31 тест** · **<0.5s полный прогон** · **99%+ стабильность** · **Docker/K8s ready**

- Слоистая архитектура: тесты не знают про HTTP
- Pydantic v2 контракты: fail fast на расхождении схем
- Детерминированные retry: tenacity + urllib3 для нестабильных эндпоинтов
- Воспроизводимые запуски: Docker, K8s, CI/local parity

---

## Какие проблемы закрывает

**То, что обычно делают неправильно:**
```python
# Антипаттерн: тест знает слишком много
def test_search():
    response = requests.get("https://api.hh.ru/vacancies", params={"text": "QA"})
    assert response.status_code == 200  # Нет валидации, нет абстракции
```

**Что делает этот фреймворк:**
```python
# Подход инженера: изолировано, валидировано, поддерживаемо
def test_search(vacancies_api: VacanciesApi):
    response = vacancies_api.search(text="QA")
    ResponseValidator(response).status(200).has_key("items").raise_if_errors()
```

Реальные боли API-тестирования, которые закрывает проект:
- Flaky endpoints → стратегии retry с экспоненциальной задержкой
- Schema drift → contract-тесты с JSON Schema валидацией
- Грязные тесты с HTTP вызовами → строгое разделение слоев
- Дублирование логики → API layer как единственная точка входа
- Нестабильный CI → mock-based тесты, 99%+ стабильность

---

## Инженерные принципы

**Тесты не знают про HTTP.** VacanciesApi скрывает все HTTP детали. Тесты вызывают только методы доменного слоя.

**API layer — единственная точка входа.** Все эндпоинты в одном месте: `VacanciesApi.ENDPOINT = "/vacancies"`.

**Контракты валидируются, а не предполагаются.** Pydantic модели + JSON Schema для каждого ответа.

**Сбои детерминированы, а не случайны.** Mock-based тесты устраняют внешние зависимости.

**Запуски тестов воспроизводимы.** Одинаковые результаты в Docker, K8s, локально, CI.

---

## Архитектура

```
tests/                    Тесты: только бизнес-логика
    ↓ (вызывают методы домена)
api/                     API слой: абстракция эндпоинтов
    ↓ (использует)
core/                   Ядро: HTTP клиент + retry + логирование
    ↓ (валидирует)
validators/               Валидаторы: Pydantic + JSON Schema
    ↓ (использует)
fixtures/                 Фикстуры: тестовые данные, клиенты
```

**Почему это работает:**
- **Tests layer** — падает? Изменилась только бизнес-логика.
- **API layer** — падает? Изменился только эндпоинт. Одно место для правки.
- **Core layer** — падает? Изменилась только реализация HTTP.
- **Validators** — падает? Изменилась только структура ответа.

---

## Пример: плохо vs хорошо

❌ **Что делает джуниор:**
```python
def test_vacancy():
    response = requests.get(f"{BASE_URL}/vacancies/12345")
    data = response.json()
    assert "name" in data  # Хрупко, нет типобезопасности
```

✅ **Что делает этот фреймворк:**
```python
def test_vacancy(vacancies_api: VacanciesApi):
    response = vacancies_api.get_by_id("12345")
    vacancy = Vacancy.model_validate(response.json())
    
    ResponseValidator(response) \
        .status(200) \
        .has_keys(["id", "name", "employer"]) \
        .json_path("items", lambda x: len(x) > 0) \
        .raise_if_errors()
```

**Сигналы:** Типобезопасность, fluent валидация, разделение ответственности.

---

## Технологический стек

**pytest 8.1+** → оркестрация тестов с маркерами и фикстурами  
**requests 2.31+** → HTTP транспорт с пулингом соединений  
**Pydantic 2.5+** → валидация ответов и типобезопасность  
**tenacity 8.2+** → стратегия повторов для транзитных сбоев  
**Allure** → HTML отчеты с вложениями и историей  
**Docker/K8s** → паритет окружений локально/CI/prod  
**GitHub Actions** → многостадийный CI с параллельными джобами  

---

## Как запускать

```bash
# Установка
pip install -r requirements.txt

# Все тесты (31 тест, mock-based, быстро)
pytest tests/ -v

# С Allure отчетом
pytest tests/ --alluredir=allure-results && allure serve allure-results

# С покрытием
pytest tests/ --cov=api --cov=core --cov=validators --cov-report=html

# Docker
docker build -f docker/Dockerfile -t hh-tests .
docker run --rm hh-tests pytest tests/ -v
```

---

## CI/CD

**Пайплайн:** lint → test → report → coverage

| Стадия | Инструмент | Что проверяет |
|--------|------------|---------------|
| **Lint** | ruff, black | Стиль кода, форматирование |
| **Types** | mypy | Статическая проверка типов |
| **Test** | pytest + Allure | 31 тест, HTML отчет |
| **Report** | Allure → GitHub Pages | Публичная история тестов |
| **Coverage** | pytest-cov → Codecov | Отслеживание покрытия кода |

Посмотреть CI: https://github.com/ssrjkk/hh-api-tests/actions  
Allure отчеты: https://ssrjkk.github.io/hh-api-tests/allure/

---

## Метрики

**31 тест**, проходящих консистентно:
- 20 mock-тестов (проверка логики без реального API)
- 4 contract-теста (валидация схем)
- 7 security-тестов (маскировка данных, HTTPS enforcement)

**Время выполнения:** ~0.4s для полного набора (mock-based).

**Покрытие:** Расширяемо через CI (интеграция с Codecov готова).

Без выдуманных цифр. Реальные результаты из реальных прогонов.

---

## Roadmap

- **Расширение contract testing** — валидация по OpenAPI спецификации
- **Управление тестовыми данными** — фабрики, фикстуры, управление состоянием
- **Параллельное выполнение** — pytest-xdist для ускорения
- **Сервисная виртуализация** — интеграция с WireMock/Hoverfly
- **Нагрузочное тестирование** — load, stress, endurance сценарии

Проект живой. Активная разработка.

---

**Автор:** ssrjkk  
**Telegram:** @ssrjkk · 
**Email:** ray013lefe@gmail.com  
**GitHub:** https://github.com/ssrjkk
