"""Device manager for handling multiple MikroTik devices."""

import json
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from .models import DeviceConfig, DevicesConfig, ConnectionResult
from .connections import DeviceConnection, ConnectionFactory
from .compatibility import RouterOSCompatibility
from .cache import CommandCache
from .audit import AuditLogger
from .logger import get_logger
from .exceptions import DeviceNotFoundError, NotConnectedError, ConfigurationError

logger = get_logger(__name__)


class DeviceManager:
    """Manage connections to multiple MikroTik devices."""

    def __init__(self, config_path: Optional[str] = None, enable_audit: bool = True):
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to devices.json in the project root
            package_dir = Path(__file__).parent
            project_root = package_dir.parent
            self.config_path = project_root / "devices.json"

        self.devices: dict[str, DeviceConfig] = {}
        self.connections: dict[str, DeviceConnection] = {}
        self.cache = CommandCache()
        self.audit_logger = AuditLogger() if enable_audit else None
        logger.info(f"DeviceManager initialized with config path: {self.config_path}")

    async def load_devices(self) -> None:
        """Load device configurations from file."""
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)

            config = DevicesConfig(**config_data)
            self.devices = {device.id: device for device in config.devices}

            logger.info(f"Loaded {len(self.devices)} devices from {self.config_path}")

            # Initialize audit database if enabled
            if self.audit_logger:
                await self.audit_logger.init_db()
                logger.info("Audit logging enabled")

        except FileNotFoundError:
            error_msg = f"Device configuration not found at {self.config_path.absolute()}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except Exception as e:
            error_msg = f"Failed to load device configuration: {str(e)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)

    def get_device(self, device_id: str) -> Optional[DeviceConfig]:
        """Get device configuration by ID."""
        return self.devices.get(device_id)

    def list_devices(self) -> list[DeviceConfig]:
        """List all configured devices."""
        return list(self.devices.values())

    async def connect_to_device(self, device_id: str) -> None:
        """Connect to a specific device."""
        device = self.devices.get(device_id)
        if not device:
            raise DeviceNotFoundError(f'Device with ID "{device_id}" not found')

        if device_id in self.connections:
            existing_connection = self.connections[device_id]
            if existing_connection.is_connected():
                logger.info(f"Already connected to device: {device_id}")
                return

        logger.info(f"Connecting to device: {device_id}")
        connection = ConnectionFactory.create_connection(device)
        await connection.connect()
        self.connections[device_id] = connection

    async def disconnect_from_device(self, device_id: str) -> None:
        """Disconnect from a specific device."""
        connection = self.connections.get(device_id)
        if connection:
            logger.info(f"Disconnecting from device: {device_id}")
            await connection.disconnect()
            del self.connections[device_id]
            # Clear cache for this device
            self.cache.invalidate(device_id)

    async def execute_command(self, device_id: str, command: str, use_cache: bool = True) -> ConnectionResult:
        """Execute a command on a specific device with optional caching."""
        device = self.devices.get(device_id)
        if not device:
            raise DeviceNotFoundError(f'Device with ID "{device_id}" not found')

        connection = self.connections.get(device_id)
        if not connection or not connection.is_connected():
            raise NotConnectedError(f"Not connected to device: {device_id}. Please connect first.")

        # Adapt command for RouterOS version
        adapted_command = RouterOSCompatibility.adapt_command(command, device.routeros_version)

        # Check cache for read-only commands
        if use_cache:
            cached = self.cache.get(device_id, adapted_command)
            if cached:
                logger.debug(f"Cache hit for {adapted_command} on {device_id}")
                return ConnectionResult(success=True, output=cached)

        # Execute command and track timing
        start_time = time.time()
        result = await connection.execute(adapted_command)
        execution_time_ms = (time.time() - start_time) * 1000

        # Cache successful read-only results
        if result.success and use_cache:
            self.cache.set(device_id, adapted_command, result.output or "")

        # Log to audit
        if self.audit_logger:
            # Handle connection_type which may be string or enum depending on use_enum_values
            conn_type = device.connection_type if isinstance(device.connection_type, str) else device.connection_type.value
            await self.audit_logger.log_command(
                device_id=device_id,
                command=adapted_command,
                success=result.success,
                output=result.output,
                error=result.error,
                execution_time_ms=execution_time_ms,
                device_name=device.name,
                device_host=device.host,
                connection_type=conn_type
            )

        return result

    async def batch_execute(
        self,
        device_id: str,
        commands: list[str],
        stop_on_error: bool = False
    ) -> list[ConnectionResult]:
        """Execute multiple commands in sequence."""
        logger.info(f"Batch executing {len(commands)} commands on {device_id}")
        results = []

        for i, cmd in enumerate(commands):
            try:
                result = await self.execute_command(device_id, cmd, use_cache=False)
                results.append(result)

                if stop_on_error and not result.success:
                    logger.warning(f"Batch execution stopped at command {i+1}/{len(commands)} due to error")
                    break
            except Exception as e:
                error_result = ConnectionResult(success=False, error=str(e))
                results.append(error_result)
                if stop_on_error:
                    logger.warning(f"Batch execution stopped at command {i+1}/{len(commands)} due to exception")
                    break

        logger.info(f"Batch execution complete: {sum(1 for r in results if r.success)}/{len(results)} successful")
        return results

    async def execute_on_all_devices(self, command: str) -> dict[str, ConnectionResult]:
        """Execute command on all connected devices."""
        logger.info(f"Executing command on all connected devices: {command}")
        results = {}

        for device_id in list(self.connections.keys()):
            try:
                result = await self.execute_command(device_id, command, use_cache=False)
                results[device_id] = result
            except Exception as e:
                logger.error(f"Failed to execute on {device_id}: {e}")
                results[device_id] = ConnectionResult(success=False, error=str(e))

        return results

    async def get_fleet_status(self) -> list[dict]:
        """Get status of all devices (connected and disconnected)."""
        statuses = []

        for device_id, device in self.devices.items():
            is_connected = device_id in self.connections
            # Handle connection_type which may be string or enum depending on use_enum_values
            conn_type = device.connection_type if isinstance(device.connection_type, str) else device.connection_type.value
            status = {
                "device_id": device_id,
                "name": device.name,
                "host": device.host,
                "connection_type": conn_type,
                "connected": is_connected,
            }

            if is_connected:
                connection = self.connections[device_id]
                stats = connection.stats.get_stats_dict()
                status.update(stats)

            statuses.append(status)

        return statuses

    async def backup_config(self, device_id: str, backup_path: Optional[str] = None) -> str:
        """Export device configuration to file."""
        logger.info(f"Backing up configuration for {device_id}")
        result = await self.execute_command(device_id, "/export", use_cache=False)

        if not result.success:
            raise Exception(f"Backup failed: {result.error}")

        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/{device_id}_{timestamp}.rsc"

        backup_file = Path(backup_path)
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        backup_file.write_text(result.output or "", encoding='utf-8')

        logger.info(f"Configuration backed up to {backup_file}")
        return str(backup_file)

    async def export_config(self, device_id: str) -> str:
        """Get config export as string."""
        result = await self.execute_command(device_id, "/export", use_cache=False)
        if not result.success:
            raise Exception(f"Export failed: {result.error}")
        return result.output or ""

    async def restore_config(self, device_id: str, backup_path: str) -> ConnectionResult:
        """
        Restore configuration from backup file.

        Args:
            device_id: Device to restore to
            backup_path: Path to backup .rsc file

        Returns:
            ConnectionResult with restoration status
        """
        logger.info(f"Restoring configuration to {device_id} from {backup_path}")

        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise ConfigurationError(f"Backup file not found: {backup_path}")

        # Read backup file
        config_content = backup_file.read_text(encoding='utf-8')

        # Execute line by line (RouterOS /import doesn't work reliably via SSH/API)
        lines = config_content.split('\n')
        total_lines = 0
        successful_lines = 0
        failed_lines = 0
        errors = []

        for line in lines:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            total_lines += 1

            try:
                result = await self.execute_command(device_id, line, use_cache=False)
                if result.success:
                    successful_lines += 1
                else:
                    failed_lines += 1
                    errors.append(f"Line {total_lines}: {result.error}")
                    logger.warning(f"Failed to restore line: {line[:50]}... - {result.error}")
            except Exception as e:
                failed_lines += 1
                errors.append(f"Line {total_lines}: {str(e)}")
                logger.warning(f"Exception restoring line: {line[:50]}... - {e}")

        summary = f"Restored {successful_lines}/{total_lines} commands successfully"
        if failed_lines > 0:
            summary += f", {failed_lines} failed"

        logger.info(f"Restore complete: {summary}")

        return ConnectionResult(
            success=(failed_lines == 0),
            output=summary + (f"\n\nErrors:\n" + "\n".join(errors[:10]) if errors else "")
        )

    async def compare_configs(self, device1_id: str, device2_id: str) -> dict:
        """
        Compare configurations of two devices.

        Args:
            device1_id: First device ID
            device2_id: Second device ID

        Returns:
            Dictionary with comparison results including diff
        """
        logger.info(f"Comparing configurations: {device1_id} vs {device2_id}")

        # Export both configs
        config1 = await self.export_config(device1_id)
        config2 = await self.export_config(device2_id)

        # Generate unified diff
        import difflib
        diff = list(difflib.unified_diff(
            config1.splitlines(keepends=True),
            config2.splitlines(keepends=True),
            fromfile=f"{device1_id} config",
            tofile=f"{device2_id} config",
            lineterm=''
        ))

        # Calculate similarity
        similarity = difflib.SequenceMatcher(None, config1, config2).ratio()

        return {
            "device1_id": device1_id,
            "device2_id": device2_id,
            "identical": len(diff) == 0,
            "similarity_percent": round(similarity * 100, 2),
            "diff_lines": len(diff),
            "diff": ''.join(diff) if diff else "Configurations are identical",
            "config1_lines": len(config1.splitlines()),
            "config2_lines": len(config2.splitlines())
        }

    async def disconnect_all(self) -> None:
        """Disconnect from all devices."""
        logger.info("Disconnecting from all devices")
        for device_id in list(self.connections.keys()):
            await self.disconnect_from_device(device_id)

    def is_connected(self, device_id: str) -> bool:
        """Check if connected to a device."""
        connection = self.connections.get(device_id)
        return connection.is_connected() if connection else False

    def get_connection_status(self) -> dict[str, bool]:
        """Get connection status for all devices."""
        return {device_id: self.is_connected(device_id) for device_id in self.devices.keys()}
