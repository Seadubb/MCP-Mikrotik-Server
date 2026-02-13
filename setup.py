"""Setup script for mikrotik-mcp-server."""

from setuptools import setup, find_packages

setup(
    name="mikrotik-mcp-server",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "mcp>=1.0.0",
        "paramiko>=3.4.0",
        "telnetlib3>=2.0.0",
        "routeros-api>=0.17.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        "aiosqlite>=0.19.0",
        "pyyaml>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mikrotik-mcp=mikrotik_mcp.server:main",
        ],
    },
)
