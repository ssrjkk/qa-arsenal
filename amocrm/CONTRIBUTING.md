# Contributing to amoCRM QA Framework

Спасибо за ваш интерес!

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/ssrjkk/amoCRM.git
cd amoCRM

# Install dependencies
pip install -r requirements.txt

# Run all tests
docker-compose up -d
pytest pipelines/ -v

# Or run specific test suite
pytest pipelines/api/ -m api -v
pytest pipelines/ui/ -m ui -v
```

## 📋 Development Workflow

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** following our code standards

3. **Run tests locally**:
   ```bash
   # Lint
   make lint
   
   # Unit tests
   pytest tests/ -v
   
   # Integration tests
   pytest pipelines/ -v --alluredir=reports
   ```

4. **Commit with conventional messages**:
   ```bash
   git commit -m "feat(api): add new endpoint tests"
   ```

5. **Push and create PR**:
   ```bash
   git push -u origin feature/your-feature-name
   ```

## 🧪 Running Tests

| Command | Description |
|---------|-------------|
| `make test-all` | All tests |
| `make test-api` | API tests only |
| `make test-ui` | UI tests only |
| `make test-db` | Database tests |
| `make test-kafka` | Kafka tests |
| `make test-load` | Load tests |
| `make test-smoke` | Smoke tests |

### Run with specific markers

```bash
# Critical tests only
pytest -m critical -v

# API tests
pytest -m api -v

# Smoke tests (fast feedback)
pytest -m smoke -v
```

## 📁 Project Structure

```
amoCRM/
├── tests/                 # Unit тесты
├── pipelines/           # E2E тесты
│   ├── api/            # API tests
│   ├── ui/             # UI tests (Playwright)
│   ├── db/             # Database tests
│   └── kafka/         # Kafka tests
├── core/               # Core utilities
├── fixtures/           # Test fixtures
├── .github/workflows/# CI/CD pipelines
└── docker/             # Docker files
```

## ✅ PR Requirements

Before submitting a PR, ensure:

- [ ] Tests pass locally: `pytest pipelines/ -v`
- [ ] No lint errors: `make lint`
- [ ] New tests added for new functionality
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow conventional format

## 🏗️ Architecture

### Page Object Model
All UI tests use Page Objects from `pipelines/ui/pages/`:

```python
from pipelines.ui.pages.home import LoginPage

def test_login(page):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("user@test.com", "password")
```

### API Client
Use the provided client for API tests:

```python
def test_get_contacts(api_client):
    resp = api_client.contacts.list()
    assert resp.status_code == 200
```

### Data Factory
Generate test data:

```python
from fixtures.data_factory import contact_factory

def test_create_contact(api_client):
    data = contact_factory.create_contact()
    resp = api_client.contacts.create(data)
```

## 🐛 Reporting Issues

Include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Test output/logs
4. Environment details

## 📝 License

MIT License - see LICENSE file for details.
