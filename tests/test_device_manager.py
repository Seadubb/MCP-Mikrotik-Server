"""Unit tests for DeviceManager."""

import pytest
from pathlib import Path
from mikrotik_mcp.device_manager import DeviceManager
from mikrotik_mcp.exceptions import DeviceNotFoundError, NotConnectedError
from tests.mocks.mock_connection import MockConnection


@pytest.mark.unit
@pytest.mark.asyncio
async def test_load_devices(tmp_path):
    """Test loading devices from configuration file."""
    devices_file = tmp_path / "devices.json"
    devices_file.write_text('''
    {
        "devices": [
            {
                "id": "router1",
                "name": "Router 1",
                "host": "192.168.1.1",
                "port": 8728,
                "username": "admin",
                "password": "password",
                "connection_type": "api",
                "routeros_version": 7
            }
        ]
    }
    ''')

    manager = DeviceManager(config_path=str(devices_file), enable_audit=False)
    await manager.load_devices()

    assert len(manager.devices) == 1
    assert "router1" in manager.devices
    assert manager.devices["router1"].name == "Router 1"

    await manager.disconnect_all()


@pytest.mark.unit
def test_get_device(device_manager):
    """Test getting device configuration."""
    device = device_manager.get_device("test_router")

    assert device is not None
    assert device.id == "test_router"
    assert device.name == "Test Router"


@pytest.mark.unit
def test_get_nonexistent_device(device_manager):
    """Test getting non-existent device returns None."""
    device = device_manager.get_device("nonexistent")
    assert device is None


@pytest.mark.unit
def test_list_devices(device_manager):
    """Test listing all devices."""
    devices = device_manager.list_devices()

    assert len(devices) == 1
    assert devices[0].id == "test_router"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_connect_to_device_not_found():
    """Test connecting to non-existent device raises error."""
    manager = DeviceManager(enable_audit=False)
    manager.devices = {}

    with pytest.raises(DeviceNotFoundError):
        await manager.connect_to_device("nonexistent")


@pytest.mark.unit
def test_is_connected(device_manager):
    """Test checking connection status."""
    assert device_manager.is_connected("test_router") is False


@pytest.mark.unit
def test_get_connection_status(device_manager):
    """Test getting connection status for all devices."""
    status = device_manager.get_connection_status()

    assert "test_router" in status
    assert status["test_router"] is False
