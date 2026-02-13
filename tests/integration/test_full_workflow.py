"""Integration tests for complete workflows."""

import pytest
from pathlib import Path
from mikrotik_mcp.device_manager import DeviceManager


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_manager_workflow(tmp_path):
    """Test complete device manager workflow."""
    # Create test configuration
    devices_file = tmp_path / "devices.json"
    devices_file.write_text('''
    {
        "devices": [
            {
                "id": "router1",
                "name": "Test Router 1",
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

    # Initialize device manager
    manager = DeviceManager(config_path=str(devices_file), enable_audit=False)
    await manager.load_devices()

    # Test device listing
    devices = manager.list_devices()
    assert len(devices) == 1
    assert devices[0].id == "router1"

    # Test device retrieval
    device = manager.get_device("router1")
    assert device is not None
    assert device.name == "Test Router 1"

    # Test connection status
    status = manager.get_connection_status()
    assert "router1" in status
    assert status["router1"] is False

    # Clean up
    await manager.disconnect_all()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fleet_status(tmp_path):
    """Test fleet status retrieval."""
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
            },
            {
                "id": "router2",
                "name": "Router 2",
                "host": "192.168.1.2",
                "port": 22,
                "username": "admin",
                "password": "password",
                "connection_type": "ssh",
                "routeros_version": 6
            }
        ]
    }
    ''')

    manager = DeviceManager(config_path=str(devices_file), enable_audit=False)
    await manager.load_devices()

    fleet_status = await manager.get_fleet_status()

    assert len(fleet_status) == 2
    assert all(device['connected'] is False for device in fleet_status)

    await manager.disconnect_all()
