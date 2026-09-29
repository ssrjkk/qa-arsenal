from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from utils.logger import logger

F = TypeVar("F", bound=Callable[..., Any])


class RetryableError(Exception):
    pass


class NonRetryableError(Exception):
    pass


def create_retry_decorator(
    max_attempts: int = 3,
    delay: float = 1.0,
    retryable_exceptions: tuple[type[Exception], ...] | None = None,
) -> Callable[[F], F]:
    if retryable_exceptions is None:
        retryable_exceptions = (RetryableError,)

    def before_sleep(retry_state: Any) -> None:
        exc = retry_state.outcome.exception() if retry_state.outcome else "Unknown"
        logger.warning(
            f"Повторная попытка {retry_state.attempt_number}/{max_attempts} после ошибки: {exc}"
        )

    return retry(  # type: ignore[no-any-return]
        stop=stop_after_attempt(max_attempts),
        wait=wait_fixed(delay),
        retry=retry_if_exception_type(retryable_exceptions),
        reraise=True,
        before_sleep=before_sleep,
    )


def retry_on_5xx_or_timeout(
    max_attempts: int = 3,
    delay: float = 1.0,
) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        def before_sleep(retry_state: Any) -> None:
            exc_type = (
                type(retry_state.outcome.exception()).__name__
                if retry_state.outcome
                else "Unknown"
            )
            logger.warning(f"Попытка {retry_state.attempt_number}/{max_attempts}: {exc_type}")

        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_fixed(delay),
            retry=retry_if_exception_type((TimeoutError, ConnectionError)),
            reraise=True,
            before_sleep=before_sleep,
        )
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
