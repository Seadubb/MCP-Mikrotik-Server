# MikroTik MCP Server (Python Edition)

A robust Model Context Protocol (MCP) server for managing MikroTik routers running RouterOS 6 and 7. This Python implementation provides seamless connectivity via SSH, Telnet, or API with automatic command adaptation.

## Why Python?

This Python version offers:
- **Simple Deployment**: No build step required
- **Easy Installation**: Just `pip install`
- **Auto-Start**: Claude Desktop automatically starts the server
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Minimal Setup**: Configure once and forget

## Quick Start (5 Minutes)

### 1. Install

**Windows:**
```bash
install-python.bat
```

**Linux/macOS:**
```bash
chmod +x install-python.sh
./install-python.sh
```

**Manual Install:**
```bash
pip install -e .
```

### 2. Configure Your Devices

Edit `devices.json`:
```json
{
  "devices": [
    {
      "id": "my-router",
      "name": "My MikroTik Router",
      "host": "192.168.88.1",
      "port": 22,
      "username": "admin",
      "password": "your-password",
      "connectionType": "ssh",
      "routerOSVersion": 7,
      "timeout": 10000
    }
  ]
}
```

### 3. Configure Claude Desktop

Add to `claude_desktop_config.json`:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

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

**That's it!** Claude Desktop will automatically start the server when needed.

### 4. Restart Claude Desktop

The server will start automatically when Claude needs it.

### 5. Test It

In Claude Desktop, try:
```
List my MikroTik devices
```

Then:
```
Connect to my-router and show me the system info
```

## Features

### Multi-Protocol Support
- **SSH** (port 22) - Secure, recommended
- **API** (port 8728) - Native MikroTik protocol
- **Telnet** (port 23) - Legacy support

### RouterOS Compatibility
- Automatic command adaptation between ROS 6 and 7
- Version-specific command mapping
- Graceful handling of unsupported commands

### 13 MCP Tools
1. **list_devices** - List all configured devices
2. **connect_device** - Connect to a device
3. **disconnect_device** - Disconnect from a device
4. **execute_command** - Run any RouterOS command
5. **get_connection_status** - Check connection status
6. **get_device_info** - Get device details
7. **get_system_info** - System resources
8. **get_interfaces** - List interfaces
9. **get_ip_addresses** - List IP addresses
10. **get_firewall_rules** - Firewall rules
11. **get_dhcp_leases** - DHCP leases
12. **get_routes** - Routing table
13. **list_supported_commands** - Commands by ROS version

## Usage Examples

### With Claude Desktop

```
"List my MikroTik devices"
→ Shows all configured routers

"Connect to my-router"
→ Establishes connection

"What's the CPU usage on my-router?"
→ Executes: /system resource print

"Show me all interfaces on my-router"
→ Executes: /interface print

"List DHCP leases on my-router"
→ Executes: /ip dhcp-server lease print

"Execute '/queue simple print' on my-router"
→ Executes the command directly
```

## Project Structure

```
mikrotik_mcp/
├── __init__.py
├── models.py                 # Pydantic models
├── device_manager.py         # Device management
├── compatibility.py          # ROS 6/7 compatibility
├── server.py                 # Main MCP server
└── connections/
    ├── __init__.py
    ├── base.py               # Base interface
    ├── ssh_connection.py     # SSH handler
    ├── telnet_connection.py  # Telnet handler
    ├── api_connection.py     # API handler
    └── factory.py            # Connection factory
```

## Requirements

- Python 3.10 or higher
- pip (Python package manager)
- Access to MikroTik router(s)

## Installation Details

### System Requirements

**Python 3.10+**
- Windows: Download from [python.org](https://www.python.org)
- macOS: `brew install python3`
- Linux: `sudo apt install python3 python3-pip`

### Dependencies

All dependencies are automatically installed:
- `mcp` - Model Context Protocol SDK
- `paramiko` - SSH client
- `telnetlib3` - Telnet client
- `routeros-api` - MikroTik API client
- `pydantic` - Data validation

## Configuration

### Device Configuration

The `devices.json` file contains your router configurations:

```json
{
  "devices": [
    {
      "id": "router-main",           // Unique identifier
      "name": "Main Gateway",        // Human-readable name
      "host": "192.168.88.1",        // IP or hostname
      "port": 22,                    // SSH: 22, API: 8728, Telnet: 23
      "username": "admin",           // RouterOS username
      "password": "yourpassword",    // RouterOS password
      "connectionType": "ssh",       // ssh, api, or telnet
      "routerOSVersion": 7,          // 6 or 7
      "timeout": 10000,              // Connection timeout (ms)
      "description": "Main router"   // Optional description
    }
  ]
}
```

### MCP Configuration

The MCP configuration tells Claude how to start the server.

**Simple (Recommended):**
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

**With Virtual Environment:**
```json
{
  "mcpServers": {
    "mikrotik": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "mikrotik_mcp.server"]
    }
  }
}
```

**With Specific Python:**
```json
{
  "mcpServers": {
    "mikrotik": {
      "command": "python3",
      "args": ["-m", "mikrotik_mcp.server"]
    }
  }
}
```

## Router Setup

Ensure the appropriate service is enabled on your MikroTik router:

### For SSH (Recommended)
```routeros
/ip service enable ssh
/ip service set ssh port=22
```

### For API
```routeros
/ip service enable api
/ip service set api port=8728
```

### For Telnet (Not Recommended)
```routeros
/ip service enable telnet
/ip service set telnet port=23
```

## Troubleshooting

### Server Not Starting

**Check Python Version:**
```bash
python --version  # Should be 3.10+
```

**Reinstall:**
```bash
pip uninstall mikrotik-mcp-server
pip install -e .
```

### Connection Issues

**Connection Timeout:**
- Verify IP address: `ping 192.168.88.1`
- Check firewall rules
- Increase timeout in `devices.json`

**Authentication Failed:**
- Verify username/password
- Check user permissions in RouterOS
- Try logging in via Winbox first

**Device Not Found:**
- Check device ID in `devices.json`
- Run `List my MikroTik devices` to see available IDs

### Import Errors

**If you see "No module named 'mikrotik_mcp'":**
```bash
# Make sure you're in the right directory
cd path/to/Mikrotik

# Install in development mode
pip install -e .
```

## Development

### Run in Development Mode

```bash
python -m mikrotik_mcp.server
```

### Testing Configuration

```python
python -c "
from mikrotik_mcp.device_manager import DeviceManager
import asyncio

async def test():
    dm = DeviceManager()
    await dm.load_devices()
    print(f'Loaded {len(dm.list_devices())} devices')

asyncio.run(test())
"
```

### Virtual Environment (Optional)

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install
pip install -e .
```

## Security

### Best Practices

1. **Never commit `devices.json`** - It contains passwords
2. **Use SSH instead of Telnet** - Telnet is unencrypted
3. **Strong passwords** - Use complex RouterOS passwords
4. **Firewall rules** - Limit management access
5. **Regular updates** - Keep RouterOS updated

### File Permissions

```bash
# Linux/macOS - protect devices.json
chmod 600 devices.json
```

## Comparison: Python vs TypeScript

| Feature | Python | TypeScript |
|---------|--------|------------|
| Installation | `pip install -e .` | `npm install && npm run build` |
| Deployment | Direct execution | Build required |
| Auto-start | ✓ Automatic | ✓ Automatic |
| Dependencies | Fewer | More (node_modules) |
| Performance | Fast enough | Slightly faster |
| Type Safety | Runtime (Pydantic) | Compile-time |
| Debugging | Easier | More complex |

**Recommendation:** Use Python for simplicity, TypeScript for large-scale deployments.

## Advanced Usage

### Custom Commands

```python
# Execute any RouterOS command
"Execute '/interface wireless registration-table print' on my-router"
```

### Multiple Devices

```python
# Configure multiple routers in devices.json
"Connect to router-branch and show me the firewall rules"
"What's the uptime on router-main?"
```

### Scripting

```bash
# You can also use it programmatically
python -c "
from mikrotik_mcp.device_manager import DeviceManager
import asyncio

async def main():
    dm = DeviceManager()
    await dm.load_devices()
    await dm.connect_to_device('my-router')
    result = await dm.execute_command('my-router', '/system resource print')
    print(result.output)
    await dm.disconnect_all()

asyncio.run(main())
"
```

## FAQ

**Q: Do I need to keep a terminal open?**
A: No! Claude Desktop starts and stops the server automatically.

**Q: Can I use both Python and TypeScript versions?**
A: Yes, but configure only one in Claude Desktop at a time.

**Q: How do I update?**
A: Run `pip install -e . --upgrade` or re-run the install script.

**Q: Can I connect to multiple routers simultaneously?**
A: Yes! Add multiple devices to `devices.json`.

**Q: Is this secure?**
A: SSH connections are encrypted. Keep `devices.json` secure.

**Q: Can I use SSH keys instead of passwords?**
A: Not yet - this feature is planned for a future release.

## Support

For issues or questions:
1. Check this README
2. Verify your configuration
3. Check the Claude Desktop logs
4. Test manual connection to your router

## License

MIT

## Credits

Built with:
- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk) - Model Context Protocol
- [Paramiko](https://www.paramiko.org/) - SSH client
- [telnetlib3](https://telnetlib3.readthedocs.io/) - Telnet client
- [routeros-api](https://github.com/socialwifi/RouterOS-api) - MikroTik API
- [Pydantic](https://docs.pydantic.dev/) - Data validation

---

**Happy routing with Python! 🐍🚀**
