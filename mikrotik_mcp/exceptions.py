"""Custom exceptions for MikroTik MCP Server."""


class MikroTikMCPError(Exception):
    """Base exception for all MikroTik MCP errors."""
    pass


class ConnectionError(MikroTikMCPError):
    """Raised when connection to device fails or is lost."""
    pass


class AuthenticationError(MikroTikMCPError):
    """Raised when authentication fails."""
    pass


class CommandError(MikroTikMCPError):
    """Raised when command execution fails."""
    pass


class TimeoutError(MikroTikMCPError):
    """Raised when operation times out."""
    pass


class ConfigurationError(MikroTikMCPError):
    """Raised when configuration is invalid."""
    pass


class DeviceNotFoundError(MikroTikMCPError):
    """Raised when device ID is not found."""
    pass


class NotConnectedError(MikroTikMCPError):
    """Raised when attempting operation on disconnected device."""
    pass


class UnsupportedCommandError(MikroTikMCPError):
    """Raised when command is not supported on RouterOS version."""
    pass


class ParseError(MikroTikMCPError):
    """Raised when parsing command or response fails."""
    pass
