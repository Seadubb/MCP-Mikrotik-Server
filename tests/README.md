# MikroTik MCP Server - Test Suite

Comprehensive test suite for the MikroTik MCP Server.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── test_device_manager.py   # Device manager unit tests
├── test_firewall_manager.py # Firewall module unit tests
├── test_profile_manager.py  # Profile manager unit tests
├── integration/             # Integration tests
│   └── test_full_workflow.py
├── mocks/                   # Mock objects
│   ├── mock_connection.py
│   └── mock_device.py
└── performance/             # Performance tests (future)
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Unit Tests Only
```bash
pytest -m unit
```

### Run Integration Tests Only
```bash
pytest -m integration
```

### Run With Coverage Report
```bash
pytest --cov=mikrotik_mcp --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_device_manager.py
```

### Run Specific Test Function
```bash
pytest tests/test_device_manager.py::test_load_devices
```

### Run Tests in Verbose Mode
```bash
pytest -v
```

### Skip Slow Tests
```bash
pytest -m "not slow"
```

## Test Markers

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, test component interaction)
- `@pytest.mark.slow` - Slow tests
- `@pytest.mark.requires_device` - Tests that require a real MikroTik device

## Coverage Goals

- Target: 70%+ code coverage
- Focus on critical paths
- All public APIs should be tested

## Writing New Tests

### Unit Test Template
```python
import pytest
from mikrotik_mcp.modules.your_module import YourClass


@pytest.mark.unit
@pytest.mark.asyncio
async def test_your_function():
    """Test description."""
    # Arrange
    mock_dependency = MagicMock()

    # Act
    result = await your_function(mock_dependency)

    # Assert
    assert result is not None
```

### Integration Test Template
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_workflow(tmp_path):
    """Test complete workflow."""
    # Setup
    manager = DeviceManager(config_path=str(tmp_path / "devices.json"))

    # Execute workflow
    await manager.load_devices()
    devices = manager.list_devices()

    # Verify
    assert len(devices) > 0

    # Cleanup
    await manager.disconnect_all()
```

## Mock Objects

Use mock objects to test without real devices:

```python
from tests.mocks.mock_connection import MockConnection

# Create mock connection
mock_conn = MockConnection(test_device_config)
mock_conn.set_mock_response("/interface print", "mocked output")

# Use in tests
result = await mock_conn.execute("/interface print")
assert result.success
```

## Continuous Integration

Tests run automatically on every commit via GitHub Actions. See `.github/workflows/test.yml`.

## Troubleshooting

### Tests Fail Due to Missing Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Coverage Reports Not Generated
```bash
pip install pytest-cov
```

### Async Tests Not Running
```bash
pip install pytest-asyncio
```

## Best Practices

1. **Test Isolation** - Each test should be independent
2. **Use Fixtures** - Share setup code via pytest fixtures
3. **Mock External Dependencies** - Don't rely on real MikroTik devices
4. **Clear Test Names** - Use descriptive function names
5. **Test Both Success and Failure** - Cover error cases
6. **Keep Tests Fast** - Use mocks to speed up tests
7. **Document Complex Tests** - Add docstrings explaining what's being tested
