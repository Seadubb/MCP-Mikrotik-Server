# MikroTik MCP Server

A robust Model Context Protocol (MCP) server for managing MikroTik routers running RouterOS 6 and 7. Provides seamless connectivity via SSH, Telnet, or API with automatic command adaptation.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-1.0.0-orange.svg)](https://modelcontextprotocol.io)

## 🚀 Quick Start (Python - Recommended)

**Python version is simpler and easier to deploy!**

### 1. Install
```bash
pip install -e .
```

### 2. Configure
Copy and edit the example configuration:
```bash
cp devices.json.example devices.json
# Edit devices.json with your router details
```

### 3. Add to Claude Desktop
Add to your Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "mikrotik": {
      "command": "python",
      "args": ["-m", "mikrotik_mcp.server"]
    }
  }
}
```

### 4. Start Using
Restart Claude Desktop and try:
```
List my MikroTik devices
Connect to router-main and show system info
```

📖 **[Read Full Python Documentation →](README_PYTHON.md)**

## ✨ Features

- **46+ MCP Tools**: Complete router management suite
- **Multi-Protocol Support**: SSH (recommended), API, Telnet
- **RouterOS 6 & 7 Compatible**: Automatic command adaptation
- **Advanced Features**:
  - Firewall management (filter, NAT, address lists)
  - DHCP server configuration
  - VPN setup (IPsec, L2TP, WireGuard)
  - Configuration profiles
  - Backup/restore
  - Audit logging
  - Fleet management

## 📦 Installation Options

### Python (Recommended)
```bash
# Windows
install-python.bat

# Linux/macOS
chmod +x install-python.sh
./install-python.sh
```

### TypeScript (Advanced)
```bash
npm install
npm run build
```

## 🔧 MCP Tools Available

### Device Management (13 tools)
- `list_devices` - List all configured routers
- `connect_device` - Establish connection
- `execute_command` - Run any RouterOS command
- `get_system_info` - System resources
- `get_interfaces` - Network interfaces
- `get_firewall_rules` - Firewall configuration
- `backup_config` - Export configuration
- And more...

### Firewall Management (5 tools)
- `firewall_add_filter_rule` - Add filter rules
- `firewall_add_nat_rule` - Configure NAT
- `firewall_add_address_list` - Manage address lists
- `firewall_get_address_list` - View address lists
- `firewall_remove_rule` - Remove rules

### DHCP Management (5 tools)
- `dhcp_create_server` - Create DHCP server
- `dhcp_add_network` - Configure network
- `dhcp_add_static_lease` - Add static leases
- `dhcp_create_pool` - Create IP pools
- `dhcp_get_servers` - List DHCP servers

### VPN Management (8 tools)
- IPsec: `vpn_add_ipsec_peer`, `vpn_get_ipsec_peers`
- L2TP: `vpn_add_l2tp_user`, `vpn_configure_l2tp_server`, `vpn_get_l2tp_connections`
- WireGuard: `vpn_add_wireguard_interface`, `vpn_add_wireguard_peer`, `vpn_get_wireguard_interfaces`
- Generic: `vpn_get_ppp_secrets`

### Configuration Profiles (6 tools)
- `profile_list` - List available profiles
- `profile_get` - Get profile details
- `profile_preview` - Preview commands
- `profile_apply` - Apply profile to device
- `profile_validate` - Validate profile
- `profile_save_current` - Save device config as profile

### Advanced Features (9 tools)
- `execute_batch_commands` - Run multiple commands
- `get_fleet_status` - Multi-device overview
- `execute_on_all_devices` - Run command on all
- `compare_configs` - Compare two devices
- `get_command_history` - Audit log access
- `get_device_audit_stats` - Device statistics
- `get_connection_stats` - Connection metrics
- `export_config` - Export without saving
- `restore_config` - Restore from backup

## 📁 Project Structure

```
mikrotik_mcp/
├── server.py              # Main MCP server
├── device_manager.py      # Device lifecycle management
├── models.py              # Pydantic data models
├── connections/           # SSH, Telnet, API implementations
├── modules/               # Feature modules
│   ├── firewall.py       # Firewall management
│   ├── dhcp.py           # DHCP management
│   ├── vpn.py            # VPN management
│   └── profiles.py       # Configuration profiles
├── audit.py              # Audit logging
├── cache.py              # Response caching
├── retry.py              # Connection retry logic
└── logger.py             # Structured logging
```

## 🔒 Security

- **Never commit** `devices.json` or `.env` (already in `.gitignore`)
- Use SSH instead of Telnet (encrypted)
- Store passwords in environment variables
- Enable audit logging for compliance
- Regularly update RouterOS firmware

## 📚 Documentation

- **[Python Documentation](README_PYTHON.md)** - Detailed Python setup and usage
- **[Quick Start Guide](QUICKSTART_PYTHON.md)** - Get running in 5 minutes
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- **[Manual](MANUAL.md)** - Complete reference guide
- **[Implementation Status](IMPLEMENTATION_STATUS.md)** - Current progress

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=mikrotik_mcp --cov-report=html

# Specific test
pytest tests/test_device_manager.py
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Credits

Built with:
- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk) - Model Context Protocol
- [Paramiko](https://www.paramiko.org/) - SSH client
- [telnetlib3](https://telnetlib3.readthedocs.io/) - Telnet client
- [routeros-api](https://github.com/socialwifi/RouterOS-api) - MikroTik API
- [Pydantic](https://docs.pydantic.dev/) - Data validation

## 🐛 Support

For issues:
1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review [Documentation](README_PYTHON.md)
3. Check existing GitHub issues
4. Create a new issue with details

## 🗺️ Roadmap

- [x] Basic device management
- [x] SSH/API/Telnet support
- [x] RouterOS 6/7 compatibility
- [x] Firewall management
- [x] DHCP management
- [x] VPN management (IPsec, L2TP, WireGuard)
- [x] Configuration profiles
- [x] Audit logging
- [ ] Wireless management
- [ ] Queue management
- [ ] Hotspot management
- [ ] User management
- [ ] Backup scheduling
- [ ] SSH key authentication
- [ ] Web-based dashboard

---

**Happy routing! 🚀**

For detailed setup and usage, see the **[Python Documentation](README_PYTHON.md)**.
