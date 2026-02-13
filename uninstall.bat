@echo off
REM Uninstall script for MikroTik MCP Server
REM Removes the package and optionally cleans up data files

echo ========================================
echo MikroTik MCP Server - Uninstall Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher first
    pause
    exit /b 1
)

echo This script will:
echo 1. Uninstall the mikrotik-mcp-server package
echo 2. Optionally remove configuration and data files
echo.

REM Confirm uninstall
set /p CONFIRM="Are you sure you want to uninstall? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Uninstall cancelled.
    pause
    exit /b 0
)

echo.
echo [Step 1/2] Uninstalling mikrotik-mcp-server package...
echo ========================================
pip uninstall -y mikrotik-mcp-server

if errorlevel 1 (
    echo.
    echo WARNING: Package may not be installed or uninstall failed
    echo Continuing with cleanup...
) else (
    echo.
    echo [OK] Package uninstalled successfully
)

echo.
echo [Step 2/2] Data cleanup options
echo ========================================
echo The following files and directories may contain your data:
echo - devices.json (device configurations)
echo - backups/ (configuration backups)
echo - audit.db (command history database)
echo - .env (environment variables)
echo - htmlcov/ (test coverage reports)
echo - .pytest_cache/ (pytest cache)
echo - __pycache__/ (Python cache files)
echo.

set /p CLEANUP="Do you want to remove these files? (y/N): "
if /i "%CLEANUP%"=="y" (
    echo.
    echo Removing data files...

    REM Remove cache directories
    if exist "__pycache__" (
        rmdir /s /q __pycache__ 2>nul
        echo - Removed __pycache__/
    )

    if exist "mikrotik_mcp\__pycache__" (
        rmdir /s /q mikrotik_mcp\__pycache__ 2>nul
        echo - Removed mikrotik_mcp\__pycache__/
    )

    if exist "mikrotik_mcp\connections\__pycache__" (
        rmdir /s /q mikrotik_mcp\connections\__pycache__ 2>nul
        echo - Removed mikrotik_mcp\connections\__pycache__/
    )

    if exist "mikrotik_mcp\modules\__pycache__" (
        rmdir /s /q mikrotik_mcp\modules\__pycache__ 2>nul
        echo - Removed mikrotik_mcp\modules\__pycache__/
    )

    if exist "tests\__pycache__" (
        rmdir /s /q tests\__pycache__ 2>nul
        echo - Removed tests\__pycache__/
    )

    if exist ".pytest_cache" (
        rmdir /s /q .pytest_cache 2>nul
        echo - Removed .pytest_cache/
    )

    if exist "htmlcov" (
        rmdir /s /q htmlcov 2>nul
        echo - Removed htmlcov/
    )

    if exist ".coverage" (
        del /f /q .coverage 2>nul
        echo - Removed .coverage
    )

    REM Ask about backups separately
    echo.
    set /p BACKUP_CLEANUP="Remove configuration backups (backups/)? (y/N): "
    if /i "%BACKUP_CLEANUP%"=="y" (
        if exist "backups" (
            rmdir /s /q backups 2>nul
            echo - Removed backups/
        )
    ) else (
        echo - Kept backups/
    )

    REM Ask about audit database separately
    set /p AUDIT_CLEANUP="Remove command history database (audit.db)? (y/N): "
    if /i "%AUDIT_CLEANUP%"=="y" (
        if exist "audit.db" (
            del /f /q audit.db 2>nul
            echo - Removed audit.db
        )
    ) else (
        echo - Kept audit.db
    )

    REM Ask about devices.json separately
    set /p DEVICES_CLEANUP="Remove device configuration (devices.json)? (y/N): "
    if /i "%DEVICES_CLEANUP%"=="y" (
        if exist "devices.json" (
            del /f /q devices.json 2>nul
            echo - Removed devices.json
        )
    ) else (
        echo - Kept devices.json
    )

    REM Ask about .env separately
    set /p ENV_CLEANUP="Remove environment variables file (.env)? (y/N): "
    if /i "%ENV_CLEANUP%"=="y" (
        if exist ".env" (
            del /f /q .env 2>nul
            echo - Removed .env
        )
    ) else (
        echo - Kept .env
    )

    echo.
    echo [OK] Cleanup completed
) else (
    echo.
    echo Skipped data file cleanup
    echo Your configuration and backups are preserved
)

echo.
echo ========================================
echo Uninstall Complete!
echo ========================================
echo.
echo The MikroTik MCP Server has been uninstalled.
echo.
echo If you kept your configuration files, you can reinstall later with:
echo   install.bat
echo.

pause
