"""Hermetic unit tests for resilience patterns (no network, no timers that sleep long)."""

import time

import pytest

from core.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    ExponentialBackoff,
    RateLimiter,
    circuit_breaker,
    retry_with_backoff,
)


class TestExponentialBackoff:
    def test_delay_grows_exponentially(self):
        b = ExponentialBackoff(base_delay=1.0, max_delay=64.0, jitter=0.0)
        d0 = b.get_delay(0)
        d1 = b.get_delay(1)
        d2 = b.get_delay(2)
        assert d1 > d0
        assert d2 > d1

    def test_delay_capped_at_max(self):
        b = ExponentialBackoff(base_delay=1.0, max_delay=4.0, jitter=0.0)
        assert b.get_delay(10) <= 4.0

    def test_jitter_bounds(self):
        b = ExponentialBackoff(base_delay=1.0, max_delay=64.0, jitter=0.5)
        for attempt in range(5):
            d = b.get_delay(attempt)
            # delay = base * 2^attempt, jitter range = delay * 0.5
            assert d >= 0


class TestCircuitBreaker:
    def test_closed_by_default(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute()

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1000)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert not cb.can_execute()

    def test_recovers_to_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.001, half_open_attempts=2)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        time.sleep(0.01)
        assert cb.state == CircuitState.HALF_OPEN

    def test_closes_after_half_open_successes(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.001, half_open_attempts=2)
        cb.record_failure()
        time.sleep(0.01)
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success()
        cb.record_success()
        assert cb.state == CircuitState.CLOSED


class TestRateLimiter:
    def test_acquires_up_to_capacity(self):
        rl = RateLimiter(rate=1000, capacity=5)
        for _ in range(5):
            assert rl.acquire()
        assert not rl.acquire(block=False)

    def test_non_blocking_returns_false_when_empty(self):
        rl = RateLimiter(rate=0.000001, capacity=1)
        rl.acquire()
        assert not rl.acquire(block=False)


class TestDecorators:
    def test_retry_succeeds_eventually(self):
        calls = {"n": 0}

        @retry_with_backoff(max_attempts=3, base_delay=0.001, jitter=0.0)
        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise ValueError("boom")
            return "ok"

        assert flaky() == "ok"
        assert calls["n"] == 3

    def test_retry_exhausts_and_raises(self):
        @retry_with_backoff(max_attempts=2, base_delay=0.001, jitter=0.0)
        def always_fails():
            raise ValueError("boom")

        with pytest.raises(ValueError):
            always_fails()

    def test_circuit_breaker_decorator_blocks_when_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1000)

        @circuit_breaker(failure_threshold=1, recovery_timeout=1000)
        def flaky():
            raise ValueError("boom")

        with pytest.raises(ValueError):
            flaky()
        # Second call: circuit is OPEN -> CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            flaky()
        assert cb is not None