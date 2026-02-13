"""Unit tests for FirewallManager."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from mikrotik_mcp.modules.firewall import FirewallManager
from mikrotik_mcp.models import ConnectionResult


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_filter_rule():
    """Test adding a firewall filter rule."""
    mock_device_manager = MagicMock()
    mock_device_manager.execute_command = AsyncMock(
        return_value=ConnectionResult(success=True, output="Rule added")
    )

    manager = FirewallManager(mock_device_manager)

    result = await manager.add_filter_rule(
        device_id="test_router",
        chain="input",
        action="accept",
        protocol="tcp",
        dst_port="22",
        comment="Allow SSH"
    )

    assert result.success
    mock_device_manager.execute_command.assert_called_once()
    call_args = mock_device_manager.execute_command.call_args[0]
    assert "chain=input" in call_args[1]
    assert "action=accept" in call_args[1]
    assert "protocol=tcp" in call_args[1]
    assert "dst-port=22" in call_args[1]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_nat_rule():
    """Test adding a NAT rule."""
    mock_device_manager = MagicMock()
    mock_device_manager.execute_command = AsyncMock(
        return_value=ConnectionResult(success=True, output="NAT rule added")
    )

    manager = FirewallManager(mock_device_manager)

    result = await manager.add_nat_rule(
        device_id="test_router",
        chain="srcnat",
        action="masquerade",
        out_interface="ether1"
    )

    assert result.success
    call_args = mock_device_manager.execute_command.call_args[0]
    assert "chain=srcnat" in call_args[1]
    assert "action=masquerade" in call_args[1]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_add_address_list():
    """Test adding address to address list."""
    mock_device_manager = MagicMock()
    mock_device_manager.execute_command = AsyncMock(
        return_value=ConnectionResult(success=True, output="Address added")
    )

    manager = FirewallManager(mock_device_manager)

    result = await manager.add_address_list(
        device_id="test_router",
        list_name="blacklist",
        address="1.2.3.4",
        comment="Bad IP"
    )

    assert result.success
    call_args = mock_device_manager.execute_command.call_args[0]
    assert "list=blacklist" in call_args[1]
    assert "address=1.2.3.4" in call_args[1]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_address_list():
    """Test getting address list entries."""
    mock_device_manager = MagicMock()
    mock_device_manager.execute_command = AsyncMock(
        return_value=ConnectionResult(success=True, output="Address list output")
    )

    manager = FirewallManager(mock_device_manager)

    result = await manager.get_address_list(
        device_id="test_router",
        list_name="blacklist"
    )

    assert result.success
    assert result.output == "Address list output"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_remove_filter_rule():
    """Test removing a filter rule."""
    mock_device_manager = MagicMock()
    mock_device_manager.execute_command = AsyncMock(
        return_value=ConnectionResult(success=True, output="Rule removed")
    )

    manager = FirewallManager(mock_device_manager)

    result = await manager.remove_filter_rule(
        device_id="test_router",
        rule_id="5"
    )

    assert result.success
    call_args = mock_device_manager.execute_command.call_args[0]
    assert "/ip firewall filter remove 5" in call_args[1]
