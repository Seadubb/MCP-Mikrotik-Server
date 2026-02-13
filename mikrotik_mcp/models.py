"""Data models for MikroTik MCP Server."""

import os
import re
from enum import Enum
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field, field_validator


class ConnectionType(str, Enum):
    """Connection type enumeration."""
    SSH = "ssh"
    TELNET = "telnet"
    API = "api"


class RouterOSVersion(int, Enum):
    """RouterOS version enumeration."""
    VERSION_6 = 6
    VERSION_7 = 7


class SSHKeyConfig(BaseModel):
    """SSH key configuration for public key authentication."""
    key_path: str = Field(..., alias="keyPath", description="Path to private SSH key file")
    key_passphrase: Optional[str] = Field(default=None, alias="keyPassphrase", description="Passphrase for encrypted key")

    class Config:
        populate_by_name = True


class DeviceConfig(BaseModel):
    """Configuration for a single MikroTik device."""
    id: str = Field(..., description="Unique device identifier")
    name: str = Field(..., description="Human-readable device name")
    host: str = Field(..., description="IP address or hostname")
    port: int = Field(..., description="Connection port")
    username: str = Field(..., description="RouterOS username")
    password: str = Field(..., description="RouterOS password")
    connection_type: ConnectionType = Field(..., alias="connectionType")
    routeros_version: Literal[6, 7] = Field(..., alias="routerOSVersion")
    timeout: int = Field(default=10000, description="Connection timeout in milliseconds")
    description: Optional[str] = Field(default=None, description="Optional device description")
    ssh_key: Optional[SSHKeyConfig] = Field(default=None, alias="sshKey", description="SSH key configuration")

    @field_validator('username', 'password', mode='before')
    @classmethod
    def expand_env_vars(cls, v: Any) -> Any:
        """Expand environment variables in format ${VAR_NAME} or $VAR_NAME."""
        if isinstance(v, str):
            # Handle ${VAR_NAME} format
            if v.startswith('${') and v.endswith('}'):
                var_name = v[2:-1]
                value = os.getenv(var_name)
                if value is None:
                    raise ValueError(f"Environment variable {var_name} not found")
                return value
            # Handle $VAR_NAME format
            elif v.startswith('$'):
                var_name = v[1:]
                value = os.getenv(var_name)
                if value is None:
                    raise ValueError(f"Environment variable {var_name} not found")
                return value
        return v

    class Config:
        populate_by_name = True
        use_enum_values = True


class DevicesConfig(BaseModel):
    """Configuration for all devices."""
    devices: list[DeviceConfig]


class ConnectionResult(BaseModel):
    """Result of a command execution."""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None


class RouterOSCommand(BaseModel):
    """RouterOS command definition."""
    command: str
    description: str
    supports_ros6: bool
    supports_ros7: bool
    ros7_alternative: Optional[str] = None


class OutputParser:
    """Parse RouterOS text output to structured data."""

    @staticmethod
    def parse_table_output(text: str) -> list[dict]:
        """
        Parse RouterOS table output to list of dicts.

        Args:
            text: Raw RouterOS command output

        Returns:
            List of dictionaries with parsed key-value pairs
        """
        if not text:
            return []

        lines = text.strip().split('\n')
        results = []
        current_item = {}

        for line in lines:
            line = line.strip()

            # Skip empty lines, column headers, and separator lines
            if not line or line.startswith('#') or all(c in '=-' for c in line):
                if current_item:
                    results.append(current_item)
                    current_item = {}
                continue

            # Parse key=value or key="value with spaces"
            matches = re.findall(r'(\w+(?:-\w+)*)=(?:"([^"]*)"|(\S+))', line)
            for key, quoted_val, unquoted_val in matches:
                value = quoted_val if quoted_val else unquoted_val
                current_item[key] = value

        # Add last item if exists
        if current_item:
            results.append(current_item)

        return results
