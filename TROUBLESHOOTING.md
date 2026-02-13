# MikroTik MCP Server - Troubleshooting Guide

Common issues and solutions for the MikroTik MCP Server.

---

## Error: "ModuleNotFoundError: No module named 'aiosqlite'"

### Symptom:
```
Traceback (most recent call last):
  File "...\mikrotik_mcp\server.py", line 12, in <module>
    from .device_manager import DeviceManager
  File "...\mikrotik_mcp\device_manager.py", line 13, in <module>
    from .audit import AuditLogger
  File "...\mikrotik_mcp\audit.py", line 3, in <module>
    import aiosqlite
ModuleNotFoundError: No module named 'aiosqlite'
```

### Cause:
The `aiosqlite` dependency is not installed in your Python environment.

### Solution:

**Option 1: Install the missing dependency**
```bash
pip install aiosqlite
```

**Option 2: Reinstall the package**
```bash
pip uninstall mikrotik-mcp-server
pip install -e .
```

**Option 3: Install all dependencies manually**
```bash
pip install -r requirements.txt
```

---

## Error: "ModuleNotFoundError: No module named 'pyyaml'"

### Symptom:
```
ModuleNotFoundError: No module named 'yaml'
```

### Cause:
The `pyyaml` dependency (required for configuration profiles) is not installed.

### Solution:
```bash
pip install pyyaml
```

Or reinstall with all dependencies:
```bash
pip install -r requirements.txt
```

---

## Error: "ModuleNotFoundError: No module named 'dotenv'"

### Symptom:
```
ModuleNotFoundError: No module named 'dotenv'
```

### Cause:
The `python-dotenv` dependency is not installed.

### Solution:
```bash
pip install python-dotenv
```

---

## Error: "Server disconnected" in Claude Desktop

### Symptom:
Claude Desktop shows:
```
Server disconnected. For troubleshooting guidance, please visit our debugging documentation
```

### Cause:
The MCP server process is crashing, usually due to missing dependencies or configuration errors.

### Solution:

**1. Check Claude Desktop logs:**
- Windows: `%APPDATA%\Claude\logs\`
- macOS: `~/Library/Logs/Claude/`
- Linux: `~/.config/Claude/logs/`

**2. Look for the actual error** in the log file (usually shows Python traceback)

**3. Common fixes:**
```bash
# Reinstall all dependencies
pip install -r requirements.txt

# Or reinstall the package
pip uninstall mikrotik-mcp-server
pip install -e .
```

---

## Error: "Device configuration not found"

### Symptom:
```
ConfigurationError: Device configuration not found at /path/to/devices.json
```

### Cause:
The `devices.json` configuration file is missing or in the wrong location.

### Solution:

**1. Check if devices.json exists:**
```bash
# Windows
dir devices.json

# Linux/macOS
ls -l devices.json
```

**2. Create devices.json if missing:**
```json
{
  "devices": [
    {
      "id": "router-main",
      "name": "Main Router",
      "host": "192.168.88.1",
      "port": 22,
      "username": "admin",
      "password": "your-password",
      "connectionType": "ssh",
      "routerOSVersion": 7
    }
  ]
}
```

**3. Ensure it's in the project root** (same directory as `mikrotik_mcp/`)

---

## Error: Connection Timeout

### Symptom:
```
TimeoutError: Connection to device router-main timed out
```

### Cause:
- Device is offline
- Firewall blocking connection
- Wrong IP address
- Wrong port number

### Solution:

**1. Verify device is reachable:**
```bash
ping 192.168.88.1
```

**2. Check port is open:**
```bash
# Test SSH (port 22)
telnet 192.168.88.1 22

# Test API (port 8728)
telnet 192.168.88.1 8728
```

**3. Verify firewall rules** on the MikroTik device:
```
/ip firewall filter print
```

**4. Check devices.json** has correct IP and port

---

## Error: Authentication Failed

### Symptom:
```
AuthenticationError: Authentication failed for device router-main
```

### Cause:
- Incorrect username or password
- User doesn't have API/SSH access
- User is disabled

### Solution:

**1. Verify credentials** in devices.json

**2. Test manually:**
```bash
# SSH
ssh admin@192.168.88.1

# API
# Use a RouterOS API client to test
```

**3. Check user permissions** on MikroTik:
```
/user print
/user group print
```

**4. Ensure user has required permissions:**
- API access: User must be in a group with API policy
- SSH access: SSH service must be enabled

---

## Error: "Command not found: mikrotik-mcp"

### Symptom:
```bash
mikrotik-mcp
# bash: mikrotik-mcp: command not found
```

### Cause:
The package is not installed, or Python Scripts directory is not in PATH.

### Solution:

**1. Verify installation:**
```bash
pip show mikrotik-mcp-server
```

**2. If not installed:**
```bash
pip install -e .
# or
./install.bat  # Windows
./install.sh   # Linux/macOS
```

**3. If installed but command not found, add Python Scripts to PATH:**

**Windows:**
```cmd
# Add to PATH (replace with your Python version):
set PATH=%PATH%;C:\Python313\Scripts
```

**Linux/macOS:**
```bash
# Add to PATH
export PATH=$PATH:~/.local/bin
```

---

## Error: Python Version Too Old

### Symptom:
```
ERROR: This package requires Python >=3.10
```

### Cause:
You're using Python 3.9 or older.

### Solution:

**1. Check Python version:**
```bash
python --version
```

**2. Install Python 3.10 or higher:**
- Download from: https://www.python.org/downloads/
- Or use a version manager (pyenv, conda, etc.)

**3. Reinstall with correct Python version:**
```bash
python3.13 -m pip install -e .
```

---

## Debugging Tips

### Enable Debug Logging

Add to your Python code or startup:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check MCP Server is Running

**Test directly:**
```bash
python -m mikrotik_mcp.server
```

Should start without errors and wait for MCP messages.

### View Real-time Logs

The server logs to stderr, which appears in Claude Desktop logs.

**Monitor logs in real-time:**

**Windows:**
```cmd
type "%APPDATA%\Claude\logs\mcp-server-mikrotik.log"
```

**Linux/macOS:**
```bash
tail -f ~/.config/Claude/logs/mcp-server-mikrotik.log
```

### Test Connection Manually

```python
from mikrotik_mcp.device_manager import DeviceManager
import asyncio

async def test():
    dm = DeviceManager()
    await dm.load_devices()
    await dm.connect_to_device("router-main")
    result = await dm.execute_command("router-main", "/system resource print")
    print(result.output)
    await dm.disconnect_all()

asyncio.run(test())
```

---

## Common Installation Issues

### Issue: "pip: command not found"

**Solution:**
```bash
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### Issue: "Permission denied"

**Windows (run as Administrator):**
```cmd
# Right-click Command Prompt → Run as Administrator
pip install -e .
```

**Linux/macOS:**
```bash
# Install to user directory
pip install --user -e .
```

### Issue: Multiple Python versions

**Solution: Specify Python version explicitly:**
```bash
# Use python3
python3 -m pip install -e .

# Or specific version
python3.13 -m pip install -e .
```

---

## Performance Issues

### Slow Command Execution

**Cause:** Network latency or device overload

**Solutions:**
1. Increase timeout in devices.json
2. Use caching for read-only commands
3. Check network connection quality

### High Memory Usage

**Cause:** Large audit database or many cached results

**Solutions:**
1. Disable audit logging (set `enable_audit=False`)
2. Clear cache periodically
3. Archive old audit.db file

---

## Getting Help

If issues persist:

1. **Check logs** in Claude Desktop log directory
2. **Search issues** on GitHub
3. **Create new issue** with:
   - Error message
   - Python version (`python --version`)
   - Operating system
   - devices.json (without passwords)
   - Full error traceback from logs

---

## Quick Checklist

Before reporting an issue, verify:

- [ ] Python 3.10 or higher installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] devices.json exists and is valid JSON
- [ ] MikroTik device is reachable (ping)
- [ ] Credentials are correct
- [ ] Firewall allows connection
- [ ] User has required permissions
- [ ] Claude Desktop logs checked

---

## Useful Commands

```bash
# Show package info
pip show mikrotik-mcp-server

# List installed packages
pip list | grep mikrotik

# Check Python version
python --version

# Test import
python -c "from mikrotik_mcp import server"

# Reinstall from scratch
pip uninstall mikrotik-mcp-server
pip install -e .

# View all dependencies
pip show mikrotik-mcp-server | grep Requires
```
