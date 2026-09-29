# Runbook: CI Test Failures

## Quick Reference

| Error Pattern | Likely Cause | Resolution |
|---------------|--------------|------------|
| `ConnectionError` | Service down | 2 min |
| `401 Unauthorized` | Token expired | 1 min |
| `TimeoutError` | Service slow | 5 min |
| `Flaky test` | Race condition | 10 min |
| `AssertionError` | Regression | 30 min |

## Step 1: Identify Failure Type

### Common Patterns

| Pattern | Meaning | Action |
|---------|---------|--------|
| `ConnectionError` to PostgreSQL | DB not ready | Check docker-compose ps |
| `401 Unauthorized` | Token issues | Refresh AMOCRM_LONG_TOKEN |
| `404 Not Found` | API endpoint changed | Check contract |
| `Timeout` | Service slow | Check service health |
| `StaleElementReference` | UI changed | Update locator |

## Step 2: Reproduce Locally

```bash
# Run only the failing test
pytest tests/test_contacts.py::test_create_contact -v

# Run with full debug output
pytest tests/ -k "test_name" -vv --capture=no

# Run smoke tests
pytest tests/ -m smoke -v
```

## Step 3: Analyze Failure

### Check Test Output

```bash
# Run all tests with verbose
pytest tests/ -v --tb=short

# Run with xdist parallel
pytest tests/ -n auto
```

### Check Service Health

```bash
docker-compose ps
docker-compose logs app --tail=50
```

## Step 4: Fix

### If Flaky Test

```python
# Add explicit wait or retry
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_sometimes_fails():
    pass
```

### If Regression

1. Create issue
2. Fix the bug
3. Add test that catches the bug

### If Environment Issue

```bash
docker-compose restart
# or
docker-compose down -v
docker-compose up -d
```

## Step 5: Verify Fix

```bash
# Run the test again
pytest tests/ -k "test_name" -v

# Commit fix
git commit -m "fix: resolve flaky test_test_name"
```

## Emergency Contacts

| Role | Contact |
|------|---------|
| QA Lead | @ssrjkk |
| On-call | Check PagerDuty |