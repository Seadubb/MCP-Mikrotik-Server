"""Pytest configuration and shared fixtures."""

import pytest
import asyncio
from pathlib import Path
from mikrotik_mcp.models import DeviceConfig, ConnectionType
from mikrotik_mcp.device_manager import DeviceManager


@pytest.fixture
def test_device_config():
    """Provide a test device configuration."""
    return DeviceConfig(
        id="test_router",
        name="Test Router",
        host="192.168.1.1",
        port=8728,
        username="admin",
        password="test_password",
        connection_type=ConnectionType.API,
        routeros_version=7
    )


@pytest.fixture
def test_device_configs():
    """Provide multiple test device configurations."""
    return [
        DeviceConfig(
            id="router1",
            name="Router 1",
            host="192.168.1.1",
            port=22,
            username="admin",
            password="pass1",
            connection_type=ConnectionType.SSH,
            routeros_version=7
        ),
        DeviceConfig(
            id="router2",
            name="Router 2",
            host="192.168.1.2",
            port=8728,
            username="admin",
            password="pass2",
            connection_type=ConnectionType.API,
            routeros_version=6
        ),
    ]


@pytest.fixture
async def device_manager(tmp_path):
    """Provide a device manager with temporary config."""
    # Create temporary devices.json
    devices_file = tmp_path / "devices.json"
    devices_file.write_text('''
    {
        "devices": [
            {
                "id": "test_router",
                "name": "Test Router",
                "host": "192.168.1.1",
                "port": 8728,
                "username": "admin",
                "password": "test_password",
                "connection_type": "api",
                "routeros_version": 7
            }
        ]
    }
    ''')

    manager = DeviceManager(config_path=str(devices_file), enable_audit=False)
    await manager.load_devices()

    yield manager

    await manager.disconnect_all()


@pytest.fixture
def mock_command_output():
    """Provide mock RouterOS command outputs."""
    return {
        "/interface print": """
            name                           type     actual-mtu    mac-address
            ether1                         ether    1500          AA:BB:CC:DD:EE:01
            ether2                         ether    1500          AA:BB:CC:DD:EE:02
            bridge                         bridge   1500          AA:BB:CC:DD:EE:03
        """,
        "/ip address print": """
            #   address            network          interface
            0   192.168.1.1/24     192.168.1.0      ether1
            1   10.0.0.1/24        10.0.0.0         ether2
        """,
        "/system resource print": """
            uptime: 1d2h3m4s
            version: 7.10.2
            cpu: ARMv7
            cpu-count: 2
            free-memory: 512.0MiB
            total-memory: 1024.0MiB
        """,
        "/system identity print": """
            name: TestRouter
        """,
    }
