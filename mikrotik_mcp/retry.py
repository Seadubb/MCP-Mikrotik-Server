"""Retry logic and connection health utilities."""

import asyncio
import time
from typing import Callable, Any, Optional, Type
from functools import wraps

from .logger import get_logger
from .exceptions import ConnectionError, TimeoutError

logger = get_logger(__name__)


async def retry_async(
    func: Callable,
    *args,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (ConnectionError, TimeoutError),
    **kwargs
) -> Any:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        *args: Positional arguments for func
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry
        **kwargs: Keyword arguments for func

    Returns:
        Result of successful function call

    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    delay = initial_delay

    for attempt in range(1, max_attempts + 1):
        try:
            logger.debug(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
            result = await func(*args, **kwargs)
            if attempt > 1:
                logger.info(f"{func.__name__} succeeded on attempt {attempt}")
            return result

        except exceptions as e:
            last_exception = e
            if attempt == max_attempts:
                logger.error(
                    f"{func.__name__} failed after {max_attempts} attempts: {e}"
                )
                raise

            logger.warning(
                f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                f"Retrying in {delay:.1f}s..."
            )
            await asyncio.sleep(delay)

            # Exponential backoff with max cap
            delay = min(delay * exponential_base, max_delay)

    # Should never reach here, but just in case
    if last_exception:
        raise last_exception


def retry_decorator(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (ConnectionError, TimeoutError)
):
    """
    Decorator for automatic retry with exponential backoff.

    Usage:
        @retry_decorator(max_attempts=3)
        async def connect_to_device(self):
            # connection logic here

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_async(
                func,
                *args,
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                exceptions=exceptions,
                **kwargs
            )
        return wrapper
    return decorator


class ConnectionHealthChecker:
    """Monitor connection health with periodic keepalive checks."""

    def __init__(
        self,
        check_interval: float = 60.0,
        timeout: float = 10.0
    ):
        """
        Initialize health checker.

        Args:
            check_interval: Seconds between health checks
            timeout: Timeout for health check commands
        """
        self.check_interval = check_interval
        self.timeout = timeout
        self.last_check: Optional[float] = None
        self.is_healthy: bool = True
        self._check_task: Optional[asyncio.Task] = None

    async def check_health(self, connection) -> bool:
        """
        Perform health check on connection.

        Args:
            connection: Device connection object

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Simple command that should always work
            await asyncio.wait_for(
                connection.execute("/system/identity/print"),
                timeout=self.timeout
            )
            self.is_healthy = True
            self.last_check = time.time()
            logger.debug(f"Health check passed for connection")
            return True

        except Exception as e:
            self.is_healthy = False
            logger.warning(f"Health check failed: {e}")
            return False

    async def start_monitoring(self, connection):
        """
        Start periodic health monitoring.

        Args:
            connection: Device connection to monitor
        """
        logger.info(
            f"Starting health monitoring (interval: {self.check_interval}s)"
        )

        while True:
            await asyncio.sleep(self.check_interval)
            await self.check_health(connection)

    def start_background_monitoring(self, connection):
        """
        Start health monitoring in background task.

        Args:
            connection: Device connection to monitor
        """
        if self._check_task is None or self._check_task.done():
            self._check_task = asyncio.create_task(
                self.start_monitoring(connection)
            )

    async def stop_monitoring(self):
        """Stop background health monitoring."""
        if self._check_task and not self._check_task.done():
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
            logger.info("Health monitoring stopped")


class ConnectionStats:
    """Track connection statistics."""

    def __init__(self):
        """Initialize connection statistics."""
        self.connected_at: Optional[float] = None
        self.commands_executed: int = 0
        self.commands_failed: int = 0
        self.last_command_at: Optional[float] = None
        self.last_error: Optional[str] = None
        self.response_times: list[float] = []
        self.max_response_times: int = 100  # Keep last 100 response times

    def mark_connected(self):
        """Mark connection as established."""
        self.connected_at = time.time()

    def record_command(self, success: bool, response_time: float, error: Optional[str] = None):
        """
        Record command execution.

        Args:
            success: Whether command succeeded
            response_time: Time taken in seconds
            error: Error message if failed
        """
        self.last_command_at = time.time()

        if success:
            self.commands_executed += 1
        else:
            self.commands_failed += 1
            self.last_error = error

        # Track response times (keep last N)
        self.response_times.append(response_time)
        if len(self.response_times) > self.max_response_times:
            self.response_times.pop(0)

    def get_uptime(self) -> Optional[float]:
        """Get connection uptime in seconds."""
        if self.connected_at is None:
            return None
        return time.time() - self.connected_at

    def get_avg_response_time(self) -> Optional[float]:
        """Get average response time in seconds."""
        if not self.response_times:
            return None
        return sum(self.response_times) / len(self.response_times)

    def get_stats_dict(self) -> dict:
        """
        Get statistics as dictionary.

        Returns:
            Dictionary with all statistics
        """
        uptime = self.get_uptime()
        avg_response = self.get_avg_response_time()

        return {
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime) if uptime else None,
            "commands_executed": self.commands_executed,
            "commands_failed": self.commands_failed,
            "success_rate": (
                self.commands_executed / (self.commands_executed + self.commands_failed)
                if (self.commands_executed + self.commands_failed) > 0
                else 0.0
            ),
            "avg_response_time_ms": round(avg_response * 1000, 2) if avg_response else None,
            "last_error": self.last_error,
            "last_command_at": self.last_command_at,
        }

    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """Format uptime as human-readable string."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")

        return " ".join(parts)
