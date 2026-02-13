"""Mock MikroTik device simulator."""


class MockMikroTikDevice:
    """Simulates a MikroTik device for testing."""

    def __init__(self):
        self.interfaces = [
            {"name": "ether1", "type": "ether", "mtu": "1500"},
            {"name": "ether2", "type": "ether", "mtu": "1500"},
            {"name": "bridge", "type": "bridge", "mtu": "1500"},
        ]
        self.ip_addresses = [
            {"address": "192.168.1.1/24", "interface": "ether1"},
            {"address": "10.0.0.1/24", "interface": "ether2"},
        ]
        self.firewall_rules = []
        self.dhcp_servers = []
        self.vpn_peers = []

    def execute(self, command: str) -> str:
        """Execute a command and return mock output."""
        if "/interface print" in command:
            return self._mock_interface_output()
        elif "/ip address print" in command:
            return self._mock_ip_address_output()
        elif "/ip firewall filter print" in command:
            return self._mock_firewall_output()
        elif "/ip firewall filter add" in command:
            self.firewall_rules.append(command)
            return ""
        elif "/ip dhcp-server print" in command:
            return self._mock_dhcp_servers_output()
        elif "/system resource print" in command:
            return self._mock_system_resource_output()
        elif "/system identity print" in command:
            return "name: TestRouter"
        else:
            return f"Mock response for: {command}"

    def _mock_interface_output(self) -> str:
        """Generate mock interface output."""
        lines = ["  name       type     mtu"]
        for iface in self.interfaces:
            lines.append(f"  {iface['name']:<10} {iface['type']:<8} {iface['mtu']}")
        return "\n".join(lines)

    def _mock_ip_address_output(self) -> str:
        """Generate mock IP address output."""
        lines = ["  # address            interface"]
        for i, addr in enumerate(self.ip_addresses):
            lines.append(f"  {i} {addr['address']:<18} {addr['interface']}")
        return "\n".join(lines)

    def _mock_firewall_output(self) -> str:
        """Generate mock firewall output."""
        if not self.firewall_rules:
            return "No rules found"
        return "\n".join(self.firewall_rules)

    def _mock_dhcp_servers_output(self) -> str:
        """Generate mock DHCP servers output."""
        if not self.dhcp_servers:
            return "No DHCP servers configured"
        return "\n".join(self.dhcp_servers)

    def _mock_system_resource_output(self) -> str:
        """Generate mock system resource output."""
        return """
uptime: 1d2h3m4s
version: 7.10.2
cpu: ARMv7
cpu-count: 2
free-memory: 512.0MiB
total-memory: 1024.0MiB
        """.strip()
