"""SSH connection handler."""

import asyncio
import time
from typing import Optional
import paramiko

from .base import DeviceConnection
from ..models import DeviceConfig, ConnectionResult
from ..logger import get_logger
from ..retry import retry_decorator
from ..exceptions import ConnectionError, AuthenticationError, NotConnectedError

logger = get_logger(__name__)


class SSHConnection(DeviceConnection):
    """SSH connection implementation using Paramiko."""

    def __init__(self, config: DeviceConfig):
        super().__init__()  # Initialize stats and health_checker
        self.config = config
        self.client: Optional[paramiko.SSHClient] = None
        self._connected = False

    @retry_decorator(max_attempts=3, initial_delay=1.0)
    async def connect(self) -> None:
        """Establish SSH connection with retry logic."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Build connection kwargs
            connect_kwargs = {
                "hostname": self.config.host,
                "port": self.config.port,
                "username": self.config.username,
                "timeout": self.config.timeout / 1000.0,
            }

            # SSH key auth or password auth
            if self.config.ssh_key:
                logger.info(f"Connecting to {self.config.host} via SSH with key auth")
                connect_kwargs["key_filename"] = self.config.ssh_key.key_path
                if self.config.ssh_key.key_passphrase:
                    connect_kwargs["passphrase"] = self.config.ssh_key.key_passphrase
            else:
                logger.info(f"Connecting to {self.config.host} via SSH with password auth")
                connect_kwargs["password"] = self.config.password
                connect_kwargs["look_for_keys"] = False
                connect_kwargs["allow_agent"] = False

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.connect(**connect_kwargs)
            )

            self._connected = True
            self.stats.mark_connected()
            logger.info(f"SSH connection established to {self.config.host}")

        except paramiko.AuthenticationException as e:
            self._connected = False
            logger.error(f"SSH authentication failed for {self.config.host}: {e}")
            raise AuthenticationError(f"SSH authentication failed: {str(e)}")
        except Exception as e:
            self._connected = False
            logger.error(f"SSH connection error for {self.config.host}: {e}")
            raise ConnectionError(f"SSH connection error: {str(e)}")

    async def disconnect(self) -> None:
        """Close SSH connection."""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info(f"SSH connection closed to {self.config.host}")

    async def execute(self, command: str) -> ConnectionResult:
        """Execute command via SSH with stats tracking."""
        if not self.client or not self._connected:
            raise NotConnectedError("SSH connection not established")

        start_time = time.time()
        try:
            loop = asyncio.get_event_loop()
            stdin, stdout, stderr = await loop.run_in_executor(
                None,
                self.client.exec_command,
                command
            )

            # Read output
            output = await loop.run_in_executor(None, stdout.read)
            error = await loop.run_in_executor(None, stderr.read)
            exit_status = stdout.channel.recv_exit_status()

            response_time = time.time() - start_time
            success = (exit_status == 0)

            result = ConnectionResult(
                success=success,
                output=output.decode('utf-8') if output else None,
                error=error.decode('utf-8') if error else None
            )

            # Record stats
            self.stats.record_command(
                success=success,
                response_time=response_time,
                error=result.error if not success else None
            )

            if success:
                logger.debug(f"SSH command executed successfully on {self.config.host}: {command}")
            else:
                logger.warning(f"SSH command failed on {self.config.host}: {command}")

            return result

        except Exception as e:
            response_time = time.time() - start_time
            error_msg = f"SSH exec error: {str(e)}"
            self.stats.record_command(success=False, response_time=response_time, error=error_msg)
            logger.error(f"SSH execution error on {self.config.host}: {e}")
            return ConnectionResult(success=False, error=error_msg)

    def is_connected(self) -> bool:
        """Check if SSH connection is active."""
        return (
            self._connected
            and self.client is not None
            and self.client.get_transport() is not None
            and self.client.get_transport().is_active()
        )
