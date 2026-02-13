# Contributing to MikroTik MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mikrotik-mcp-server.git
   cd mikrotik-mcp-server
   ```
3. **Install dependencies**:
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🔧 Development Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git
- Access to a MikroTik router (for testing)

### Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

This includes:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities

### Configure Test Environment
1. Copy example configuration:
   ```bash
   cp devices.json.example devices.json
   cp .env.example .env
   ```
2. Edit `devices.json` with test router details
3. Edit `.env` if using environment variables

## 📝 Coding Standards

### Python Style
- Follow **PEP 8** guidelines
- Use **type hints** for all functions and methods
- Write **docstrings** for all public functions (Google style)
- Maximum line length: **100 characters**

### Code Formatting
Format code with Black before committing:
```bash
black mikrotik_mcp/
```

### Type Checking
Run mypy to check types:
```bash
mypy mikrotik_mcp/
```

### Example Code Style
```python
async def execute_command(
    self, device_id: str, command: str
) -> ConnectionResult:
    """Execute a RouterOS command on the specified device.

    Args:
        device_id: Unique identifier of the device
        command: RouterOS command to execute

    Returns:
        ConnectionResult containing output and status

    Raises:
        DeviceNotFoundError: If device_id doesn't exist
        NotConnectedError: If device isn't connected
    """
    # Implementation
    pass
```

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=mikrotik_mcp --cov-report=html --cov-report=term
```

### Run Specific Test File
```bash
pytest tests/test_device_manager.py
```

### Run Specific Test
```bash
pytest tests/test_device_manager.py::TestDeviceManager::test_connect_success
```

### Writing Tests
- Place tests in `tests/` directory
- Use `test_` prefix for test files and functions
- Use pytest fixtures for common setup
- Mock external connections (SSH, API, Telnet)
- Aim for >80% code coverage

Example test:
```python
import pytest
from mikrotik_mcp.device_manager import DeviceManager

@pytest.fixture
async def device_manager():
    """Provide initialized DeviceManager."""
    dm = DeviceManager()
    await dm.load_devices()
    yield dm
    await dm.disconnect_all()

async def test_connect_success(device_manager):
    """Test successful device connection."""
    result = await device_manager.connect_to_device("test-router")
    assert result is True
```

## 📦 Pull Request Process

### Before Submitting
1. **Run all tests**: Ensure tests pass
   ```bash
   pytest --cov=mikrotik_mcp
   ```

2. **Format code**: Run Black
   ```bash
   black mikrotik_mcp/
   ```

3. **Type check**: Run mypy
   ```bash
   mypy mikrotik_mcp/
   ```

4. **Update documentation**: If adding features, update README

5. **Add tests**: New features need test coverage

### Commit Messages
Use conventional commit format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Examples:
```
feat: add WireGuard VPN support
fix: resolve SSH connection timeout issue
docs: update installation instructions
test: add firewall manager tests
```

### Pull Request Template
When creating a PR, include:
- **Description**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Testing**: How was it tested?
- **Breaking Changes**: Any backward incompatibilities?
- **Checklist**:
  - [ ] Tests pass
  - [ ] Code formatted with Black
  - [ ] Type hints added
  - [ ] Documentation updated
  - [ ] Changelog updated (if applicable)

## 🎯 Contribution Ideas

### Good First Issues
- Add more RouterOS command mappings
- Improve error messages
- Add example configuration profiles
- Write additional tests
- Improve documentation

### Feature Requests
- Wireless management tools
- Queue management
- Hotspot configuration
- User management
- Backup scheduling
- SSH key authentication

### Bug Reports
When reporting bugs, include:
- Python version
- Operating system
- RouterOS version
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

## 🔒 Security

If you discover a security vulnerability:
1. **Do NOT** open a public issue
2. Email details to the maintainers
3. Wait for confirmation before disclosure

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Questions?

- Check existing [issues](https://github.com/YOUR_USERNAME/mikrotik-mcp-server/issues)
- Review [documentation](README_PYTHON.md)
- Ask in discussions

## 🎉 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!
