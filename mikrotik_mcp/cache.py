"""Command caching for read-only operations."""

from typing import Optional
from datetime import datetime, timedelta

from .logger import get_logger

logger = get_logger(__name__)


class CommandCache:
    """Cache for read-only command results with configurable TTL."""

    def __init__(self):
        self.cache: dict[str, tuple[datetime, str]] = {}
        self.ttl_config: dict[str, int] = {
            "/system resource print": 30,  # 30 seconds
            "/interface print": 60,  # 1 minute
            "/ip address print": 60,
            "/system identity print": 300,  # 5 minutes
            "/ip firewall filter print": 30,
            "/ip dhcp-server lease print": 30,
            "/ip route print": 60,
        }

    def get_cache_key(self, device_id: str, command: str) -> str:
        """Generate cache key from device ID and command."""
        return f"{device_id}:{command}"

    def get(self, device_id: str, command: str) -> Optional[str]:
        """
        Get cached result if not expired.

        Args:
            device_id: Device identifier
            command: RouterOS command

        Returns:
            Cached result if valid, None otherwise
        """
        key = self.get_cache_key(device_id, command)
        if key in self.cache:
            cached_time, result = self.cache[key]
            ttl = self.ttl_config.get(command, 0)
            if ttl > 0 and datetime.now() - cached_time < timedelta(seconds=ttl):
                logger.debug(f"Cache hit for {command} on {device_id}")
                return result
            else:
                # Expired
                del self.cache[key]
                logger.debug(f"Cache expired for {command} on {device_id}")
        return None

    def set(self, device_id: str, command: str, result: str):
        """
        Cache command result.

        Args:
            device_id: Device identifier
            command: RouterOS command
            result: Command output to cache
        """
        if command in self.ttl_config:
            key = self.get_cache_key(device_id, command)
            self.cache[key] = (datetime.now(), result)
            logger.debug(f"Cached result for {command} on {device_id}")

    def invalidate(self, device_id: str, command: Optional[str] = None):
        """
        Invalidate cache for device or specific command.

        Args:
            device_id: Device identifier
            command: Optional specific command to invalidate
        """
        if command:
            key = self.get_cache_key(device_id, command)
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"Invalidated cache for {command} on {device_id}")
        else:
            # Invalidate all for device
            keys_to_delete = [k for k in self.cache.keys() if k.startswith(f"{device_id}:")]
            for k in keys_to_delete:
                del self.cache[k]
            logger.debug(f"Invalidated all cache for {device_id}")

    def clear(self):
        """Clear all cached entries."""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cleared {count} cached entries")

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "total_entries": len(self.cache),
            "cached_commands": list(self.ttl_config.keys()),
            "cache_keys": list(self.cache.keys())
        }
