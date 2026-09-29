# ADR-002: Use Playwright over Selenium for UI Automation

## Status
Accepted

## Context
We need a modern, fast, and reliable UI automation framework that:
- Has built-in waiting mechanisms (no explicit sleeps)
- Supports modern web apps (SPA, async)
- Works well with parallel execution
- Has good debugging/storytelling features

## Decision
We will use **Playwright** as the primary UI automation tool.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Playwright** | Auto-wait, built-in retries, fast | Newer, smaller community |
| | Parallel support, trace viewer | |
| Selenium | Large community, multi-browser | Explicit waits needed, slower |
| | | Flaky by design |
| Cypress | Great DX, fast | Chrome only, no iFrames |

## Implementation

```python
# pipelines/ui/conftest.py
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
```

## Consequences

### Positive
- ✅ Auto-wait eliminates 80% of flakiness
- ✅ Built-in retry on failure
- ✅ Parallel execution out of the box
- ✅ Trace viewer for debugging
- ✅ Works with CI

### Negative
- ❌ Fewer community resources than Selenium
- ❌ Team learning curve
- ❌ WebKit support less mature

## References
- [Playwright Docs](https://playwright.dev/python/)
- [Why Playwright](https://playwright.dev/python/docs/why-playwright)