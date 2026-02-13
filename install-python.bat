@echo off
echo ========================================
echo MikroTik MCP Server (Python) - Installation
echo ========================================
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://www.python.org
    pause
    exit /b 1
)

python --version
echo.

echo [2/3] Installing Python dependencies...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/3] Verifying installation...
python -c "import mikrotik_mcp; print('✓ Package installed successfully')"
if errorlevel 1 (
    echo ERROR: Package verification failed
    pause
    exit /b 1
)
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Configure your devices in devices.json
echo 2. Add this to your Claude Desktop config:
echo.
echo    {
echo      "mcpServers": {
echo        "mikrotik": {
echo          "command": "python",
echo          "args": ["-m", "mikrotik_mcp.server"]
echo        }
echo      }
echo    }
echo.
echo 3. Restart Claude Desktop
echo.
echo For detailed setup, see README_PYTHON.md
echo.
pause
