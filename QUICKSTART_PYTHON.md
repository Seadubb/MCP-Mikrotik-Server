# Quick Start - Python Edition

Get your MikroTik MCP Server running in **3 simple steps**!

## Step 1: Install (1 minute)

### Windows
```bash
install-python.bat
```

### Linux/macOS
```bash
chmod +x install-python.sh && ./install-python.sh
```

### What it does:
- ✓ Checks Python installation
- ✓ Installs all dependencies
- ✓ Verifies the installation

## Step 2: Configure (2 minutes)

### Edit `devices.json`

Replace with your router details:

```json
{
  "devices": [
    {
      "id": "my-router",
      "name": "My MikroTik",
      "host": "192.168.88.1",
      "port": 22,
      "username": "admin",
      "password": "your-password-here",
      "connectionType": "ssh",
      "routerOSVersion": 7,
      "timeout": 10000
    }
  ]
}
```

**Quick Config Tips:**
- `id`: Any name you want (use in commands)
- `host`: Your router's IP address
- `connectionType`: Use `"ssh"` (recommended)
- `routerOSVersion`: `6` or `7` (check your router)

### Add to Claude Desktop

**Find your config file:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Add this:**
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

**Save and close the file.**

## Step 3: Restart Claude Desktop

Close and reopen Claude Desktop.

**That's it!** The server will start automatically.

## Test It

Try these in Claude Desktop:

```
List my MikroTik devices
```

You should see your configured router(s).

```
Connect to my-router
```

Connection successful? Great!

```
Show me the system info on my-router
```

See CPU, memory, uptime? **You're all set! 🎉**

## Common First-Time Issues

### "Python not found"
**Solution:**
```bash
python --version  # Should show 3.10+
```
If not, install Python from [python.org](https://www.python.org)

### "Connection timeout"
**Check:**
1. Can you ping the router? `ping 192.168.88.1`
2. Is SSH enabled on the router?
3. Try increasing timeout to `15000` in devices.json

### "Authentication failed"
**Check:**
1. Username and password are correct
2. Try logging in via Winbox first
3. Make sure the user has appropriate permissions

### "Device not found"
**Check:**
1. The `id` in devices.json matches what you're using
2. Run `List my MikroTik devices` to see available IDs

## What Now?

### Try These Commands

```
"What interfaces does my-router have?"
"Show me the IP addresses on my-router"
"List the DHCP leases on my-router"
"What are the firewall rules on my-router?"
"Execute '/queue simple print' on my-router"
```

### Add More Routers

Just add more entries to `devices.json`:

```json
{
  "devices": [
    {
      "id": "router-main",
      "name": "Main Gateway",
      ...
    },
    {
      "id": "router-branch",
      "name": "Branch Office",
      ...
    }
  ]
}
```

### Learn More

- **Full Documentation:** [README_PYTHON.md](README_PYTHON.md)
- **All Features:** [FEATURES.md](FEATURES.md)

## Pro Tips

1. **Multiple Routers**: Add as many as you want to `devices.json`
2. **Security**: Never commit `devices.json` to git (passwords!)
3. **Connection Types**:
   - SSH (port 22) - Most secure, recommended
   - API (port 8728) - Fastest for automation
   - Telnet (port 23) - Only on trusted networks

4. **RouterOS Version**: Make sure it matches your actual version
   - Check in Winbox: System → Resources
   - Or ask Claude: "Execute '/system resource print' on my-router"

## Need Help?

1. Read the error message carefully
2. Check [README_PYTHON.md](README_PYTHON.md) troubleshooting section
3. Verify router is accessible
4. Test manual SSH connection

## Auto-Start Explained

When you configure Claude Desktop with:
```json
"command": "python",
"args": ["-m", "mikrotik_mcp.server"]
```

Claude automatically:
1. Starts the Python server when needed
2. Loads your `devices.json` configuration
3. Keeps the server running while you work
4. Stops it when you close Claude

**You don't need to do anything!** Just use Claude normally.

---

**Enjoy your automated MikroTik management! 🚀**
