"""Connection factory for creating device connections."""

from ..models import DeviceConfig, ConnectionType
from .base import DeviceConnection
from .ssh_connection import SSHConnection
from .telnet_connection import TelnetConnection
from .api_connection import APIConnection


class ConnectionFactory:
    """Factory for creating device connections."""

    @staticmethod
    def create_connection(config: DeviceConfig) -> DeviceConnection:
        """Create a connection based on configuration."""
        if config.connection_type == ConnectionType.SSH:
            return SSHConnection(config)
        elif config.connection_type == ConnectionType.TELNET:
            return TelnetConnection(config)
        elif config.connection_type == ConnectionType.API:
            return APIConnection(config)
        else:
            raise ValueError(f"Unsupported connection type: {config.connection_type}")
