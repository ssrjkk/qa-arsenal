"""Resilience patterns: retry, circuit breaker, timeout."""

import time
import random
import logging
from functools import wraps
from typing import Callable, Any, Optional
from threading import Lock

logger = logging.getLogger(__name__)


class ExponentialBackoff:
    """Exponential backoff with jitter - prevents thundering herd."""

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponent: float = 2.0,
        jitter: float = 0.3,
    ):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponent = exponent
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and random jitter."""
        delay = min(self.base_delay * (self.exponent**attempt), self.max_delay)
        jitter_range = delay * self.jitter
        return delay + random.uniform(-jitter_range, jitter_range)


class CircuitState:
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """Circuit breaker pattern - fail fast when service is down."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_attempts: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_attempts = half_open_attempts

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_successes = 0
        self._lock = Lock()

    @property
    def state(self) -> str:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if time.time() - self._last_failure_time >= self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_successes = 0
            return self._state

    def record_success(self):
        """Record successful call."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_successes += 1
                if self._half_open_successes >= self.half_open_attempts:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info("Circuit breaker CLOSED - recovered")
            else:
                self._failure_count = max(0, self._failure_count - 1)

    def record_failure(self):
        """Record failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning("Circuit breaker OPEN - half-open test failed")
            elif self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(f"Circuit breaker OPEN - {self._failure_count} failures")

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        return self.state != CircuitState.OPEN


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponent: float = 2.0,
    jitter: float = 0.3,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """
    Decorator for retry with exponential backoff and jitter.

    Usage:
        @retry_with_backoff(max_attempts=3, base_delay=1.0)
        def unreliable_api_call():
            ...
    """
    backoff = ExponentialBackoff(base_delay, max_delay, exponent, jitter)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    delay = backoff.get_delay(attempt)

                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Retry {attempt + 1}/{max_attempts} for {func.__name__} after {delay:.2f}s: {e}"
                        )
                        if on_retry:
                            on_retry(attempt, e)
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")

            raise last_exception

        return wrapper

    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for circuit breaker pattern.

    Usage:
        @circuit_breaker(failure_threshold=5, recovery_timeout=30)
        def external_service_call():
            ...
    """
    circuit = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not circuit.can_execute():
                raise CircuitBreakerOpenError(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                circuit.record_success()
                return result
            except exceptions:
                circuit.record_failure()
                raise

        return wrapper

    return decorator


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


class TimeoutError(Exception):
    """Custom timeout error."""

    pass


def timeout(seconds: float):
    """
    Decorator for function timeout.

    Usage:
        @timeout(30)
        def slow_operation():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds}s")

            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))

            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            return result

        return wrapper

    return decorator


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = Lock()

    def acquire(self, tokens: int = 1, block: bool = True, timeout: float = None) -> bool:
        """Acquire tokens, return True if successful."""
        start = time.time()

        while True:
            with self._lock:
                now = time.time()
                elapsed = now - self.last_update
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True

            if not block:
                return False

            if timeout and (time.time() - start) >= timeout:
                return False

            time.sleep(0.01)


# Global instances
http_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
db_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
rate_limiter = RateLimiter(rate=10, capacity=20)
