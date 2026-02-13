"""Unit tests for ProfileManager."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from mikrotik_mcp.modules.profiles import ProfileManager


@pytest.mark.unit
def test_list_profiles(tmp_path):
    """Test listing available profiles."""
    # Create test profile
    network_dir = tmp_path / "network"
    network_dir.mkdir()

    profile_file = network_dir / "test-profile.yaml"
    profile_file.write_text("""
profile:
  name: "Test Profile"
  description: "A test configuration profile"
  variables: []
    """)

    mock_dm = MagicMock()
    manager = ProfileManager(mock_dm, profiles_dir=tmp_path)

    profiles = manager.list_profiles(category="network")

    assert len(profiles) == 1
    assert profiles[0]['id'] == 'test-profile'
    assert profiles[0]['name'] == 'Test Profile'
    assert profiles[0]['category'] == 'network'


@pytest.mark.unit
def test_get_profile(tmp_path):
    """Test getting a specific profile."""
    network_dir = tmp_path / "network"
    network_dir.mkdir()

    profile_file = network_dir / "test-profile.yaml"
    profile_file.write_text("""
profile:
  name: "Test Profile"
  description: "A test configuration profile"
  commands:
    - "/system identity set name=TestRouter"
    """)

    mock_dm = MagicMock()
    manager = ProfileManager(mock_dm, profiles_dir=tmp_path)

    profile = manager.get_profile("test-profile", category="network")

    assert profile is not None
    assert profile['profile']['name'] == 'Test Profile'
    assert len(profile['profile']['commands']) == 1


@pytest.mark.unit
def test_substitute_variables():
    """Test variable substitution in profiles."""
    mock_dm = MagicMock()
    manager = ProfileManager(mock_dm)

    config = {
        "interface": "${WAN_INTERFACE}",
        "address": "192.168.1.1",
        "rules": [
            "allow from ${TRUSTED_IP}",
            "deny all"
        ]
    }

    variables = {
        "WAN_INTERFACE": "ether1",
        "TRUSTED_IP": "10.0.0.5"
    }

    result = manager._substitute_variables(config, variables)

    assert result['interface'] == 'ether1'
    assert result['rules'][0] == 'allow from 10.0.0.5'
    assert result['rules'][1] == 'deny all'


@pytest.mark.unit
def test_validate_profile(tmp_path):
    """Test profile validation."""
    network_dir = tmp_path / "network"
    network_dir.mkdir()

    profile_file = network_dir / "test-profile.yaml"
    profile_file.write_text("""
profile:
  name: "Test Profile"
  description: "A test profile"
  variables: ["VAR1", "VAR2"]
    """)

    mock_dm = MagicMock()
    manager = ProfileManager(mock_dm, profiles_dir=tmp_path)

    validation = manager.validate_profile("test-profile", category="network")

    assert validation['valid'] is True
    assert len(validation['warnings']) > 0  # Should warn about required variables


@pytest.mark.unit
@pytest.mark.asyncio
async def test_apply_profile_dry_run(tmp_path):
    """Test applying profile in dry-run mode."""
    network_dir = tmp_path / "network"
    network_dir.mkdir()

    profile_file = network_dir / "simple.yaml"
    profile_file.write_text("""
profile:
  name: "Simple Profile"
  description: "Simple test"
  commands:
    - "/system identity set name=TestRouter"
    - "/interface print"
    """)

    mock_dm = MagicMock()
    manager = ProfileManager(mock_dm, profiles_dir=tmp_path)

    result = await manager.apply_profile(
        device_id="test_router",
        profile_id="simple",
        category="network",
        dry_run=True
    )

    assert result['success'] is True
    assert result['dry_run'] is True
    assert result['command_count'] == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_apply_profile_execute(tmp_path):
    """Test applying profile with execution."""
    network_dir = tmp_path / "network"
    network_dir.mkdir()

    profile_file = network_dir / "simple.yaml"
    profile_file.write_text("""
profile:
  name: "Simple Profile"
  description: "Simple test"
  commands:
    - "/system identity set name=TestRouter"
    """)

    from mikrotik_mcp.models import ConnectionResult

    mock_dm = MagicMock()
    mock_dm.execute_command = AsyncMock(
        return_value=ConnectionResult(success=True, output="OK")
    )

    manager = ProfileManager(mock_dm, profiles_dir=tmp_path)

    result = await manager.apply_profile(
        device_id="test_router",
        profile_id="simple",
        category="network",
        dry_run=False
    )

    assert result['success'] is True
    assert result['successful'] == 1
    assert result['failed'] == 0
    mock_dm.execute_command.assert_called_once()
