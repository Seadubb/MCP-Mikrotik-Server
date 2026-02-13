"""Firewall management module for MikroTik devices."""

from typing import Optional, TYPE_CHECKING
from ..logger import get_logger
from ..models import ConnectionResult

if TYPE_CHECKING:
    from ..device_manager import DeviceManager

logger = get_logger(__name__)


class FirewallManager:
    """Manage firewall operations on MikroTik devices."""

    def __init__(self, device_manager: 'DeviceManager'):
        self.device_manager = device_manager

    async def add_filter_rule(
        self,
        device_id: str,
        chain: str,
        action: str,
        protocol: Optional[str] = None,
        src_address: Optional[str] = None,
        dst_address: Optional[str] = None,
        src_port: Optional[str] = None,
        dst_port: Optional[str] = None,
        in_interface: Optional[str] = None,
        out_interface: Optional[str] = None,
        comment: Optional[str] = None,
        disabled: bool = False
    ) -> ConnectionResult:
        """
        Add a firewall filter rule.

        Args:
            device_id: Device to configure
            chain: Chain name (input, forward, output)
            action: Action to take (accept, drop, reject, etc.)
            protocol: Protocol (tcp, udp, icmp, etc.)
            src_address: Source IP address/network
            dst_address: Destination IP address/network
            src_port: Source port(s)
            dst_port: Destination port(s)
            in_interface: Input interface
            out_interface: Output interface
            comment: Rule comment
            disabled: Whether rule is disabled
        """
        logger.info(f"Adding firewall filter rule to {device_id}: chain={chain}, action={action}")

        cmd_parts = ["/ip firewall filter add"]
        cmd_parts.append(f"chain={chain}")
        cmd_parts.append(f"action={action}")

        if protocol:
            cmd_parts.append(f"protocol={protocol}")
        if src_address:
            cmd_parts.append(f"src-address={src_address}")
        if dst_address:
            cmd_parts.append(f"dst-address={dst_address}")
        if src_port:
            cmd_parts.append(f"src-port={src_port}")
        if dst_port:
            cmd_parts.append(f"dst-port={dst_port}")
        if in_interface:
            cmd_parts.append(f"in-interface={in_interface}")
        if out_interface:
            cmd_parts.append(f"out-interface={out_interface}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def remove_filter_rule(self, device_id: str, rule_id: str) -> ConnectionResult:
        """
        Remove a firewall filter rule by ID.

        Args:
            device_id: Device to configure
            rule_id: Rule ID or number
        """
        logger.info(f"Removing firewall filter rule {rule_id} from {device_id}")
        command = f"/ip firewall filter remove {rule_id}"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def disable_filter_rule(self, device_id: str, rule_id: str) -> ConnectionResult:
        """Disable a firewall filter rule."""
        logger.info(f"Disabling firewall filter rule {rule_id} on {device_id}")
        command = f"/ip firewall filter disable {rule_id}"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def enable_filter_rule(self, device_id: str, rule_id: str) -> ConnectionResult:
        """Enable a firewall filter rule."""
        logger.info(f"Enabling firewall filter rule {rule_id} on {device_id}")
        command = f"/ip firewall filter enable {rule_id}"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_filter_rules(self, device_id: str, chain: Optional[str] = None) -> ConnectionResult:
        """
        Get firewall filter rules, optionally filtered by chain.

        Args:
            device_id: Device to query
            chain: Optional chain filter
        """
        logger.info(f"Getting firewall filter rules from {device_id}")
        command = "/ip firewall filter print detail"
        if chain:
            command += f" where chain={chain}"
        return await self.device_manager.execute_command(device_id, command)

    async def add_nat_rule(
        self,
        device_id: str,
        chain: str,
        action: str,
        protocol: Optional[str] = None,
        src_address: Optional[str] = None,
        dst_address: Optional[str] = None,
        src_port: Optional[str] = None,
        dst_port: Optional[str] = None,
        to_addresses: Optional[str] = None,
        to_ports: Optional[str] = None,
        in_interface: Optional[str] = None,
        out_interface: Optional[str] = None,
        comment: Optional[str] = None,
        disabled: bool = False
    ) -> ConnectionResult:
        """
        Add a NAT rule.

        Args:
            device_id: Device to configure
            chain: Chain name (srcnat, dstnat)
            action: Action (masquerade, dst-nat, src-nat, etc.)
            protocol: Protocol (tcp, udp, etc.)
            src_address: Source IP address/network
            dst_address: Destination IP address/network
            src_port: Source port(s)
            dst_port: Destination port(s)
            to_addresses: NAT target address
            to_ports: NAT target port
            in_interface: Input interface
            out_interface: Output interface
            comment: Rule comment
            disabled: Whether rule is disabled
        """
        logger.info(f"Adding NAT rule to {device_id}: chain={chain}, action={action}")

        cmd_parts = ["/ip firewall nat add"]
        cmd_parts.append(f"chain={chain}")
        cmd_parts.append(f"action={action}")

        if protocol:
            cmd_parts.append(f"protocol={protocol}")
        if src_address:
            cmd_parts.append(f"src-address={src_address}")
        if dst_address:
            cmd_parts.append(f"dst-address={dst_address}")
        if src_port:
            cmd_parts.append(f"src-port={src_port}")
        if dst_port:
            cmd_parts.append(f"dst-port={dst_port}")
        if to_addresses:
            cmd_parts.append(f"to-addresses={to_addresses}")
        if to_ports:
            cmd_parts.append(f"to-ports={to_ports}")
        if in_interface:
            cmd_parts.append(f"in-interface={in_interface}")
        if out_interface:
            cmd_parts.append(f"out-interface={out_interface}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_nat_rules(self, device_id: str, chain: Optional[str] = None) -> ConnectionResult:
        """Get NAT rules, optionally filtered by chain."""
        logger.info(f"Getting NAT rules from {device_id}")
        command = "/ip firewall nat print detail"
        if chain:
            command += f" where chain={chain}"
        return await self.device_manager.execute_command(device_id, command)

    async def remove_nat_rule(self, device_id: str, rule_id: str) -> ConnectionResult:
        """Remove a NAT rule by ID."""
        logger.info(f"Removing NAT rule {rule_id} from {device_id}")
        command = f"/ip firewall nat remove {rule_id}"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def add_mangle_rule(
        self,
        device_id: str,
        chain: str,
        action: str,
        protocol: Optional[str] = None,
        src_address: Optional[str] = None,
        dst_address: Optional[str] = None,
        new_packet_mark: Optional[str] = None,
        new_connection_mark: Optional[str] = None,
        passthrough: bool = True,
        comment: Optional[str] = None,
        disabled: bool = False
    ) -> ConnectionResult:
        """
        Add a mangle rule for packet/connection marking.

        Args:
            device_id: Device to configure
            chain: Chain name (prerouting, postrouting, forward, etc.)
            action: Action (mark-packet, mark-connection, etc.)
            protocol: Protocol filter
            src_address: Source address filter
            dst_address: Destination address filter
            new_packet_mark: Packet mark to set
            new_connection_mark: Connection mark to set
            passthrough: Whether to pass to next rule
            comment: Rule comment
            disabled: Whether rule is disabled
        """
        logger.info(f"Adding mangle rule to {device_id}: chain={chain}, action={action}")

        cmd_parts = ["/ip firewall mangle add"]
        cmd_parts.append(f"chain={chain}")
        cmd_parts.append(f"action={action}")

        if protocol:
            cmd_parts.append(f"protocol={protocol}")
        if src_address:
            cmd_parts.append(f"src-address={src_address}")
        if dst_address:
            cmd_parts.append(f"dst-address={dst_address}")
        if new_packet_mark:
            cmd_parts.append(f"new-packet-mark={new_packet_mark}")
        if new_connection_mark:
            cmd_parts.append(f"new-connection-mark={new_connection_mark}")
        cmd_parts.append(f"passthrough={'yes' if passthrough else 'no'}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_mangle_rules(self, device_id: str) -> ConnectionResult:
        """Get mangle rules."""
        logger.info(f"Getting mangle rules from {device_id}")
        command = "/ip firewall mangle print detail"
        return await self.device_manager.execute_command(device_id, command)

    async def remove_mangle_rule(self, device_id: str, rule_id: str) -> ConnectionResult:
        """Remove a mangle rule by ID."""
        logger.info(f"Removing mangle rule {rule_id} from {device_id}")
        command = f"/ip firewall mangle remove {rule_id}"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def add_address_list(
        self,
        device_id: str,
        list_name: str,
        address: str,
        comment: Optional[str] = None,
        timeout: Optional[str] = None,
        disabled: bool = False
    ) -> ConnectionResult:
        """
        Add an address to a firewall address list.

        Args:
            device_id: Device to configure
            list_name: Name of the address list
            address: IP address or network
            comment: Optional comment
            timeout: Optional timeout (e.g., "1d", "2h30m")
            disabled: Whether entry is disabled
        """
        logger.info(f"Adding {address} to address list '{list_name}' on {device_id}")

        cmd_parts = ["/ip firewall address-list add"]
        cmd_parts.append(f"list={list_name}")
        cmd_parts.append(f"address={address}")

        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")
        if timeout:
            cmd_parts.append(f"timeout={timeout}")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def remove_address_list_entry(self, device_id: str, entry_id: str) -> ConnectionResult:
        """Remove an address list entry by ID."""
        logger.info(f"Removing address list entry {entry_id} from {device_id}")
        command = f"/ip firewall address-list remove {entry_id}"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_address_list(self, device_id: str, list_name: Optional[str] = None) -> ConnectionResult:
        """
        Get address list entries, optionally filtered by list name.

        Args:
            device_id: Device to query
            list_name: Optional list name filter
        """
        logger.info(f"Getting address list from {device_id}")
        command = "/ip firewall address-list print detail"
        if list_name:
            command += f" where list={list_name}"
        return await self.device_manager.execute_command(device_id, command)

    async def clear_address_list(self, device_id: str, list_name: str) -> ConnectionResult:
        """
        Clear all entries from an address list.

        Args:
            device_id: Device to configure
            list_name: Name of list to clear
        """
        logger.info(f"Clearing address list '{list_name}' on {device_id}")

        # First, get all entries for this list
        result = await self.get_address_list(device_id, list_name)
        if not result.success:
            return result

        # Remove entries (this will need parsing, but for now just return success)
        command = f"/ip firewall address-list remove [find list={list_name}]"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_connection_tracking(self, device_id: str) -> ConnectionResult:
        """Get connection tracking information."""
        logger.info(f"Getting connection tracking info from {device_id}")
        command = "/ip firewall connection print"
        return await self.device_manager.execute_command(device_id, command)
