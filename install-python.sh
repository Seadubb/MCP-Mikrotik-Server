#!/bin/bash

echo "========================================"
echo "MikroTik MCP Server (Python) - Installation"
echo "========================================"
echo

echo "[1/3] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

python3 --version
echo

echo "[2/3] Installing Python dependencies..."
pip3 install -e .
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo

echo "[3/3] Verifying installation..."
python3 -c "import mikrotik_mcp; print('✓ Package installed successfully')"
if [ $? -ne 0 ]; then
    echo "ERROR: Package verification failed"
    exit 1
fi
echo

echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo
echo "Next Steps:"
echo "1. Configure your devices in devices.json"
echo "2. Add this to your Claude Desktop config:"
echo
echo '   {'
echo '     "mcpServers": {'
echo '       "mikrotik": {'
echo '         "command": "python3",'
echo '         "args": ["-m", "mikrotik_mcp.server"]'
echo '       }'
echo '     }'
echo '   }'
echo
echo "3. Restart Claude Desktop"
echo
echo "For detailed setup, see README_PYTHON.md"
echo

chmod +x install-python.sh
