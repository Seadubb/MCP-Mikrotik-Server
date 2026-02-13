"""DHCP management module for MikroTik devices."""

from typing import Optional, TYPE_CHECKING
from ..logger import get_logger
from ..models import ConnectionResult

if TYPE_CHECKING:
    from ..device_manager import DeviceManager

logger = get_logger(__name__)


class DHCPManager:
    """Manage DHCP server and client operations on MikroTik devices."""

    def __init__(self, device_manager: 'DeviceManager'):
        self.device_manager = device_manager

    async def create_dhcp_server(
        self,
        device_id: str,
        name: str,
        interface: str,
        address_pool: str,
        lease_time: str = "1d",
        disabled: bool = False
    ) -> ConnectionResult:
        """
        Create a DHCP server.

        Args:
            device_id: Device to configure
            name: DHCP server name
            interface: Interface to run DHCP on
            address_pool: Pool name to use
            lease_time: Lease time (e.g., "1d", "12h", "3600")
            disabled: Whether server is disabled
        """
        logger.info(f"Creating DHCP server '{name}' on {device_id}")

        cmd_parts = ["/ip dhcp-server add"]
        cmd_parts.append(f"name={name}")
        cmd_parts.append(f"interface={interface}")
        cmd_parts.append(f"address-pool={address_pool}")
        cmd_parts.append(f"lease-time={lease_time}")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def remove_dhcp_server(self, device_id: str, server_name: str) -> ConnectionResult:
        """
        Remove a DHCP server by name.

        Args:
            device_id: Device to configure
            server_name: Name of DHCP server to remove
        """
        logger.info(f"Removing DHCP server '{server_name}' from {device_id}")
        command = f"/ip dhcp-server remove [find name={server_name}]"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_dhcp_servers(self, device_id: str) -> ConnectionResult:
        """Get list of all DHCP servers."""
        logger.info(f"Getting DHCP servers from {device_id}")
        command = "/ip dhcp-server print detail"
        return await self.device_manager.execute_command(device_id, command)

    async def enable_dhcp_server(self, device_id: str, server_name: str) -> ConnectionResult:
        """Enable a DHCP server."""
        logger.info(f"Enabling DHCP server '{server_name}' on {device_id}")
        command = f"/ip dhcp-server enable [find name={server_name}]"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def disable_dhcp_server(self, device_id: str, server_name: str) -> ConnectionResult:
        """Disable a DHCP server."""
        logger.info(f"Disabling DHCP server '{server_name}' on {device_id}")
        command = f"/ip dhcp-server disable [find name={server_name}]"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def create_address_pool(
        self,
        device_id: str,
        name: str,
        ranges: str,
        next_pool: Optional[str] = None,
        comment: Optional[str] = None
    ) -> ConnectionResult:
        """
        Create an IP address pool.

        Args:
            device_id: Device to configure
            name: Pool name
            ranges: IP ranges (e.g., "192.168.1.100-192.168.1.200")
            next_pool: Next pool to use when this one is exhausted
            comment: Optional comment
        """
        logger.info(f"Creating address pool '{name}' on {device_id}")

        cmd_parts = ["/ip pool add"]
        cmd_parts.append(f"name={name}")
        cmd_parts.append(f"ranges={ranges}")

        if next_pool:
            cmd_parts.append(f"next-pool={next_pool}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def remove_address_pool(self, device_id: str, pool_name: str) -> ConnectionResult:
        """Remove an address pool."""
        logger.info(f"Removing address pool '{pool_name}' from {device_id}")
        command = f"/ip pool remove [find name={pool_name}]"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_address_pools(self, device_id: str) -> ConnectionResult:
        """Get list of address pools."""
        logger.info(f"Getting address pools from {device_id}")
        command = "/ip pool print detail"
        return await self.device_manager.execute_command(device_id, command)

    async def add_dhcp_network(
        self,
        device_id: str,
        address: str,
        gateway: Optional[str] = None,
        netmask: Optional[str] = None,
        dns_server: Optional[str] = None,
        domain: Optional[str] = None,
        ntp_server: Optional[str] = None,
        comment: Optional[str] = None
    ) -> ConnectionResult:
        """
        Add a DHCP network configuration.

        Args:
            device_id: Device to configure
            address: Network address (e.g., "192.168.1.0/24")
            gateway: Gateway IP
            netmask: Network mask (or use CIDR in address)
            dns_server: DNS server(s) (comma-separated)
            domain: Domain name
            ntp_server: NTP server(s)
            comment: Optional comment
        """
        logger.info(f"Adding DHCP network {address} on {device_id}")

        cmd_parts = ["/ip dhcp-server network add"]
        cmd_parts.append(f"address={address}")

        if gateway:
            cmd_parts.append(f"gateway={gateway}")
        if netmask:
            cmd_parts.append(f"netmask={netmask}")
        if dns_server:
            cmd_parts.append(f"dns-server={dns_server}")
        if domain:
            cmd_parts.append(f"domain={domain}")
        if ntp_server:
            cmd_parts.append(f"ntp-server={ntp_server}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def remove_dhcp_network(self, device_id: str, address: str) -> ConnectionResult:
        """Remove a DHCP network configuration."""
        logger.info(f"Removing DHCP network {address} from {device_id}")
        command = f"/ip dhcp-server network remove [find address={address}]"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_dhcp_networks(self, device_id: str) -> ConnectionResult:
        """Get DHCP network configurations."""
        logger.info(f"Getting DHCP networks from {device_id}")
        command = "/ip dhcp-server network print detail"
        return await self.device_manager.execute_command(device_id, command)

    async def add_static_lease(
        self,
        device_id: str,
        address: str,
        mac_address: str,
        server: Optional[str] = None,
        comment: Optional[str] = None,
        disabled: bool = False
    ) -> ConnectionResult:
        """
        Add a static DHCP lease.

        Args:
            device_id: Device to configure
            address: IP address to assign
            mac_address: Client MAC address
            server: DHCP server name (optional)
            comment: Optional comment
            disabled: Whether lease is disabled
        """
        logger.info(f"Adding static lease {address} for {mac_address} on {device_id}")

        cmd_parts = ["/ip dhcp-server lease add"]
        cmd_parts.append(f"address={address}")
        cmd_parts.append(f"mac-address={mac_address}")

        if server:
            cmd_parts.append(f"server={server}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def remove_lease(self, device_id: str, lease_id: str) -> ConnectionResult:
        """
        Remove a DHCP lease by ID.

        Args:
            device_id: Device to configure
            lease_id: Lease ID or number
        """
        logger.info(f"Removing DHCP lease {lease_id} from {device_id}")
        command = f"/ip dhcp-server lease remove {lease_id}"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def make_static_lease(self, device_id: str, lease_id: str) -> ConnectionResult:
        """
        Convert a dynamic lease to static.

        Args:
            device_id: Device to configure
            lease_id: Lease ID to make static
        """
        logger.info(f"Making lease {lease_id} static on {device_id}")
        command = f"/ip dhcp-server lease make-static {lease_id}"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_leases(self, device_id: str, server: Optional[str] = None, active_only: bool = False) -> ConnectionResult:
        """
        Get DHCP leases.

        Args:
            device_id: Device to query
            server: Optional server filter
            active_only: Show only active leases
        """
        logger.info(f"Getting DHCP leases from {device_id}")
        command = "/ip dhcp-server lease print detail"

        filters = []
        if server:
            filters.append(f"server={server}")
        if active_only:
            filters.append("status=bound")

        if filters:
            command += " where " + " ".join(filters)

        return await self.device_manager.execute_command(device_id, command)

    async def clear_leases(self, device_id: str, server: Optional[str] = None) -> ConnectionResult:
        """
        Clear dynamic DHCP leases.

        Args:
            device_id: Device to configure
            server: Optional server to clear leases from
        """
        logger.info(f"Clearing DHCP leases on {device_id}")
        command = "/ip dhcp-server lease remove [find dynamic=yes"
        if server:
            command += f" server={server}"
        command += "]"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_dhcp_alerts(self, device_id: str) -> ConnectionResult:
        """Get DHCP server alerts (invalid addresses, etc.)."""
        logger.info(f"Getting DHCP alerts from {device_id}")
        command = "/ip dhcp-server alert print"
        return await self.device_manager.execute_command(device_id, command)

    async def add_dhcp_option(
        self,
        device_id: str,
        name: str,
        code: int,
        value: str,
        comment: Optional[str] = None
    ) -> ConnectionResult:
        """
        Add a custom DHCP option.

        Args:
            device_id: Device to configure
            name: Option name
            code: DHCP option code
            value: Option value
            comment: Optional comment
        """
        logger.info(f"Adding DHCP option '{name}' (code {code}) on {device_id}")

        cmd_parts = ["/ip dhcp-server option add"]
        cmd_parts.append(f"name={name}")
        cmd_parts.append(f"code={code}")
        cmd_parts.append(f"value={value}")

        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_dhcp_options(self, device_id: str) -> ConnectionResult:
        """Get custom DHCP options."""
        logger.info(f"Getting DHCP options from {device_id}")
        command = "/ip dhcp-server option print detail"
        return await self.device_manager.execute_command(device_id, command)
