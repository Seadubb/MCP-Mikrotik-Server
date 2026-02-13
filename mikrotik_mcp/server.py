#!/usr/bin/env python3
"""MikroTik MCP Server - Main server implementation."""

import asyncio
import json
import sys
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from dotenv import load_dotenv

from .device_manager import DeviceManager
from .compatibility import RouterOSCompatibility
from .logger import get_logger
from .exceptions import (
    MikroTikMCPError,
    DeviceNotFoundError,
    NotConnectedError,
    CommandError
)
from .modules import FirewallManager, DHCPManager, VPNManager, ProfileManager

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Initialize device manager
device_manager = DeviceManager()

# Initialize specialized managers
firewall_manager = FirewallManager(device_manager)
dhcp_manager = DHCPManager(device_manager)
vpn_manager = VPNManager(device_manager)
profile_manager = ProfileManager(device_manager)

# Create MCP server
app = Server("mikrotik-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="list_devices",
            description="List all configured MikroTik devices from the devices.json configuration file",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="connect_device",
            description="Connect to a MikroTik device using SSH, Telnet, or API",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID from the configuration",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="disconnect_device",
            description="Disconnect from a MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to disconnect from",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="execute_command",
            description="Execute a RouterOS command on a connected MikroTik device. Automatically adapts commands for RouterOS 6 or 7 compatibility.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to execute the command on",
                    },
                    "command": {
                        "type": "string",
                        "description": 'The RouterOS command to execute (e.g., "/interface print", "/ip address print")',
                    },
                },
                "required": ["device_id", "command"],
            },
        ),
        Tool(
            name="get_connection_status",
            description="Get the connection status of all configured devices",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_device_info",
            description="Get detailed information about a specific device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to get information for",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="get_system_info",
            description="Get system resource information from a connected MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to query",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="get_interfaces",
            description="List all interfaces on a connected MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to query",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="get_ip_addresses",
            description="List all IP addresses configured on a MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to query",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="get_firewall_rules",
            description="List firewall filter rules on a MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to query",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="get_dhcp_leases",
            description="List DHCP leases on a MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to query",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="get_routes",
            description="List IP routes on a MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to query",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="list_supported_commands",
            description="List RouterOS commands supported by a specific RouterOS version (6 or 7)",
            inputSchema={
                "type": "object",
                "properties": {
                    "version": {
                        "type": "number",
                        "description": "RouterOS version (6 or 7)",
                        "enum": [6, 7],
                    },
                },
                "required": ["version"],
            },
        ),
        Tool(
            name="execute_batch_commands",
            description="Execute multiple RouterOS commands in sequence on a device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to execute commands on",
                    },
                    "commands": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of RouterOS commands to execute",
                    },
                    "stop_on_error": {
                        "type": "boolean",
                        "description": "Whether to stop execution if a command fails (default: false)",
                        "default": False,
                    },
                },
                "required": ["device_id", "commands"],
            },
        ),
        Tool(
            name="get_connection_stats",
            description="Get detailed connection statistics for a connected device (uptime, commands executed, response times, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to get statistics for",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="get_fleet_status",
            description="Get status and statistics for all configured devices",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="execute_on_all_devices",
            description="Execute the same command on all connected devices concurrently",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The RouterOS command to execute on all devices",
                    },
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="backup_config",
            description="Export and save device configuration to a backup file",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to backup",
                    },
                    "backup_path": {
                        "type": "string",
                        "description": "Optional custom backup file path (defaults to backups/<device_id>_<timestamp>.rsc)",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="export_config",
            description="Export device configuration as text (without saving to file)",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to export configuration from",
                    },
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="restore_config",
            description="Restore device configuration from a backup file",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device ID to restore to",
                    },
                    "backup_path": {
                        "type": "string",
                        "description": "Path to the backup .rsc file",
                    },
                },
                "required": ["device_id", "backup_path"],
            },
        ),
        Tool(
            name="compare_configs",
            description="Compare configurations between two devices and show differences",
            inputSchema={
                "type": "object",
                "properties": {
                    "device1_id": {
                        "type": "string",
                        "description": "First device ID",
                    },
                    "device2_id": {
                        "type": "string",
                        "description": "Second device ID",
                    },
                },
                "required": ["device1_id", "device2_id"],
            },
        ),
        Tool(
            name="get_command_history",
            description="Get command execution history from audit log",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Filter by device ID (optional)",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of records to return (default: 50)",
                        "default": 50,
                    },
                    "failed_only": {
                        "type": "boolean",
                        "description": "Only show failed commands (default: false)",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="get_device_audit_stats",
            description="Get audit statistics for a specific device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device ID to get statistics for",
                    },
                },
                "required": ["device_id"],
            },
        ),
        # Firewall Management Tools
        Tool(
            name="firewall_add_filter_rule",
            description="Add a firewall filter rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "chain": {"type": "string", "description": "Chain (input, forward, output)"},
                    "action": {"type": "string", "description": "Action (accept, drop, reject, etc.)"},
                    "protocol": {"type": "string", "description": "Protocol (tcp, udp, icmp, etc.)"},
                    "src_address": {"type": "string", "description": "Source IP address/network"},
                    "dst_address": {"type": "string", "description": "Destination IP address/network"},
                    "src_port": {"type": "string", "description": "Source port(s)"},
                    "dst_port": {"type": "string", "description": "Destination port(s)"},
                    "in_interface": {"type": "string", "description": "Input interface"},
                    "out_interface": {"type": "string", "description": "Output interface"},
                    "comment": {"type": "string", "description": "Rule comment"},
                    "disabled": {"type": "boolean", "description": "Disable rule", "default": False},
                },
                "required": ["device_id", "chain", "action"],
            },
        ),
        Tool(
            name="firewall_add_nat_rule",
            description="Add a NAT rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "chain": {"type": "string", "description": "Chain (srcnat, dstnat)"},
                    "action": {"type": "string", "description": "Action (masquerade, dst-nat, src-nat)"},
                    "protocol": {"type": "string", "description": "Protocol"},
                    "src_address": {"type": "string", "description": "Source address"},
                    "dst_address": {"type": "string", "description": "Destination address"},
                    "dst_port": {"type": "string", "description": "Destination port"},
                    "to_addresses": {"type": "string", "description": "NAT target address"},
                    "to_ports": {"type": "string", "description": "NAT target port"},
                    "out_interface": {"type": "string", "description": "Output interface"},
                    "comment": {"type": "string", "description": "Rule comment"},
                },
                "required": ["device_id", "chain", "action"],
            },
        ),
        Tool(
            name="firewall_add_address_list",
            description="Add an address to a firewall address list",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "list_name": {"type": "string", "description": "Address list name"},
                    "address": {"type": "string", "description": "IP address or network"},
                    "comment": {"type": "string", "description": "Comment"},
                    "timeout": {"type": "string", "description": "Timeout (e.g., 1d, 2h)"},
                },
                "required": ["device_id", "list_name", "address"],
            },
        ),
        Tool(
            name="firewall_get_address_list",
            description="Get firewall address list entries",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "list_name": {"type": "string", "description": "Filter by list name (optional)"},
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="firewall_remove_rule",
            description="Remove a firewall filter, NAT, or mangle rule by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "rule_type": {"type": "string", "description": "Rule type (filter, nat, mangle)", "enum": ["filter", "nat", "mangle"]},
                    "rule_id": {"type": "string", "description": "Rule ID or number"},
                },
                "required": ["device_id", "rule_type", "rule_id"],
            },
        ),
        # DHCP Management Tools
        Tool(
            name="dhcp_create_server",
            description="Create a DHCP server",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "name": {"type": "string", "description": "DHCP server name"},
                    "interface": {"type": "string", "description": "Interface to run DHCP on"},
                    "address_pool": {"type": "string", "description": "Address pool name"},
                    "lease_time": {"type": "string", "description": "Lease time (default: 1d)", "default": "1d"},
                },
                "required": ["device_id", "name", "interface", "address_pool"],
            },
        ),
        Tool(
            name="dhcp_add_network",
            description="Add a DHCP network configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "address": {"type": "string", "description": "Network address (e.g., 192.168.1.0/24)"},
                    "gateway": {"type": "string", "description": "Gateway IP"},
                    "dns_server": {"type": "string", "description": "DNS server(s)"},
                    "domain": {"type": "string", "description": "Domain name"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["device_id", "address"],
            },
        ),
        Tool(
            name="dhcp_add_static_lease",
            description="Add a static DHCP lease",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "address": {"type": "string", "description": "IP address to assign"},
                    "mac_address": {"type": "string", "description": "Client MAC address"},
                    "server": {"type": "string", "description": "DHCP server name"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["device_id", "address", "mac_address"],
            },
        ),
        Tool(
            name="dhcp_create_pool",
            description="Create an IP address pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "name": {"type": "string", "description": "Pool name"},
                    "ranges": {"type": "string", "description": "IP ranges (e.g., 192.168.1.100-192.168.1.200)"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["device_id", "name", "ranges"],
            },
        ),
        Tool(
            name="dhcp_get_servers",
            description="Get list of DHCP servers",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                },
                "required": ["device_id"],
            },
        ),
        # VPN Management Tools
        Tool(
            name="vpn_add_ipsec_peer",
            description="Add an IPsec peer",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "name": {"type": "string", "description": "Peer name"},
                    "address": {"type": "string", "description": "Peer IP address"},
                    "secret": {"type": "string", "description": "Pre-shared key"},
                    "exchange_mode": {"type": "string", "description": "Exchange mode (main, aggressive)", "default": "main"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["device_id", "name", "address"],
            },
        ),
        Tool(
            name="vpn_get_ipsec_peers",
            description="Get IPsec peers",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="vpn_add_l2tp_user",
            description="Add an L2TP VPN user",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "name": {"type": "string", "description": "Username"},
                    "password": {"type": "string", "description": "Password"},
                    "local_address": {"type": "string", "description": "Local (server) IP"},
                    "remote_address": {"type": "string", "description": "Remote (client) IP"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["device_id", "name", "password"],
            },
        ),
        Tool(
            name="vpn_configure_l2tp_server",
            description="Configure L2TP server settings",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "enabled": {"type": "boolean", "description": "Enable server", "default": True},
                    "use_ipsec": {"type": "boolean", "description": "Use IPsec", "default": True},
                    "ipsec_secret": {"type": "string", "description": "IPsec pre-shared key"},
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="vpn_get_l2tp_connections",
            description="Get active L2TP connections",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="vpn_add_wireguard_interface",
            description="Add a WireGuard interface",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "name": {"type": "string", "description": "Interface name"},
                    "listen_port": {"type": "number", "description": "UDP listen port"},
                    "private_key": {"type": "string", "description": "Private key (optional)"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["device_id", "name", "listen_port"],
            },
        ),
        Tool(
            name="vpn_add_wireguard_peer",
            description="Add a WireGuard peer",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "interface": {"type": "string", "description": "WireGuard interface name"},
                    "public_key": {"type": "string", "description": "Peer's public key"},
                    "allowed_address": {"type": "string", "description": "Allowed IP addresses"},
                    "endpoint_address": {"type": "string", "description": "Peer endpoint IP"},
                    "endpoint_port": {"type": "number", "description": "Peer endpoint port"},
                    "comment": {"type": "string", "description": "Comment"},
                },
                "required": ["device_id", "interface", "public_key", "allowed_address"],
            },
        ),
        Tool(
            name="vpn_get_wireguard_interfaces",
            description="Get WireGuard interfaces",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                },
                "required": ["device_id"],
            },
        ),
        Tool(
            name="vpn_get_ppp_secrets",
            description="Get PPP secrets (L2TP/PPTP users)",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device ID"},
                    "service": {"type": "string", "description": "Filter by service (l2tp, pptp)"},
                },
                "required": ["device_id"],
            },
        ),
        # Configuration Profile Tools
        Tool(
            name="profile_list",
            description="List available configuration profiles",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category (network, security, vpn, wireless)"},
                },
            },
        ),
        Tool(
            name="profile_get",
            description="Get details of a specific profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "profile_id": {"type": "string", "description": "Profile identifier"},
                    "category": {"type": "string", "description": "Profile category (optional)"},
                },
                "required": ["profile_id"],
            },
        ),
        Tool(
            name="profile_preview",
            description="Preview commands that will be executed for a profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "profile_id": {"type": "string", "description": "Profile identifier"},
                    "variables": {"type": "object", "description": "Variable substitutions (key-value pairs)"},
                    "category": {"type": "string", "description": "Profile category (optional)"},
                },
                "required": ["profile_id"],
            },
        ),
        Tool(
            name="profile_apply",
            description="Apply a configuration profile to a device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device to configure"},
                    "profile_id": {"type": "string", "description": "Profile identifier"},
                    "variables": {"type": "object", "description": "Variable substitutions (key-value pairs)"},
                    "category": {"type": "string", "description": "Profile category (optional)"},
                    "dry_run": {"type": "boolean", "description": "Preview only, don't execute (default: false)", "default": False},
                },
                "required": ["device_id", "profile_id"],
            },
        ),
        Tool(
            name="profile_validate",
            description="Validate a profile structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "profile_id": {"type": "string", "description": "Profile identifier"},
                    "category": {"type": "string", "description": "Profile category (optional)"},
                },
                "required": ["profile_id"],
            },
        ),
        Tool(
            name="profile_save_current",
            description="Save current device configuration as a reusable profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {"type": "string", "description": "Device to export from"},
                    "profile_name": {"type": "string", "description": "Name for the new profile"},
                    "category": {"type": "string", "description": "Profile category (network, security, vpn, wireless)"},
                    "description": {"type": "string", "description": "Profile description"},
                },
                "required": ["device_id", "profile_name", "category", "description"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "list_devices":
            devices = device_manager.list_devices()
            # Convert to dict for JSON serialization, hiding passwords
            devices_data = [
                {
                    **device.model_dump(),
                    "password": "***"
                } for device in devices
            ]
            return [TextContent(type="text", text=json.dumps(devices_data, indent=2))]

        elif name == "connect_device":
            device_id = arguments["device_id"]
            await device_manager.connect_to_device(device_id)
            return [TextContent(type="text", text=f"Successfully connected to device: {device_id}")]

        elif name == "disconnect_device":
            device_id = arguments["device_id"]
            await device_manager.disconnect_from_device(device_id)
            return [TextContent(type="text", text=f"Successfully disconnected from device: {device_id}")]

        elif name == "execute_command":
            device_id = arguments["device_id"]
            command = arguments["command"]
            result = await device_manager.execute_command(device_id, command)

            if result.success:
                return [TextContent(type="text", text=result.output or "Command executed successfully")]
            else:
                return [TextContent(type="text", text=f"Error: {result.error}")]

        elif name == "get_connection_status":
            status = device_manager.get_connection_status()
            return [TextContent(type="text", text=json.dumps(status, indent=2))]

        elif name == "get_device_info":
            device_id = arguments["device_id"]
            device = device_manager.get_device(device_id)
            if not device:
                return [TextContent(type="text", text=f"Device not found: {device_id}")]

            device_data = {**device.model_dump(), "password": "***"}
            return [TextContent(type="text", text=json.dumps(device_data, indent=2))]

        elif name == "get_system_info":
            device_id = arguments["device_id"]
            result = await device_manager.execute_command(device_id, "/system resource print")
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "get_interfaces":
            device_id = arguments["device_id"]
            result = await device_manager.execute_command(device_id, "/interface print")
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "get_ip_addresses":
            device_id = arguments["device_id"]
            result = await device_manager.execute_command(device_id, "/ip address print")
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "get_firewall_rules":
            device_id = arguments["device_id"]
            result = await device_manager.execute_command(device_id, "/ip firewall filter print")
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "get_dhcp_leases":
            device_id = arguments["device_id"]
            result = await device_manager.execute_command(device_id, "/ip dhcp-server lease print")
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "get_routes":
            device_id = arguments["device_id"]
            result = await device_manager.execute_command(device_id, "/ip route print")
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "list_supported_commands":
            version = int(arguments["version"])
            commands = RouterOSCompatibility.get_supported_commands(version)
            commands_data = [cmd.model_dump() for cmd in commands]
            return [TextContent(type="text", text=json.dumps(commands_data, indent=2))]

        elif name == "execute_batch_commands":
            device_id = arguments["device_id"]
            commands = arguments["commands"]
            stop_on_error = arguments.get("stop_on_error", False)

            logger.info(f"Executing batch of {len(commands)} commands on {device_id}")
            results = await device_manager.batch_execute(device_id, commands, stop_on_error)

            # Format results
            output = []
            for i, (cmd, result) in enumerate(zip(commands, results), 1):
                output.append({
                    "command_number": i,
                    "command": cmd,
                    "success": result.success,
                    "output": result.output,
                    "error": result.error
                })

            return [TextContent(type="text", text=json.dumps(output, indent=2))]

        elif name == "get_connection_stats":
            device_id = arguments["device_id"]

            if device_id not in device_manager.connections:
                return [TextContent(type="text", text=f"Error: Device {device_id} is not connected")]

            connection = device_manager.connections[device_id]
            stats = connection.stats.get_stats_dict()

            return [TextContent(type="text", text=json.dumps(stats, indent=2))]

        elif name == "get_fleet_status":
            logger.info("Getting fleet status for all devices")
            fleet_status = await device_manager.get_fleet_status()
            return [TextContent(type="text", text=json.dumps(fleet_status, indent=2))]

        elif name == "execute_on_all_devices":
            command = arguments["command"]

            logger.info(f"Executing command on all connected devices: {command}")
            results = await device_manager.execute_on_all_devices(command)

            # Format results
            output = {}
            for device_id, result in results.items():
                output[device_id] = {
                    "success": result.success,
                    "output": result.output,
                    "error": result.error
                }

            return [TextContent(type="text", text=json.dumps(output, indent=2))]

        elif name == "backup_config":
            device_id = arguments["device_id"]
            backup_path = arguments.get("backup_path")

            logger.info(f"Creating backup for device {device_id}")
            backup_file = await device_manager.backup_config(device_id, backup_path)

            return [TextContent(type="text", text=f"Configuration backed up successfully to: {backup_file}")]

        elif name == "export_config":
            device_id = arguments["device_id"]

            logger.info(f"Exporting configuration for device {device_id}")
            config_text = await device_manager.export_config(device_id)

            return [TextContent(type="text", text=config_text)]

        elif name == "restore_config":
            device_id = arguments["device_id"]
            backup_path = arguments["backup_path"]

            logger.info(f"Restoring configuration to {device_id} from {backup_path}")
            result = await device_manager.restore_config(device_id, backup_path)

            if result.success:
                return [TextContent(type="text", text=f"Success: {result.output}")]
            else:
                return [TextContent(type="text", text=f"Restore completed with errors:\n{result.output}")]

        elif name == "compare_configs":
            device1_id = arguments["device1_id"]
            device2_id = arguments["device2_id"]

            logger.info(f"Comparing configs: {device1_id} vs {device2_id}")
            comparison = await device_manager.compare_configs(device1_id, device2_id)

            return [TextContent(type="text", text=json.dumps(comparison, indent=2))]

        elif name == "get_command_history":
            device_id = arguments.get("device_id")
            limit = arguments.get("limit", 50)
            failed_only = arguments.get("failed_only", False)

            if not device_manager.audit_logger:
                return [TextContent(type="text", text="Error: Audit logging is not enabled")]

            logger.info(f"Getting command history (device={device_id}, limit={limit})")
            history = await device_manager.audit_logger.get_history(
                device_id=device_id,
                limit=limit,
                failed_only=failed_only
            )

            return [TextContent(type="text", text=json.dumps(history, indent=2))]

        elif name == "get_device_audit_stats":
            device_id = arguments["device_id"]

            if not device_manager.audit_logger:
                return [TextContent(type="text", text="Error: Audit logging is not enabled")]

            logger.info(f"Getting audit stats for {device_id}")
            stats = await device_manager.audit_logger.get_device_stats(device_id)

            return [TextContent(type="text", text=json.dumps(stats, indent=2))]

        # Firewall Management Handlers
        elif name == "firewall_add_filter_rule":
            result = await firewall_manager.add_filter_rule(
                device_id=arguments["device_id"],
                chain=arguments["chain"],
                action=arguments["action"],
                protocol=arguments.get("protocol"),
                src_address=arguments.get("src_address"),
                dst_address=arguments.get("dst_address"),
                src_port=arguments.get("src_port"),
                dst_port=arguments.get("dst_port"),
                in_interface=arguments.get("in_interface"),
                out_interface=arguments.get("out_interface"),
                comment=arguments.get("comment"),
                disabled=arguments.get("disabled", False)
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "firewall_add_nat_rule":
            result = await firewall_manager.add_nat_rule(
                device_id=arguments["device_id"],
                chain=arguments["chain"],
                action=arguments["action"],
                protocol=arguments.get("protocol"),
                src_address=arguments.get("src_address"),
                dst_address=arguments.get("dst_address"),
                dst_port=arguments.get("dst_port"),
                to_addresses=arguments.get("to_addresses"),
                to_ports=arguments.get("to_ports"),
                out_interface=arguments.get("out_interface"),
                comment=arguments.get("comment")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "firewall_add_address_list":
            result = await firewall_manager.add_address_list(
                device_id=arguments["device_id"],
                list_name=arguments["list_name"],
                address=arguments["address"],
                comment=arguments.get("comment"),
                timeout=arguments.get("timeout")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "firewall_get_address_list":
            result = await firewall_manager.get_address_list(
                device_id=arguments["device_id"],
                list_name=arguments.get("list_name")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "firewall_remove_rule":
            rule_type = arguments["rule_type"]
            device_id = arguments["device_id"]
            rule_id = arguments["rule_id"]

            if rule_type == "filter":
                result = await firewall_manager.remove_filter_rule(device_id, rule_id)
            elif rule_type == "nat":
                result = await firewall_manager.remove_nat_rule(device_id, rule_id)
            elif rule_type == "mangle":
                result = await firewall_manager.remove_mangle_rule(device_id, rule_id)
            else:
                return [TextContent(type="text", text=f"Error: Unknown rule type: {rule_type}")]

            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        # DHCP Management Handlers
        elif name == "dhcp_create_server":
            result = await dhcp_manager.create_dhcp_server(
                device_id=arguments["device_id"],
                name=arguments["name"],
                interface=arguments["interface"],
                address_pool=arguments["address_pool"],
                lease_time=arguments.get("lease_time", "1d")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "dhcp_add_network":
            result = await dhcp_manager.add_dhcp_network(
                device_id=arguments["device_id"],
                address=arguments["address"],
                gateway=arguments.get("gateway"),
                dns_server=arguments.get("dns_server"),
                domain=arguments.get("domain"),
                comment=arguments.get("comment")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "dhcp_add_static_lease":
            result = await dhcp_manager.add_static_lease(
                device_id=arguments["device_id"],
                address=arguments["address"],
                mac_address=arguments["mac_address"],
                server=arguments.get("server"),
                comment=arguments.get("comment")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "dhcp_create_pool":
            result = await dhcp_manager.create_address_pool(
                device_id=arguments["device_id"],
                name=arguments["name"],
                ranges=arguments["ranges"],
                comment=arguments.get("comment")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "dhcp_get_servers":
            result = await dhcp_manager.get_dhcp_servers(arguments["device_id"])
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        # VPN Management Handlers
        elif name == "vpn_add_ipsec_peer":
            result = await vpn_manager.add_ipsec_peer(
                device_id=arguments["device_id"],
                name=arguments["name"],
                address=arguments["address"],
                secret=arguments.get("secret"),
                exchange_mode=arguments.get("exchange_mode", "main"),
                comment=arguments.get("comment")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "vpn_get_ipsec_peers":
            result = await vpn_manager.get_ipsec_peers(arguments["device_id"])
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "vpn_add_l2tp_user":
            result = await vpn_manager.add_l2tp_user(
                device_id=arguments["device_id"],
                name=arguments["name"],
                password=arguments["password"],
                local_address=arguments.get("local_address"),
                remote_address=arguments.get("remote_address"),
                comment=arguments.get("comment")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "vpn_configure_l2tp_server":
            result = await vpn_manager.configure_l2tp_server(
                device_id=arguments["device_id"],
                enabled=arguments.get("enabled", True),
                use_ipsec=arguments.get("use_ipsec", True),
                ipsec_secret=arguments.get("ipsec_secret")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "vpn_get_l2tp_connections":
            result = await vpn_manager.get_l2tp_connections(arguments["device_id"])
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "vpn_add_wireguard_interface":
            result = await vpn_manager.add_wireguard_interface(
                device_id=arguments["device_id"],
                name=arguments["name"],
                listen_port=arguments["listen_port"],
                private_key=arguments.get("private_key"),
                comment=arguments.get("comment")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "vpn_add_wireguard_peer":
            result = await vpn_manager.add_wireguard_peer(
                device_id=arguments["device_id"],
                interface=arguments["interface"],
                public_key=arguments["public_key"],
                allowed_address=arguments["allowed_address"],
                endpoint_address=arguments.get("endpoint_address"),
                endpoint_port=arguments.get("endpoint_port"),
                comment=arguments.get("comment")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "vpn_get_wireguard_interfaces":
            result = await vpn_manager.get_wireguard_interfaces(arguments["device_id"])
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        elif name == "vpn_get_ppp_secrets":
            result = await vpn_manager.get_ppp_secrets(
                device_id=arguments["device_id"],
                service=arguments.get("service")
            )
            return [TextContent(type="text", text=result.output if result.success else f"Error: {result.error}")]

        # Configuration Profile Handlers
        elif name == "profile_list":
            category = arguments.get("category")
            profiles = profile_manager.list_profiles(category)
            return [TextContent(type="text", text=json.dumps(profiles, indent=2))]

        elif name == "profile_get":
            profile_id = arguments["profile_id"]
            category = arguments.get("category")
            profile = profile_manager.get_profile(profile_id, category)

            if profile:
                return [TextContent(type="text", text=json.dumps(profile, indent=2))]
            else:
                return [TextContent(type="text", text=f"Profile '{profile_id}' not found")]

        elif name == "profile_preview":
            profile_id = arguments["profile_id"]
            variables = arguments.get("variables", {})
            category = arguments.get("category")

            commands = profile_manager.preview_profile_commands(profile_id, variables, category)

            if commands:
                return [TextContent(type="text", text=json.dumps({"commands": commands, "count": len(commands)}, indent=2))]
            else:
                return [TextContent(type="text", text=f"Profile '{profile_id}' not found or contains no commands")]

        elif name == "profile_apply":
            device_id = arguments["device_id"]
            profile_id = arguments["profile_id"]
            variables = arguments.get("variables", {})
            category = arguments.get("category")
            dry_run = arguments.get("dry_run", False)

            logger.info(f"Applying profile '{profile_id}' to device '{device_id}' (dry_run={dry_run})")

            result = await profile_manager.apply_profile(device_id, profile_id, variables, category, dry_run)

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "profile_validate":
            profile_id = arguments["profile_id"]
            category = arguments.get("category")

            validation = profile_manager.validate_profile(profile_id, category)

            return [TextContent(type="text", text=json.dumps(validation, indent=2))]

        elif name == "profile_save_current":
            device_id = arguments["device_id"]
            profile_name = arguments["profile_name"]
            category = arguments["category"]
            description = arguments["description"]

            logger.info(f"Saving device '{device_id}' config as profile '{profile_name}'")

            result = await profile_manager.save_current_as_profile(device_id, profile_name, category, description)

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main() -> None:
    """Main entry point."""
    try:
        # Load device configurations
        logger.info("Loading device configurations...")
        await device_manager.load_devices()
        logger.info("Successfully loaded devices")

        # Run the server
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            logger.info("MikroTik MCP Server running on stdio")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await device_manager.disconnect_all()


def run() -> None:
    """Run the server (entry point for scripts)."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
