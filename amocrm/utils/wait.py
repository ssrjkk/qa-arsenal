"""Wait utilities - ожиданиеCondition."""
import time
from typing import Callable, TypeVar, Optional

from core.logger import get_logger

logger = get_logger("utils.wait")

T = TypeVar("T")


def wait_for(
    condition: Callable[[], bool],
    timeout: float = 30,
    interval: float = 1,
    error_message: str = "Condition not met",
) -> bool:
    """Ждать выполненияcondition."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(interval)
    raise TimeoutError(f"{error_message} after {timeout}s")


def wait_for_response(
    callback: Callable,
    check: Callable[[any], bool],
    timeout: float = 30,
    interval: float = 1,
) -> Optional[any]:
    """Ждать ответа от callback, проверяя через check."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = callback()
            if check(response):
                return response
        except Exception as e:
            logger.debug(f"Callback error: {e}")
        time.sleep(interval)
    return None


def wait_for_service(
    url: str,
    timeout: float = 60,
    interval: float = 2,
) -> bool:
    """Ждать готовности сервиса (HTTP healthcheck)."""
    import requests
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(interval)
    return False


def wait_for_port(
    host: str,
    port: int,
    timeout: float = 30,
) -> bool:
    """Ждать открытия порта."""
    import socket
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False