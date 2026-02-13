#!/bin/bash
# Uninstall script for MikroTik MCP Server
# Removes the package and optionally cleans up data files

set -e

echo "========================================"
echo "MikroTik MCP Server - Uninstall Script"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10 or higher first"
    exit 1
fi

echo "This script will:"
echo "1. Uninstall the mikrotik-mcp-server package"
echo "2. Optionally remove configuration and data files"
echo ""

# Confirm uninstall
read -p "Are you sure you want to uninstall? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo "[Step 1/2] Uninstalling mikrotik-mcp-server package..."
echo "========================================"
pip3 uninstall -y mikrotik-mcp-server || {
    echo ""
    echo "WARNING: Package may not be installed or uninstall failed"
    echo "Continuing with cleanup..."
}

if [ $? -eq 0 ]; then
    echo ""
    echo "[OK] Package uninstalled successfully"
fi

echo ""
echo "[Step 2/2] Data cleanup options"
echo "========================================"
echo "The following files and directories may contain your data:"
echo "- devices.json (device configurations)"
echo "- backups/ (configuration backups)"
echo "- audit.db (command history database)"
echo "- .env (environment variables)"
echo "- htmlcov/ (test coverage reports)"
echo "- .pytest_cache/ (pytest cache)"
echo "- __pycache__/ (Python cache files)"
echo ""

read -p "Do you want to remove these files? (y/N): " CLEANUP
if [[ "$CLEANUP" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Removing data files..."

    # Remove cache directories
    if [ -d "__pycache__" ]; then
        rm -rf __pycache__
        echo "- Removed __pycache__/"
    fi

    if [ -d "mikrotik_mcp/__pycache__" ]; then
        rm -rf mikrotik_mcp/__pycache__
        echo "- Removed mikrotik_mcp/__pycache__/"
    fi

    if [ -d "mikrotik_mcp/connections/__pycache__" ]; then
        rm -rf mikrotik_mcp/connections/__pycache__
        echo "- Removed mikrotik_mcp/connections/__pycache__/"
    fi

    if [ -d "mikrotik_mcp/modules/__pycache__" ]; then
        rm -rf mikrotik_mcp/modules/__pycache__
        echo "- Removed mikrotik_mcp/modules/__pycache__/"
    fi

    if [ -d "tests/__pycache__" ]; then
        rm -rf tests/__pycache__
        echo "- Removed tests/__pycache__/"
    fi

    if [ -d ".pytest_cache" ]; then
        rm -rf .pytest_cache
        echo "- Removed .pytest_cache/"
    fi

    if [ -d "htmlcov" ]; then
        rm -rf htmlcov
        echo "- Removed htmlcov/"
    fi

    if [ -f ".coverage" ]; then
        rm -f .coverage
        echo "- Removed .coverage"
    fi

    # Ask about backups separately
    echo ""
    read -p "Remove configuration backups (backups/)? (y/N): " BACKUP_CLEANUP
    if [[ "$BACKUP_CLEANUP" =~ ^[Yy]$ ]]; then
        if [ -d "backups" ]; then
            rm -rf backups
            echo "- Removed backups/"
        fi
    else
        echo "- Kept backups/"
    fi

    # Ask about audit database separately
    read -p "Remove command history database (audit.db)? (y/N): " AUDIT_CLEANUP
    if [[ "$AUDIT_CLEANUP" =~ ^[Yy]$ ]]; then
        if [ -f "audit.db" ]; then
            rm -f audit.db
            echo "- Removed audit.db"
        fi
    else
        echo "- Kept audit.db"
    fi

    # Ask about devices.json separately
    read -p "Remove device configuration (devices.json)? (y/N): " DEVICES_CLEANUP
    if [[ "$DEVICES_CLEANUP" =~ ^[Yy]$ ]]; then
        if [ -f "devices.json" ]; then
            rm -f devices.json
            echo "- Removed devices.json"
        fi
    else
        echo "- Kept devices.json"
    fi

    # Ask about .env separately
    read -p "Remove environment variables file (.env)? (y/N): " ENV_CLEANUP
    if [[ "$ENV_CLEANUP" =~ ^[Yy]$ ]]; then
        if [ -f ".env" ]; then
            rm -f .env
            echo "- Removed .env"
        fi
    else
        echo "- Kept .env"
    fi

    echo ""
    echo "[OK] Cleanup completed"
else
    echo ""
    echo "Skipped data file cleanup"
    echo "Your configuration and backups are preserved"
fi

echo ""
echo "========================================"
echo "Uninstall Complete!"
echo "========================================"
echo ""
echo "The MikroTik MCP Server has been uninstalled."
echo ""
echo "If you kept your configuration files, you can reinstall later with:"
echo "  ./install.sh"
echo ""
