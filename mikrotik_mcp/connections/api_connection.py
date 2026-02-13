"""MikroTik API connection handler."""

import asyncio
import shlex
import time
from typing import Optional
import routeros_api

from .base import DeviceConnection
from ..models import DeviceConfig, ConnectionResult
from ..logger import get_logger
from ..retry import retry_decorator
from ..exceptions import ConnectionError, AuthenticationError, NotConnectedError, ParseError

logger = get_logger(__name__)


class APIConnection(DeviceConnection):
    """MikroTik API connection implementation."""

    def __init__(self, config: DeviceConfig):
        super().__init__()  # Initialize stats and health_checker
        self.config = config
        self.connection: Optional[routeros_api.RouterOsApiPool] = None
        self.api: Optional[routeros_api.Api] = None
        self._connected = False

    @retry_decorator(max_attempts=3, initial_delay=1.0)
    async def connect(self) -> None:
        """Establish API connection with retry logic."""
        try:
            logger.info(f"Connecting to {self.config.host} via API")
            loop = asyncio.get_event_loop()

            # Create connection in executor
            self.connection = await loop.run_in_executor(
                None,
                lambda: routeros_api.RouterOsApiPool(
                    host=self.config.host,
                    username=self.config.username,
                    password=self.config.password,
                    port=self.config.port,
                    plaintext_login=True
                )
            )

            self.api = await loop.run_in_executor(None, self.connection.get_api)
            self._connected = True
            self.stats.mark_connected()
            logger.info(f"API connection established to {self.config.host}")

        except Exception as e:
            self._connected = False
            logger.error(f"API connection error for {self.config.host}: {e}")
            if "authentication" in str(e).lower():
                raise AuthenticationError(f"API authentication failed: {str(e)}")
            raise ConnectionError(f"API connection error: {str(e)}")

    async def disconnect(self) -> None:
        """Close API connection."""
        if self.connection:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.connection.disconnect)
            self._connected = False
            logger.info(f"API connection closed to {self.config.host}")

    async def execute(self, command: str) -> ConnectionResult:
        """Execute command via API with stats tracking."""
        if not self.api or not self._connected:
            raise NotConnectedError("API connection not established")

        start_time = time.time()
        try:
            # Parse command to API format with enhanced parser
            command_parts = self._parse_command(command)

            loop = asyncio.get_event_loop()

            # Execute command
            result = await loop.run_in_executor(
                None,
                lambda: self.api.get_resource(command_parts[0]).call(*command_parts[1:])
            )

            # Format output
            output = self._format_output(result)

            response_time = time.time() - start_time
            self.stats.record_command(success=True, response_time=response_time)
            logger.debug(f"API command executed on {self.config.host}: {command}")

            return ConnectionResult(success=True, output=output)

        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"API exec error: {str(e)}"
            self.stats.record_command(success=False, response_time=response_time, error=error_msg)
            logger.error(f"API execution error on {self.config.host}: {e}")
            return ConnectionResult(success=False, error=error_msg)

    def is_connected(self) -> bool:
        """Check if API connection is active."""
        return self._connected and self.api is not None

    def _parse_command(self, command: str) -> list[str]:
        """
        Parse CLI command to API format with enhanced shlex parsing.

        Supports complex commands like:
        /ip firewall filter add chain=forward action=accept src-address=10.0.0.0/8
        """
        command = command.strip()

        # Remove leading slash
        if command.startswith('/'):
            command = command[1:]

        try:
            # Use shlex for proper parsing of quoted values and parameters
            parts = shlex.split(command)
        except ValueError as e:
            logger.error(f"Failed to parse command: {command}")
            raise ParseError(f"Failed to parse command: {str(e)}")

        if not parts:
            return ['/']

        # Separate path components from parameters and actions
        path_parts = []
        params = []

        for part in parts:
            if '=' in part:
                # This is a parameter (key=value)
                params.append(part)
            elif part in ['print', 'add', 'set', 'remove', 'enable', 'disable', 'edit', 'find']:
                # This is an action - goes first in params
                params.insert(0, part)
            else:
                # This is part of the resource path
                path_parts.append(part)

        # Build resource path
        if path_parts:
            path = '/' + '/'.join(path_parts)
        else:
            path = '/'

        return [path] + params

    def _format_output(self, result: any) -> str:
        """Format API result to string."""
        if isinstance(result, list):
            output = []
            for item in result:
                if isinstance(item, dict):
                    output.append(' '.join(f"{k}={v}" for k, v in item.items()))
                else:
                    output.append(str(item))
            return '\n'.join(output)
        elif isinstance(result, dict):
            return '\n'.join(f"{k}={v}" for k, v in result.items())
        else:
            return str(result)
