"""Retry utilities."""
import time
import functools
from typing import Callable, TypeVar, ParamSpec

from core.logger import get_logger

logger = get_logger("utils.retry")

T = TypeVar("T")
P = ParamSpec("P")


def retry(
    max_attempts: int = 3,
    min_wait: float = 1,
    max_wait: float = 10,
    exceptions: tuple = (Exception,),
) -> Callable:
    """Декоратор для повторных попыток."""
    
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    wait_time = min(min_wait * (2 ** (attempt - 1)), max_wait)
                    logger.warning(f"{func.__name__} attempt {attempt} failed, retry in {wait_time}s: {e}")
                    time.sleep(wait_time)
            raise RuntimeError("Unreachable")
        return wrapper
    return decorator


def retry_with_result(
    max_attempts: int = 3,
    delay: float = 1,
    exceptions: tuple = (Exception,),
):
    """Retry с условием на result."""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_result = None
            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                    last_result = result
                except exceptions as e:
                    logger.warning(f"Attempt {attempt} error: {e}")
                
                if attempt < max_attempts:
                    time.sleep(delay)
            
            return last_result
        return wrapper
    return decorator