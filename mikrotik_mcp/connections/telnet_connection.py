"""Telnet connection handler."""

import asyncio
import time
from typing import Optional
import telnetlib3

from .base import DeviceConnection
from ..models import DeviceConfig, ConnectionResult
from ..logger import get_logger
from ..retry import retry_decorator
from ..exceptions import ConnectionError, AuthenticationError, NotConnectedError, TimeoutError as MCPTimeoutError

logger = get_logger(__name__)


class TelnetConnection(DeviceConnection):
    """Telnet connection implementation."""

    def __init__(self, config: DeviceConfig):
        super().__init__()  # Initialize stats and health_checker
        self.config = config
        self.reader: Optional[telnetlib3.TelnetReader] = None
        self.writer: Optional[telnetlib3.TelnetWriter] = None
        self._connected = False

    @retry_decorator(max_attempts=3, initial_delay=1.0)
    async def connect(self) -> None:
        """Establish Telnet connection with retry logic."""
        try:
            logger.info(f"Connecting to {self.config.host} via Telnet")

            self.reader, self.writer = await asyncio.wait_for(
                telnetlib3.open_connection(
                    self.config.host,
                    self.config.port
                ),
                timeout=self.config.timeout / 1000.0
            )

            # Wait for login prompt
            await self._wait_for_prompt(b'login:')

            # Send username
            self.writer.write(self.config.username + '\n')
            await self.writer.drain()

            # Wait for password prompt
            await self._wait_for_prompt(b'password:')

            # Send password
            self.writer.write(self.config.password + '\n')
            await self.writer.drain()

            # Wait for shell prompt
            await asyncio.sleep(0.5)

            self._connected = True
            self.stats.mark_connected()
            logger.info(f"Telnet connection established to {self.config.host}")

        except asyncio.TimeoutError as e:
            self._connected = False
            logger.error(f"Telnet connection timeout for {self.config.host}")
            raise MCPTimeoutError(f"Telnet connection timeout: {str(e)}")
        except Exception as e:
            self._connected = False
            logger.error(f"Telnet connection error for {self.config.host}: {e}")
            raise ConnectionError(f"Telnet connection error: {str(e)}")

    async def disconnect(self) -> None:
        """Close Telnet connection."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self._connected = False
            logger.info(f"Telnet connection closed to {self.config.host}")

    async def execute(self, command: str) -> ConnectionResult:
        """Execute command via Telnet with stats tracking."""
        if not self.reader or not self.writer or not self._connected:
            raise NotConnectedError("Telnet connection not established")

        start_time = time.time()
        try:
            # Send command
            self.writer.write(command + '\n')
            await self.writer.drain()

            # Read response with timeout
            output = ""
            try:
                output = await asyncio.wait_for(
                    self.reader.read(4096),
                    timeout=self.config.timeout / 1000.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"Telnet read timeout on {self.config.host}")

            response_time = time.time() - start_time
            self.stats.record_command(success=True, response_time=response_time)
            logger.debug(f"Telnet command executed on {self.config.host}: {command}")

            return ConnectionResult(success=True, output=output)

        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"Telnet exec error: {str(e)}"
            self.stats.record_command(success=False, response_time=response_time, error=error_msg)
            logger.error(f"Telnet execution error on {self.config.host}: {e}")
            return ConnectionResult(success=False, error=error_msg)

    def is_connected(self) -> bool:
        """Check if Telnet connection is active."""
        return self._connected and self.writer is not None

    async def _wait_for_prompt(self, prompt: bytes) -> None:
        """Wait for a specific prompt."""
        buffer = b""
        while prompt.lower() not in buffer.lower():
            char = await self.reader.read(1)
            if not char:
                break
            buffer += char.encode() if isinstance(char, str) else char
