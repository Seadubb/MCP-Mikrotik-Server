"""Base connection interface."""

from abc import ABC, abstractmethod
from ..models import ConnectionResult
from ..retry import ConnectionHealthChecker, ConnectionStats


class DeviceConnection(ABC):
    """Abstract base class for device connections."""

    def __init__(self):
        """Initialize connection with stats and health checker."""
        self.stats = ConnectionStats()
        self.health_checker = ConnectionHealthChecker()

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the device."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the device."""
        pass

    @abstractmethod
    async def execute(self, command: str) -> ConnectionResult:
        """Execute a command on the device."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connection is active."""
        pass
