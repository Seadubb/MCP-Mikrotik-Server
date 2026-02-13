"""VPN management module for MikroTik devices."""

from typing import Optional, TYPE_CHECKING
from ..logger import get_logger
from ..models import ConnectionResult

if TYPE_CHECKING:
    from ..device_manager import DeviceManager

logger = get_logger(__name__)


class VPNManager:
    """Manage VPN operations (IPsec, L2TP, PPTP, Wireguard) on MikroTik devices."""

    def __init__(self, device_manager: 'DeviceManager'):
        self.device_manager = device_manager

    # ==================== IPsec Operations ====================

    async def add_ipsec_peer(
        self,
        device_id: str,
        name: str,
        address: str,
        auth_method: str = "pre-shared-key",
        secret: Optional[str] = None,
        exchange_mode: str = "main",
        disabled: bool = False,
        comment: Optional[str] = None
    ) -> ConnectionResult:
        """
        Add an IPsec peer.

        Args:
            device_id: Device to configure
            name: Peer name
            address: Peer IP address
            auth_method: Authentication method (pre-shared-key, rsa-key, etc.)
            secret: Pre-shared key
            exchange_mode: Exchange mode (main, aggressive)
            disabled: Whether peer is disabled
            comment: Optional comment
        """
        logger.info(f"Adding IPsec peer '{name}' to {device_id}")

        cmd_parts = ["/ip ipsec peer add"]
        cmd_parts.append(f"name={name}")
        cmd_parts.append(f"address={address}")
        cmd_parts.append(f"auth-method={auth_method}")
        cmd_parts.append(f"exchange-mode={exchange_mode}")

        if secret:
            cmd_parts.append(f"secret={secret}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def remove_ipsec_peer(self, device_id: str, peer_name: str) -> ConnectionResult:
        """Remove an IPsec peer."""
        logger.info(f"Removing IPsec peer '{peer_name}' from {device_id}")
        command = f"/ip ipsec peer remove [find name={peer_name}]"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_ipsec_peers(self, device_id: str) -> ConnectionResult:
        """Get IPsec peers."""
        logger.info(f"Getting IPsec peers from {device_id}")
        command = "/ip ipsec peer print detail"
        return await self.device_manager.execute_command(device_id, command)

    async def add_ipsec_proposal(
        self,
        device_id: str,
        name: str,
        auth_algorithms: str = "sha256",
        enc_algorithms: str = "aes-256-cbc",
        pfs_group: str = "modp2048",
        lifetime: str = "30m",
        disabled: bool = False
    ) -> ConnectionResult:
        """
        Add an IPsec proposal.

        Args:
            device_id: Device to configure
            name: Proposal name
            auth_algorithms: Authentication algorithms (sha1, sha256, sha512, md5)
            enc_algorithms: Encryption algorithms (3des, aes-128-cbc, aes-256-cbc, etc.)
            pfs_group: PFS group (modp1024, modp2048, modp4096, etc.)
            lifetime: Proposal lifetime
            disabled: Whether proposal is disabled
        """
        logger.info(f"Adding IPsec proposal '{name}' to {device_id}")

        cmd_parts = ["/ip ipsec proposal add"]
        cmd_parts.append(f"name={name}")
        cmd_parts.append(f"auth-algorithms={auth_algorithms}")
        cmd_parts.append(f"enc-algorithms={enc_algorithms}")
        cmd_parts.append(f"pfs-group={pfs_group}")
        cmd_parts.append(f"lifetime={lifetime}")

        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_ipsec_proposals(self, device_id: str) -> ConnectionResult:
        """Get IPsec proposals."""
        logger.info(f"Getting IPsec proposals from {device_id}")
        command = "/ip ipsec proposal print detail"
        return await self.device_manager.execute_command(device_id, command)

    async def add_ipsec_policy(
        self,
        device_id: str,
        src_address: str,
        dst_address: str,
        action: str = "encrypt",
        proposal: Optional[str] = None,
        tunnel: bool = True,
        disabled: bool = False,
        comment: Optional[str] = None
    ) -> ConnectionResult:
        """
        Add an IPsec policy.

        Args:
            device_id: Device to configure
            src_address: Source address/network
            dst_address: Destination address/network
            action: Policy action (encrypt, discard, none)
            proposal: Proposal name to use
            tunnel: Use tunnel mode (vs transport)
            disabled: Whether policy is disabled
            comment: Optional comment
        """
        logger.info(f"Adding IPsec policy for {src_address} -> {dst_address} on {device_id}")

        cmd_parts = ["/ip ipsec policy add"]
        cmd_parts.append(f"src-address={src_address}")
        cmd_parts.append(f"dst-address={dst_address}")
        cmd_parts.append(f"action={action}")
        cmd_parts.append(f"tunnel={'yes' if tunnel else 'no'}")

        if proposal:
            cmd_parts.append(f"proposal={proposal}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_ipsec_policies(self, device_id: str) -> ConnectionResult:
        """Get IPsec policies."""
        logger.info(f"Getting IPsec policies from {device_id}")
        command = "/ip ipsec policy print detail"
        return await self.device_manager.execute_command(device_id, command)

    async def get_ipsec_active_peers(self, device_id: str) -> ConnectionResult:
        """Get active IPsec connections."""
        logger.info(f"Getting active IPsec peers from {device_id}")
        command = "/ip ipsec active-peers print"
        return await self.device_manager.execute_command(device_id, command)

    async def get_ipsec_installed_sa(self, device_id: str) -> ConnectionResult:
        """Get installed IPsec security associations."""
        logger.info(f"Getting IPsec installed SAs from {device_id}")
        command = "/ip ipsec installed-sa print"
        return await self.device_manager.execute_command(device_id, command)

    # ==================== L2TP Operations ====================

    async def configure_l2tp_server(
        self,
        device_id: str,
        enabled: bool = True,
        default_profile: str = "default-encryption",
        authentication: str = "mschap2",
        use_ipsec: bool = True,
        ipsec_secret: Optional[str] = None
    ) -> ConnectionResult:
        """
        Configure L2TP server settings.

        Args:
            device_id: Device to configure
            enabled: Enable L2TP server
            default_profile: Default PPP profile
            authentication: Authentication methods (pap, chap, mschap1, mschap2)
            use_ipsec: Use IPsec for L2TP
            ipsec_secret: IPsec pre-shared key
        """
        logger.info(f"Configuring L2TP server on {device_id}")

        cmd_parts = ["/interface l2tp-server server set"]
        cmd_parts.append(f"enabled={'yes' if enabled else 'no'}")
        cmd_parts.append(f"default-profile={default_profile}")
        cmd_parts.append(f"authentication={authentication}")
        cmd_parts.append(f"use-ipsec={'yes' if use_ipsec else 'no'}")

        if ipsec_secret:
            cmd_parts.append(f"ipsec-secret={ipsec_secret}")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def add_l2tp_user(
        self,
        device_id: str,
        name: str,
        password: str,
        local_address: Optional[str] = None,
        remote_address: Optional[str] = None,
        profile: str = "default",
        disabled: bool = False,
        comment: Optional[str] = None
    ) -> ConnectionResult:
        """
        Add an L2TP user.

        Args:
            device_id: Device to configure
            name: Username
            password: Password
            local_address: Local (server) IP address
            remote_address: Remote (client) IP address
            profile: PPP profile to use
            disabled: Whether user is disabled
            comment: Optional comment
        """
        logger.info(f"Adding L2TP user '{name}' to {device_id}")

        cmd_parts = ["/ppp secret add"]
        cmd_parts.append(f"name={name}")
        cmd_parts.append(f"password={password}")
        cmd_parts.append(f"service=l2tp")
        cmd_parts.append(f"profile={profile}")

        if local_address:
            cmd_parts.append(f"local-address={local_address}")
        if remote_address:
            cmd_parts.append(f"remote-address={remote_address}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_l2tp_server_status(self, device_id: str) -> ConnectionResult:
        """Get L2TP server status."""
        logger.info(f"Getting L2TP server status from {device_id}")
        command = "/interface l2tp-server server print"
        return await self.device_manager.execute_command(device_id, command)

    async def get_l2tp_connections(self, device_id: str) -> ConnectionResult:
        """Get active L2TP connections."""
        logger.info(f"Getting L2TP connections from {device_id}")
        command = "/interface l2tp-server print detail"
        return await self.device_manager.execute_command(device_id, command)

    # ==================== PPTP Operations ====================

    async def configure_pptp_server(
        self,
        device_id: str,
        enabled: bool = True,
        default_profile: str = "default-encryption",
        authentication: str = "mschap2"
    ) -> ConnectionResult:
        """
        Configure PPTP server settings.

        Args:
            device_id: Device to configure
            enabled: Enable PPTP server
            default_profile: Default PPP profile
            authentication: Authentication methods
        """
        logger.info(f"Configuring PPTP server on {device_id}")

        cmd_parts = ["/interface pptp-server server set"]
        cmd_parts.append(f"enabled={'yes' if enabled else 'no'}")
        cmd_parts.append(f"default-profile={default_profile}")
        cmd_parts.append(f"authentication={authentication}")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def add_pptp_user(
        self,
        device_id: str,
        name: str,
        password: str,
        local_address: Optional[str] = None,
        remote_address: Optional[str] = None,
        profile: str = "default",
        disabled: bool = False,
        comment: Optional[str] = None
    ) -> ConnectionResult:
        """Add a PPTP user."""
        logger.info(f"Adding PPTP user '{name}' to {device_id}")

        cmd_parts = ["/ppp secret add"]
        cmd_parts.append(f"name={name}")
        cmd_parts.append(f"password={password}")
        cmd_parts.append(f"service=pptp")
        cmd_parts.append(f"profile={profile}")

        if local_address:
            cmd_parts.append(f"local-address={local_address}")
        if remote_address:
            cmd_parts.append(f"remote-address={remote_address}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_pptp_connections(self, device_id: str) -> ConnectionResult:
        """Get active PPTP connections."""
        logger.info(f"Getting PPTP connections from {device_id}")
        command = "/interface pptp-server print detail"
        return await self.device_manager.execute_command(device_id, command)

    # ==================== WireGuard Operations ====================

    async def add_wireguard_interface(
        self,
        device_id: str,
        name: str,
        listen_port: int,
        private_key: Optional[str] = None,
        mtu: int = 1420,
        disabled: bool = False,
        comment: Optional[str] = None
    ) -> ConnectionResult:
        """
        Add a WireGuard interface.

        Args:
            device_id: Device to configure
            name: Interface name
            listen_port: UDP listen port
            private_key: Private key (if None, will be auto-generated)
            mtu: Interface MTU
            disabled: Whether interface is disabled
            comment: Optional comment
        """
        logger.info(f"Adding WireGuard interface '{name}' to {device_id}")

        cmd_parts = ["/interface wireguard add"]
        cmd_parts.append(f"name={name}")
        cmd_parts.append(f"listen-port={listen_port}")
        cmd_parts.append(f"mtu={mtu}")

        if private_key:
            cmd_parts.append(f"private-key={private_key}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def add_wireguard_peer(
        self,
        device_id: str,
        interface: str,
        public_key: str,
        allowed_address: str,
        endpoint_address: Optional[str] = None,
        endpoint_port: Optional[int] = None,
        persistent_keepalive: Optional[str] = None,
        disabled: bool = False,
        comment: Optional[str] = None
    ) -> ConnectionResult:
        """
        Add a WireGuard peer.

        Args:
            device_id: Device to configure
            interface: WireGuard interface name
            public_key: Peer's public key
            allowed_address: Allowed IP addresses (e.g., "10.0.0.2/32")
            endpoint_address: Peer endpoint IP
            endpoint_port: Peer endpoint port
            persistent_keepalive: Keepalive interval
            disabled: Whether peer is disabled
            comment: Optional comment
        """
        logger.info(f"Adding WireGuard peer to interface '{interface}' on {device_id}")

        cmd_parts = ["/interface wireguard peers add"]
        cmd_parts.append(f"interface={interface}")
        cmd_parts.append(f"public-key={public_key}")
        cmd_parts.append(f"allowed-address={allowed_address}")

        if endpoint_address:
            cmd_parts.append(f"endpoint-address={endpoint_address}")
        if endpoint_port:
            cmd_parts.append(f"endpoint-port={endpoint_port}")
        if persistent_keepalive:
            cmd_parts.append(f"persistent-keepalive={persistent_keepalive}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")
        if disabled:
            cmd_parts.append("disabled=yes")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_wireguard_interfaces(self, device_id: str) -> ConnectionResult:
        """Get WireGuard interfaces."""
        logger.info(f"Getting WireGuard interfaces from {device_id}")
        command = "/interface wireguard print detail"
        return await self.device_manager.execute_command(device_id, command)

    async def get_wireguard_peers(self, device_id: str, interface: Optional[str] = None) -> ConnectionResult:
        """Get WireGuard peers."""
        logger.info(f"Getting WireGuard peers from {device_id}")
        command = "/interface wireguard peers print detail"
        if interface:
            command += f" where interface={interface}"
        return await self.device_manager.execute_command(device_id, command)

    async def remove_wireguard_interface(self, device_id: str, interface_name: str) -> ConnectionResult:
        """Remove a WireGuard interface."""
        logger.info(f"Removing WireGuard interface '{interface_name}' from {device_id}")
        command = f"/interface wireguard remove [find name={interface_name}]"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def remove_wireguard_peer(self, device_id: str, peer_id: str) -> ConnectionResult:
        """Remove a WireGuard peer."""
        logger.info(f"Removing WireGuard peer {peer_id} from {device_id}")
        command = f"/interface wireguard peers remove {peer_id}"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    # ==================== PPP Secrets (Common for L2TP/PPTP) ====================

    async def get_ppp_secrets(self, device_id: str, service: Optional[str] = None) -> ConnectionResult:
        """
        Get PPP secrets (users for L2TP/PPTP).

        Args:
            device_id: Device to query
            service: Filter by service (l2tp, pptp, pppoe, etc.)
        """
        logger.info(f"Getting PPP secrets from {device_id}")
        command = "/ppp secret print detail"
        if service:
            command += f" where service={service}"
        return await self.device_manager.execute_command(device_id, command)

    async def remove_ppp_secret(self, device_id: str, username: str) -> ConnectionResult:
        """Remove a PPP secret (user)."""
        logger.info(f"Removing PPP secret '{username}' from {device_id}")
        command = f"/ppp secret remove [find name={username}]"
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_ppp_active_connections(self, device_id: str) -> ConnectionResult:
        """Get active PPP connections."""
        logger.info(f"Getting active PPP connections from {device_id}")
        command = "/ppp active print detail"
        return await self.device_manager.execute_command(device_id, command)

    async def create_ppp_profile(
        self,
        device_id: str,
        name: str,
        local_address: Optional[str] = None,
        remote_address: Optional[str] = None,
        dns_server: Optional[str] = None,
        use_encryption: bool = True,
        comment: Optional[str] = None
    ) -> ConnectionResult:
        """
        Create a PPP profile.

        Args:
            device_id: Device to configure
            name: Profile name
            local_address: Local (server) address pool
            remote_address: Remote (client) address pool
            dns_server: DNS server for clients
            use_encryption: Use MPPE encryption
            comment: Optional comment
        """
        logger.info(f"Creating PPP profile '{name}' on {device_id}")

        cmd_parts = ["/ppp profile add"]
        cmd_parts.append(f"name={name}")
        cmd_parts.append(f"use-encryption={'yes' if use_encryption else 'no'}")

        if local_address:
            cmd_parts.append(f"local-address={local_address}")
        if remote_address:
            cmd_parts.append(f"remote-address={remote_address}")
        if dns_server:
            cmd_parts.append(f"dns-server={dns_server}")
        if comment:
            cmd_parts.append(f"comment=\"{comment}\"")

        command = " ".join(cmd_parts)
        return await self.device_manager.execute_command(device_id, command, use_cache=False)

    async def get_ppp_profiles(self, device_id: str) -> ConnectionResult:
        """Get PPP profiles."""
        logger.info(f"Getting PPP profiles from {device_id}")
        command = "/ppp profile print detail"
        return await self.device_manager.execute_command(device_id, command)
