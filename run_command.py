#!/usr/bin/env python3
"""Quick helper to execute RouterOS commands via the MCP device manager."""
import sys
import asyncio
from mikrotik_mcp.device_manager import DeviceManager

async def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "/system resource print"
    dm = DeviceManager()
    await dm.load_devices()
    await dm.connect_to_device("hap-ax-lite")
    result = await dm.execute_command("hap-ax-lite", cmd)
    if result.success:
        output = (result.output or "").strip()
        if output:
            print(output)
        else:
            print("OK (no output)")
    else:
        print(f"ERROR: {result.error}", file=sys.stderr)
        sys.exit(1)
    await dm.disconnect_all()

asyncio.run(main())
