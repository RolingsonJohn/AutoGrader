"""
Utilities module providing resilience patterns and helper functions.
Includes circuit breaker, retry logic, and health checking mechanisms.
"""

import asyncio
import time
import logging
from enum import Enum
from typing import Callable, Any, Optional, Type
from functools import wraps
from http import HTTPStatus


logger = logging.getLogger(__name__)


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for fault tolerance.
    Prevents cascading failures by monitoring and limiting requests.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: Circuit open or underlying error
        """
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info("Circuit breaker reset to CLOSED state")
            return result
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.error(
                    f"Circuit breaker opened after {
                        self.failure_count} failures")

            raise


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 0.3,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for backoff delay
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(
                            f"Function {
                                func.__name__} failed after {max_retries} attempts")
                        raise

                    delay = backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}, "
                        f"retrying in {delay}s: {str(e)}"
                    )
                    await asyncio.sleep(delay)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(
                            f"Function {
                                func.__name__} failed after {max_retries} attempts")
                        raise

                    delay = backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}, "
                        f"retrying in {delay}s: {str(e)}"
                    )
                    time.sleep(delay)

        return async_wrapper if asyncio.iscoroutinefunction(
            func) else sync_wrapper

    return decorator


class HealthChecker:
    """Health checking utility for service dependencies."""

    @staticmethod
    async def check_service(
        url: str,
        timeout: int = 5,
        expected_status: HTTPStatus = HTTPStatus.OK
    ) -> dict:
        """
        Check health of a service endpoint.

        Args:
            url: Service URL to check
            timeout: Request timeout in seconds
            expected_status: Expected HTTP status

        Returns:
            Health check result
        """
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as resp:
                    is_healthy = resp.status == expected_status
                    return {
                        "service": url,
                        "healthy": is_healthy,
                        "status": resp.status,
                        "timestamp": time.time()
                    }
        except asyncio.TimeoutError:
            return {
                "service": url,
                "healthy": False,
                "status": None,
                "error": "Timeout",
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "service": url,
                "healthy": False,
                "status": None,
                "error": str(e),
                "timestamp": time.time()
            }

    @staticmethod
    async def check_multiple(
        services: dict[str, str],
        timeout: int = 5
    ) -> dict[str, dict]:
        """
        Check health of multiple services concurrently.

        Args:
            services: Dict mapping service names to URLs
            timeout: Request timeout in seconds

        Returns:
            Health check results for all services
        """
        tasks = [
            HealthChecker.check_service(url, timeout)
            for url in services.values()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            name: result
            for name, result in zip(services.keys(), results)
        }
