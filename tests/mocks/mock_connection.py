"""Mock connection objects for testing."""

from mikrotik_mcp.models import ConnectionResult, DeviceConfig
from mikrotik_mcp.connections.base import DeviceConnection


class MockConnection(DeviceConnection):
    """Mock MikroTik connection for testing."""

    def __init__(self, config: DeviceConfig, should_fail: bool = False):
        super().__init__(config)
        self.should_fail = should_fail
        self.executed_commands = []
        self.connect_called = False
        self.disconnect_called = False
        self._mock_responses = {}

    def set_mock_response(self, command: str, output: str):
        """Set a mock response for a specific command."""
        self._mock_responses[command] = output

    async def connect(self) -> None:
        """Mock connect."""
        self.connect_called = True
        if self.should_fail:
            raise Exception("Mock connection failed")
        self.connected = True

    async def disconnect(self) -> None:
        """Mock disconnect."""
        self.disconnect_called = True
        self.connected = False

    async def execute(self, command: str) -> ConnectionResult:
        """Mock execute."""
        self.executed_commands.append(command)

        if self.should_fail:
            return ConnectionResult(
                success=False,
                error="Mock command execution failed"
            )

        # Return mock response if available
        if command in self._mock_responses:
            return ConnectionResult(
                success=True,
                output=self._mock_responses[command]
            )

        # Default mock response
        return ConnectionResult(
            success=True,
            output=f"Mock output for: {command}"
        )

    def is_connected(self) -> bool:
        """Mock is_connected."""
        return self.connected
