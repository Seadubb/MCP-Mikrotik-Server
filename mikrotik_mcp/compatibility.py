"""RouterOS 6 and 7 compatibility layer."""

import sys
from typing import Optional
from .models import RouterOSCommand


class RouterOSCompatibility:
    """Handle RouterOS version compatibility."""

    COMMAND_MAP: list[RouterOSCommand] = [
        RouterOSCommand(
            command="/interface print",
            description="List all interfaces",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/ip address print",
            description="List IP addresses",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/ip firewall filter print",
            description="List firewall filter rules",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/ip firewall nat print",
            description="List NAT rules",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/system resource print",
            description="Show system resources",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/system identity print",
            description="Show router identity",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/interface wireless print",
            description="List wireless interfaces (ROS6)",
            supports_ros6=True,
            supports_ros7=False,
            ros7_alternative="/interface wifiwave2 print"
        ),
        RouterOSCommand(
            command="/interface wifiwave2 print",
            description="List WiFi interfaces (ROS7)",
            supports_ros6=False,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/ip dhcp-server print",
            description="List DHCP servers",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/ip dhcp-server lease print",
            description="List DHCP leases",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/ip route print",
            description="List IP routes",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/user print",
            description="List users",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/interface bridge print",
            description="List bridge interfaces",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/queue simple print",
            description="List simple queues",
            supports_ros6=True,
            supports_ros7=True
        ),
        RouterOSCommand(
            command="/log print",
            description="Show system logs",
            supports_ros6=True,
            supports_ros7=True
        ),
    ]

    @classmethod
    def adapt_command(cls, command: str, version: int) -> str:
        """Adapt command for specific RouterOS version."""
        command_info = next((cmd for cmd in cls.COMMAND_MAP if cmd.command == command), None)

        if not command_info:
            return command

        if version == 6 and not command_info.supports_ros6:
            raise ValueError(f'Command "{command}" is not supported in RouterOS 6')

        if version == 7 and not command_info.supports_ros7:
            if command_info.ros7_alternative:
                print(f"Adapting command for ROS7: {command} -> {command_info.ros7_alternative}", file=sys.stderr, flush=True)
                return command_info.ros7_alternative
            raise ValueError(f'Command "{command}" is not supported in RouterOS 7')

        return command

    @classmethod
    def get_supported_commands(cls, version: int) -> list[RouterOSCommand]:
        """Get commands supported by a specific RouterOS version."""
        if version == 6:
            return [cmd for cmd in cls.COMMAND_MAP if cmd.supports_ros6]
        else:
            return [cmd for cmd in cls.COMMAND_MAP if cmd.supports_ros7]

    @classmethod
    def is_command_supported(cls, command: str, version: int) -> bool:
        """Check if a command is supported in a specific RouterOS version."""
        command_info = next((cmd for cmd in cls.COMMAND_MAP if cmd.command == command), None)
        if not command_info:
            return True

        return command_info.supports_ros6 if version == 6 else command_info.supports_ros7
