# MikroTik MCP Server - Complete User Manual

**Version 1.0**
**48 MCP Tools for Professional Network Management**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Core Device Management](#core-device-management)
4. [Command Execution](#command-execution)
5. [Device Monitoring](#device-monitoring)
6. [Fleet Management](#fleet-management)
7. [Configuration Management](#configuration-management)
8. [Audit & History](#audit--history)
9. [Firewall Management](#firewall-management)
10. [DHCP Management](#dhcp-management)
11. [VPN Management](#vpn-management)
12. [Configuration Profiles](#configuration-profiles)
13. [Best Practices](#best-practices)
14. [Troubleshooting](#troubleshooting)
15. [Appendix](#appendix)

---

## 1. Introduction

The MikroTik MCP Server is a comprehensive network automation tool that provides 48 MCP tools for managing MikroTik RouterOS devices through Claude Desktop. It supports SSH, Telnet, and API connections, with automatic RouterOS 6/7 compatibility.

### Key Features

- **48 MCP Tools** covering all major operations
- **Multi-Protocol Support**: SSH, Telnet, API
- **RouterOS 6 & 7 Compatible** with automatic command adaptation
- **SQLite Audit Logging** for complete command history
- **Configuration Profiles** for rapid deployment
- **Fleet Management** for multi-device operations
- **Backup/Restore** with configuration comparison

### System Requirements

- Python 3.11, 3.12, or 3.13
- Claude Desktop
- Network access to MikroTik devices
- RouterOS 6.x or 7.x devices

---

## 2. Getting Started

### Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure Devices**:
Edit `devices.json`:
```json
{
  "devices": [
    {
      "id": "office-router",
      "name": "Office Main Router",
      "host": "192.168.1.1",
      "port": 8728,
      "username": "admin",
      "password": "your-password",
      "connection_type": "api",
      "routeros_version": 7
    }
  ]
}
```

3. **Configure Claude Desktop**:
Add to Claude Desktop MCP configuration:
```json
{
  "mcpServers": {
    "mikrotik": {
      "command": "python",
      "args": ["-m", "mikrotik_mcp.server"]
    }
  }
}
```

4. **Restart Claude Desktop**

### Quick Start

```
You: Connect to office-router
Claude: [Uses connect_device tool]
✓ Successfully connected to office-router

You: Show me the interfaces
Claude: [Uses get_interfaces tool]
[Lists all interfaces with details]

You: What's the system status?
Claude: [Uses get_system_info tool]
[Shows uptime, CPU, memory, version]
```

---

## 3. Core Device Management

### 3.1 list_devices

**Purpose**: List all configured MikroTik devices

**Parameters**: None

**Example**:
```
You: Show me all my routers
Claude: [Uses list_devices]

Response:
[
  {
    "id": "office-router",
    "name": "Office Main Router",
    "host": "192.168.1.1",
    "connection_type": "api",
    "routeros_version": 7
  },
  {
    "id": "branch-router",
    "name": "Branch Office Router",
    "host": "192.168.2.1",
    "connection_type": "ssh",
    "routeros_version": 6
  }
]
```

**Use Cases**:
- View all managed devices
- Check device configuration
- Verify connection settings

---

### 3.2 connect_device

**Purpose**: Establish connection to a MikroTik device

**Parameters**:
- `device_id` (required): Device identifier from devices.json

**Example**:
```
You: Connect to office-router
Claude: [Uses connect_device with device_id="office-router"]

Response:
✓ Successfully connected to device: office-router
```

**Connection Types**:
- **API** (Port 8728/8729): Fastest, recommended
- **SSH** (Port 22): Secure, widely supported
- **Telnet** (Port 23): Legacy, not recommended

**Error Handling**:
- Connection timeout: Check network connectivity
- Authentication failure: Verify username/password
- Port closed: Ensure correct port and service enabled

---

### 3.3 disconnect_device

**Purpose**: Close connection to a device

**Parameters**:
- `device_id` (required): Device to disconnect from

**Example**:
```
You: Disconnect from office-router
Claude: [Uses disconnect_device with device_id="office-router"]

Response:
✓ Successfully disconnected from device: office-router
```

**Best Practices**:
- Always disconnect when finished
- Connections auto-disconnect on server shutdown
- Check connection status before operations

---

### 3.4 get_connection_status

**Purpose**: Check connection status of all devices

**Parameters**: None

**Example**:
```
You: Which devices are connected?
Claude: [Uses get_connection_status]

Response:
{
  "office-router": true,
  "branch-router": false,
  "datacenter-router": false
}
```

**Status Indicators**:
- `true`: Connected and ready
- `false`: Not connected

---

### 3.5 get_device_info

**Purpose**: Get detailed information about a specific device

**Parameters**:
- `device_id` (required): Device identifier

**Example**:
```
You: Tell me about office-router
Claude: [Uses get_device_info with device_id="office-router"]

Response:
{
  "id": "office-router",
  "name": "Office Main Router",
  "host": "192.168.1.1",
  "port": 8728,
  "username": "admin",
  "connection_type": "api",
  "routeros_version": 7
}
```

---

## 4. Command Execution

### 4.1 execute_command

**Purpose**: Execute a single RouterOS command

**Parameters**:
- `device_id` (required): Target device
- `command` (required): RouterOS command to execute

**Example 1: View Interfaces**
```
You: Show interfaces on office-router
Claude: [Uses execute_command]
  device_id: "office-router"
  command: "/interface print"

Response:
Flags: D - dynamic, X - disabled, R - running, S - slave
 #     NAME          TYPE       ACTUAL-MTU L2MTU  MAX-L2MTU MAC-ADDRESS
 0 R   ether1        ether            1500  1580      10218 AA:BB:CC:DD:EE:01
 1 R   ether2        ether            1500  1580      10218 AA:BB:CC:DD:EE:02
 2 R   bridge        bridge           1500                  AA:BB:CC:DD:EE:03
```

**Example 2: Add IP Address**
```
You: Add IP 192.168.100.1/24 to ether3 on office-router
Claude: [Uses execute_command]
  device_id: "office-router"
  command: "/ip address add address=192.168.100.1/24 interface=ether3"

Response:
✓ Command executed successfully
```

**Example 3: Change System Identity**
```
You: Rename office-router to "HQ-Router"
Claude: [Uses execute_command]
  device_id: "office-router"
  command: "/system identity set name=HQ-Router"

Response:
✓ Command executed successfully
```

**Common Commands**:
- `/interface print` - List interfaces
- `/ip address print` - List IP addresses
- `/ip route print` - List routes
- `/system resource print` - System status
- `/log print` - View logs
- `/tool ping address=8.8.8.8 count=5` - Ping test

**Command Adaptation**:
The server automatically adapts commands for RouterOS version:
- RouterOS 6: Uses `/interface bridge port`
- RouterOS 7: Uses `/interface/bridge/port`

---

### 4.2 execute_batch_commands

**Purpose**: Execute multiple commands in sequence

**Parameters**:
- `device_id` (required): Target device
- `commands` (required): Array of commands
- `stop_on_error` (optional): Stop if a command fails (default: false)

**Example: Configure New Interface**
```
You: Configure ether4 with IP and description on office-router
Claude: [Uses execute_batch_commands]
  device_id: "office-router"
  commands: [
    "/interface set ether4 comment=\"Guest Network\"",
    "/ip address add address=192.168.99.1/24 interface=ether4",
    "/ip pool add name=guest-pool ranges=192.168.99.100-192.168.99.200"
  ]
  stop_on_error: true

Response:
[
  {
    "command_number": 1,
    "command": "/interface set ether4 comment=\"Guest Network\"",
    "success": true,
    "output": ""
  },
  {
    "command_number": 2,
    "command": "/ip address add address=192.168.99.1/24 interface=ether4",
    "success": true,
    "output": ""
  },
  {
    "command_number": 3,
    "command": "/ip pool add name=guest-pool ranges=192.168.99.100-192.168.99.200",
    "success": true,
    "output": ""
  }
]
```

**Use Cases**:
- Multi-step configuration
- Bulk operations
- Scripted deployments
- Configuration rollouts

---

### 4.3 execute_on_all_devices

**Purpose**: Execute the same command on all connected devices

**Parameters**:
- `command` (required): Command to execute everywhere

**Example: Update NTP Servers**
```
You: Set NTP servers to 0.pool.ntp.org on all routers
Claude: [Uses execute_on_all_devices]
  command: "/system ntp client set enabled=yes servers=0.pool.ntp.org"

Response:
{
  "office-router": {
    "success": true,
    "output": ""
  },
  "branch-router": {
    "success": true,
    "output": ""
  },
  "datacenter-router": {
    "success": false,
    "error": "Not connected"
  }
}
```

**Best Practices**:
- Test command on one device first
- Connect to all target devices beforehand
- Use for consistent configuration across fleet
- Review results for each device

---

## 5. Device Monitoring

### 5.1 get_system_info

**Purpose**: Get system resource information

**Parameters**:
- `device_id` (required): Device to query

**Example**:
```
You: What's the system status of office-router?
Claude: [Uses get_system_info with device_id="office-router"]

Response:
            uptime: 2w3d5h23m45s
           version: 7.10.2 (stable)
        build-time: Jun/20/2023 12:34:56
              arch: arm64
         board-name: CCR1009
               cpu: ARMv8
         cpu-count: 9
     cpu-frequency: 1200MHz
            cpu-load: 5%
      free-memory: 15.2GiB
     total-memory: 16.0GiB
 free-hdd-space: 89.5GiB
total-hdd-space: 128.0GiB
```

**Monitoring Tips**:
- Check CPU load (high sustained load indicates issues)
- Monitor free memory (low memory affects performance)
- Track uptime for stability assessment
- Review version for security updates

---

### 5.2 get_interfaces

**Purpose**: List all network interfaces

**Parameters**:
- `device_id` (required): Device to query

**Example**:
```
You: Show all interfaces on office-router
Claude: [Uses get_interfaces with device_id="office-router"]

Response:
 #     NAME          TYPE       MTU    MAC-ADDRESS         STATUS
 0 R   ether1        ether     1500   AA:BB:CC:DD:EE:01   Running
 1 R   ether2        ether     1500   AA:BB:CC:DD:EE:02   Running
 2 R   ether3        ether     1500   AA:BB:CC:DD:EE:03   Disabled
 3 R   bridge        bridge    1500   AA:BB:CC:DD:EE:04   Running
 4 D   pppoe-out1    pppoe     1480   AA:BB:CC:DD:EE:05   Running
 5 R   wlan1         wlan      1500   AA:BB:CC:DD:EE:06   Running
```

**Interface Types**:
- **ether**: Ethernet physical interface
- **bridge**: Bridge interface
- **vlan**: VLAN interface
- **pppoe**: PPPoE client
- **wlan**: Wireless interface
- **bonding**: Link aggregation

**Status Flags**:
- **R**: Running
- **D**: Dynamic
- **X**: Disabled
- **S**: Slave (part of bridge/bonding)

---

### 5.3 get_ip_addresses

**Purpose**: List all configured IP addresses

**Parameters**:
- `device_id` (required): Device to query

**Example**:
```
You: Show IP addresses on office-router
Claude: [Uses get_ip_addresses with device_id="office-router"]

Response:
 #   ADDRESS            NETWORK          INTERFACE        STATUS
 0   192.168.1.1/24     192.168.1.0      ether1          Active
 1   10.0.0.1/24        10.0.0.0         ether2          Active
 2 D 100.64.1.45/32     100.64.1.45      pppoe-out1      Dynamic
 3   192.168.88.1/24    192.168.88.0     bridge          Active
```

**IP Address Types**:
- **Static**: Manually configured
- **Dynamic**: Assigned by DHCP/PPPoE

---

### 5.4 get_firewall_rules

**Purpose**: List firewall filter rules

**Parameters**:
- `device_id` (required): Device to query

**Example**:
```
You: Show firewall rules on office-router
Claude: [Uses get_firewall_rules with device_id="office-router"]

Response:
 #    CHAIN              ACTION      PROTOCOL  SRC-ADDRESS    DST-PORT
 0    input              accept      tcp                      22
 1    input              accept      tcp                      8291
 2    input              accept      icmp
 3    input              drop
 4    forward            accept      all       192.168.0.0/16
 5    forward            drop        all
```

**Common Chains**:
- **input**: Traffic to the router itself
- **forward**: Traffic passing through router
- **output**: Traffic from the router

---

### 5.5 get_dhcp_leases

**Purpose**: List DHCP leases

**Parameters**:
- `device_id` (required): Device to query

**Example**:
```
You: Show DHCP leases on office-router
Claude: [Uses get_dhcp_leases with device_id="office-router"]

Response:
 #   ADDRESS          MAC-ADDRESS        HOST-NAME       STATUS    SERVER
 0   192.168.1.100    AA:BB:CC:DD:EE:10  Desktop-1       bound     dhcp1
 1   192.168.1.101    AA:BB:CC:DD:EE:11  Laptop-2        bound     dhcp1
 2   192.168.1.102    AA:BB:CC:DD:EE:12  Phone-3         bound     dhcp1
 3   192.168.1.150    AA:BB:CC:DD:EE:13  Printer-Main    static    dhcp1
```

**Lease Status**:
- **bound**: Active lease
- **offered**: Offered but not confirmed
- **waiting**: Waiting for confirmation
- **static**: Static reservation

---

### 5.6 get_routes

**Purpose**: List IP routes

**Parameters**:
- `device_id` (required): Device to query

**Example**:
```
You: Show routing table on office-router
Claude: [Uses get_routes with device_id="office-router"]

Response:
 #   DST-ADDRESS         GATEWAY          DISTANCE  INTERFACE
 0 S 0.0.0.0/0           192.168.1.254    1         ether1
 1 C 192.168.1.0/24      192.168.1.1      0         ether1
 2 C 10.0.0.0/24         10.0.0.1         0         ether2
 3 S 172.16.0.0/12       10.0.0.254       1         ether2
```

**Route Types**:
- **S**: Static route
- **C**: Connected route
- **D**: Dynamic (DHCP, PPPoE)
- **A**: Active route

---

## 6. Fleet Management

### 6.1 get_connection_stats

**Purpose**: Get detailed connection statistics for a device

**Parameters**:
- `device_id` (required): Device identifier

**Example**:
```
You: Show connection statistics for office-router
Claude: [Uses get_connection_stats with device_id="office-router"]

Response:
{
  "connected": true,
  "connection_type": "api",
  "connected_at": "2026-01-18T15:30:00",
  "uptime_seconds": 3600,
  "commands_executed": 147,
  "successful_commands": 145,
  "failed_commands": 2,
  "average_response_time_ms": 45.3,
  "last_command_at": "2026-01-18T16:29:45"
}
```

**Statistics Explained**:
- **uptime_seconds**: How long connected
- **commands_executed**: Total commands sent
- **average_response_time_ms**: Performance metric
- **failed_commands**: Error count

**Use Cases**:
- Monitor connection health
- Track device usage
- Identify slow devices
- Troubleshoot connectivity

---

### 6.2 get_fleet_status

**Purpose**: Get status and statistics for all configured devices

**Parameters**: None

**Example**:
```
You: Show status of all routers
Claude: [Uses get_fleet_status]

Response:
[
  {
    "device_id": "office-router",
    "name": "Office Main Router",
    "host": "192.168.1.1",
    "connection_type": "api",
    "connected": true,
    "uptime_seconds": 3600,
    "commands_executed": 147
  },
  {
    "device_id": "branch-router",
    "name": "Branch Office Router",
    "host": "192.168.2.1",
    "connection_type": "ssh",
    "connected": false
  },
  {
    "device_id": "datacenter-router",
    "name": "Datacenter Router",
    "host": "10.0.0.1",
    "connection_type": "api",
    "connected": true,
    "uptime_seconds": 7200,
    "commands_executed": 89
  }
]
```

**Dashboard View**:
Use this for a quick overview of your entire infrastructure:
- Which devices are online
- Connection health
- Usage patterns
- Device locations

---

## 7. Configuration Management

### 7.1 backup_config

**Purpose**: Export and save device configuration to a backup file

**Parameters**:
- `device_id` (required): Device to backup
- `backup_path` (optional): Custom backup file path

**Example 1: Automatic Backup**
```
You: Backup configuration of office-router
Claude: [Uses backup_config with device_id="office-router"]

Response:
✓ Configuration backed up successfully to: backups/office-router_20260118_153045.rsc
```

**Example 2: Custom Path**
```
You: Backup office-router to my-backup.rsc
Claude: [Uses backup_config]
  device_id: "office-router"
  backup_path: "my-backup.rsc"

Response:
✓ Configuration backed up successfully to: my-backup.rsc
```

**Backup Format**:
- `.rsc` file (RouterOS Script)
- Plain text, editable
- Contains complete configuration
- Can be imported to any RouterOS device

**Backup Best Practices**:
- Backup before major changes
- Regular scheduled backups
- Version control for backups
- Test restore procedures
- Store off-device securely

---

### 7.2 export_config

**Purpose**: Export device configuration as text without saving to file

**Parameters**:
- `device_id` (required): Device to export from

**Example**:
```
You: Show me the configuration of office-router
Claude: [Uses export_config with device_id="office-router"]

Response:
# jan/18/2026 15:35:12 by RouterOS 7.10.2
# software id = XXXX-XXXX
#
/interface bridge
add name=bridge
/interface vlan
add interface=bridge name=vlan10 vlan-id=10
add interface=bridge name=vlan20 vlan-id=20
/ip address
add address=192.168.1.1/24 interface=ether1
add address=10.0.0.1/24 interface=ether2
/ip dhcp-server
add address-pool=pool1 interface=bridge name=dhcp1
...
```

**Use Cases**:
- Quick configuration review
- Copy-paste configuration snippets
- Documentation
- Configuration audits

---

### 7.3 restore_config

**Purpose**: Restore device configuration from a backup file

**Parameters**:
- `device_id` (required): Device to restore to
- `backup_path` (required): Path to backup .rsc file

**Example**:
```
You: Restore office-router from backups/office-router_20260118_153045.rsc
Claude: [Uses restore_config]
  device_id: "office-router"
  backup_path: "backups/office-router_20260118_153045.rsc"

Response:
Restored 247/250 commands successfully, 3 failed

Errors:
Line 45: failure: device or resource busy
Line 120: already have such address
Line 203: no such item
```

**Important Notes**:
- ⚠️ **WARNING**: Restore can overwrite current configuration
- Backup current config before restore
- Review backup file before applying
- Some commands may fail (already exists, etc.)
- Test on non-production device first

**Restore Process**:
1. Reads backup file
2. Executes commands line-by-line
3. Skips comments and empty lines
4. Reports success/failure for each command
5. Continues even if some commands fail

---

### 7.4 compare_configs

**Purpose**: Compare configurations between two devices and show differences

**Parameters**:
- `device1_id` (required): First device ID
- `device2_id` (required): Second device ID

**Example**:
```
You: Compare configuration between office-router and branch-router
Claude: [Uses compare_configs]
  device1_id: "office-router"
  device2_id: "branch-router"

Response:
{
  "device1_id": "office-router",
  "device2_id": "branch-router",
  "identical": false,
  "similarity_percent": 73.45,
  "diff_lines": 54,
  "config1_lines": 250,
  "config2_lines": 248,
  "diff": "
--- office-router config
+++ branch-router config
@@ -12,7 +12,7 @@
 /interface bridge
 add name=bridge
-/ip address
-add address=192.168.1.1/24 interface=ether1
+add address=192.168.2.1/24 interface=ether1
@@ -45,3 +45,5 @@
 /system identity
-set name=office-router
+set name=branch-router
+/system ntp client
+set enabled=yes servers=0.pool.ntp.org
  "
}
```

**Use Cases**:
- Verify consistency across sites
- Identify configuration drift
- Audit device configurations
- Template validation
- Troubleshoot differences

**Interpreting Results**:
- **similarity_percent**: Higher = more similar
- Lines starting with `-`: Only in device1
- Lines starting with `+`: Only in device2
- **identical**: true if configs are exactly the same

---

## 8. Audit & History

### 8.1 get_command_history

**Purpose**: Get command execution history from audit log

**Parameters**:
- `device_id` (optional): Filter by device ID
- `limit` (optional): Max records to return (default: 50)
- `failed_only` (optional): Show only failed commands (default: false)

**Example 1: Recent Commands on Device**
```
You: Show last 10 commands executed on office-router
Claude: [Uses get_command_history]
  device_id: "office-router"
  limit: 10

Response:
[
  {
    "id": 147,
    "timestamp": "2026-01-18 16:29:45",
    "device_id": "office-router",
    "device_name": "Office Main Router",
    "command": "/interface print",
    "success": true,
    "execution_time_ms": 42.3
  },
  {
    "id": 146,
    "timestamp": "2026-01-18 16:28:12",
    "device_id": "office-router",
    "command": "/ip address add address=192.168.100.1/24 interface=ether3",
    "success": true,
    "execution_time_ms": 156.7
  },
  ...
]
```

**Example 2: Failed Commands Only**
```
You: Show failed commands on all devices
Claude: [Uses get_command_history]
  failed_only: true
  limit: 20

Response:
[
  {
    "id": 145,
    "timestamp": "2026-01-18 16:15:33",
    "device_id": "branch-router",
    "command": "/ip address add address=192.168.1.1/24 interface=ether5",
    "success": false,
    "error": "no such interface"
  },
  {
    "id": 132,
    "timestamp": "2026-01-18 15:45:22",
    "device_id": "office-router",
    "command": "/interface bridge port add interface=ether10 bridge=bridge",
    "success": false,
    "error": "no such interface"
  }
]
```

**Audit Use Cases**:
- Troubleshooting recent changes
- Compliance auditing
- Security review
- Performance analysis
- Error investigation

---

### 8.2 get_device_audit_stats

**Purpose**: Get audit statistics for a specific device

**Parameters**:
- `device_id` (required): Device ID to get statistics for

**Example**:
```
You: Show audit statistics for office-router
Claude: [Uses get_device_audit_stats with device_id="office-router"]

Response:
{
  "device_id": "office-router",
  "total_commands": 247,
  "successful_commands": 245,
  "failed_commands": 2,
  "success_rate": 99.19,
  "first_command_at": "2026-01-15 09:15:00",
  "last_command_at": "2026-01-18 16:29:45",
  "average_execution_time_ms": 67.4,
  "most_used_commands": [
    {
      "command": "/interface print",
      "count": 45
    },
    {
      "command": "/ip address print",
      "count": 32
    },
    {
      "command": "/system resource print",
      "count": 28
    }
  ]
}
```

**Statistics Analysis**:
- **success_rate**: Overall command success
- **average_execution_time_ms**: Performance indicator
- **most_used_commands**: Usage patterns
- Low success rate may indicate issues

---

## 9. Firewall Management

### 9.1 firewall_add_filter_rule

**Purpose**: Add a firewall filter rule

**Parameters**:
- `device_id` (required): Device to configure
- `chain` (required): Chain (input, forward, output)
- `action` (required): Action (accept, drop, reject, etc.)
- `protocol` (optional): Protocol (tcp, udp, icmp, etc.)
- `src_address` (optional): Source IP address/network
- `dst_address` (optional): Destination IP address/network
- `src_port` (optional): Source port(s)
- `dst_port` (optional): Destination port(s)
- `in_interface` (optional): Input interface
- `out_interface` (optional): Output interface
- `comment` (optional): Rule comment
- `disabled` (optional): Disable rule (default: false)

**Example 1: Allow SSH**
```
You: Allow SSH access on office-router
Claude: [Uses firewall_add_filter_rule]
  device_id: "office-router"
  chain: "input"
  action: "accept"
  protocol: "tcp"
  dst_port: "22"
  comment: "Allow SSH"

Response:
✓ Firewall rule added successfully
```

**Example 2: Block Specific IP**
```
You: Block traffic from 1.2.3.4 on office-router
Claude: [Uses firewall_add_filter_rule]
  device_id: "office-router"
  chain: "input"
  action: "drop"
  src_address: "1.2.3.4"
  comment: "Block malicious IP"

Response:
✓ Firewall rule added successfully
```

**Example 3: Allow Inter-VLAN**
```
You: Allow traffic from VLAN 10 to VLAN 20
Claude: [Uses firewall_add_filter_rule]
  device_id: "office-router"
  chain: "forward"
  action: "accept"
  src_address: "192.168.10.0/24"
  dst_address: "192.168.20.0/24"
  comment: "Allow Management to Users VLAN"

Response:
✓ Firewall rule added successfully
```

**Firewall Chains**:
- **input**: Traffic destined for router
- **forward**: Traffic passing through router
- **output**: Traffic originating from router

**Common Actions**:
- **accept**: Allow traffic
- **drop**: Silently discard
- **reject**: Discard and send rejection
- **tarpit**: Slow down attacker
- **log**: Log and continue

---

### 9.2 firewall_add_nat_rule

**Purpose**: Add a NAT rule

**Parameters**:
- `device_id` (required): Device to configure
- `chain` (required): Chain (srcnat, dstnat)
- `action` (required): Action (masquerade, dst-nat, src-nat)
- `protocol` (optional): Protocol
- `src_address` (optional): Source address
- `dst_address` (optional): Destination address
- `dst_port` (optional): Destination port
- `to_addresses` (optional): NAT target address
- `to_ports` (optional): NAT target port
- `out_interface` (optional): Output interface
- `comment` (optional): Rule comment

**Example 1: Masquerade (Internet Sharing)**
```
You: Setup NAT for internet sharing on office-router
Claude: [Uses firewall_add_nat_rule]
  device_id: "office-router"
  chain: "srcnat"
  action: "masquerade"
  out_interface: "ether1"
  comment: "Internet sharing NAT"

Response:
✓ NAT rule added successfully
```

**Example 2: Port Forwarding**
```
You: Forward port 80 to internal server 192.168.1.100 on office-router
Claude: [Uses firewall_add_nat_rule]
  device_id: "office-router"
  chain: "dstnat"
  action: "dst-nat"
  protocol: "tcp"
  dst_port: "80"
  to_addresses: "192.168.1.100"
  to_ports: "80"
  comment: "Web server port forward"

Response:
✓ NAT rule added successfully
```

**Example 3: 1-to-1 NAT**
```
You: Setup 1-to-1 NAT for 192.168.1.50 to 203.0.113.5
Claude: [Uses firewall_add_nat_rule]
  device_id: "office-router"
  chain: "srcnat"
  action: "src-nat"
  src_address: "192.168.1.50"
  to_addresses: "203.0.113.5"
  comment: "1-to-1 NAT for mail server"

Response:
✓ NAT rule added successfully
```

**NAT Chains**:
- **srcnat**: Source NAT (outbound)
- **dstnat**: Destination NAT (inbound, port forwarding)

**NAT Actions**:
- **masquerade**: Dynamic source NAT (for dynamic WAN IP)
- **src-nat**: Static source NAT
- **dst-nat**: Destination NAT (port forwarding)

---

### 9.3 firewall_add_address_list

**Purpose**: Add an address to a firewall address list

**Parameters**:
- `device_id` (required): Device to configure
- `list_name` (required): Address list name
- `address` (required): IP address or network
- `comment` (optional): Comment
- `timeout` (optional): Timeout (e.g., 1d, 2h)

**Example 1: Blacklist IP**
```
You: Add 1.2.3.4 to blacklist on office-router
Claude: [Uses firewall_add_address_list]
  device_id: "office-router"
  list_name: "blacklist"
  address: "1.2.3.4"
  comment: "Brute force attempt"

Response:
✓ Address added to list successfully
```

**Example 2: Whitelist Network**
```
You: Add trusted network 10.0.0.0/24 to whitelist
Claude: [Uses firewall_add_address_list]
  device_id: "office-router"
  list_name: "whitelist"
  address: "10.0.0.0/24"
  comment: "Corporate network"

Response:
✓ Address added to list successfully
```

**Example 3: Temporary Block**
```
You: Block 5.6.7.8 for 1 day
Claude: [Uses firewall_add_address_list]
  device_id: "office-router"
  list_name: "temp-block"
  address: "5.6.7.8"
  timeout: "1d"
  comment: "Temporary block"

Response:
✓ Address added to list successfully
```

**Address List Use Cases**:
- Blacklists (block malicious IPs)
- Whitelists (allow trusted IPs)
- Country blocking (GeoIP lists)
- VPN users
- Dynamic blocking (failed login attempts)

**Timeout Format**:
- `1h` = 1 hour
- `30m` = 30 minutes
- `1d` = 1 day
- `1w` = 1 week

---

### 9.4 firewall_get_address_list

**Purpose**: Get firewall address list entries

**Parameters**:
- `device_id` (required): Device to query
- `list_name` (optional): Filter by list name

**Example**:
```
You: Show blacklist on office-router
Claude: [Uses firewall_get_address_list]
  device_id: "office-router"
  list_name: "blacklist"

Response:
 #   LIST        ADDRESS          TIMEOUT    COMMENT
 0   blacklist   1.2.3.4          1d23h45m   Brute force
 1   blacklist   5.6.7.8                     Port scanner
 2   blacklist   9.10.11.0/24                Spam network
```

---

### 9.5 firewall_remove_rule

**Purpose**: Remove a firewall filter, NAT, or mangle rule by ID

**Parameters**:
- `device_id` (required): Device to configure
- `rule_type` (required): Rule type (filter, nat, mangle)
- `rule_id` (required): Rule ID or number

**Example**:
```
You: Remove firewall filter rule #5 from office-router
Claude: [Uses firewall_remove_rule]
  device_id: "office-router"
  rule_type: "filter"
  rule_id: "5"

Response:
✓ Firewall rule removed successfully
```

**Finding Rule IDs**:
1. List rules: `get_firewall_rules`
2. Find the `#` number in the output
3. Use that number with `firewall_remove_rule`

---

## 10. DHCP Management

### 10.1 dhcp_create_server

**Purpose**: Create a DHCP server

**Parameters**:
- `device_id` (required): Device to configure
- `name` (required): DHCP server name
- `interface` (required): Interface to run DHCP on
- `address_pool` (required): Address pool name
- `lease_time` (optional): Lease time (default: 1d)

**Example**:
```
You: Create DHCP server on VLAN 20 interface
Claude: [Uses dhcp_create_server]
  device_id: "office-router"
  name: "dhcp-vlan20"
  interface: "vlan20"
  address_pool: "pool-vlan20"
  lease_time: "8h"

Response:
✓ DHCP server created successfully
```

**Note**: You must create the address pool first using `dhcp_create_pool`

---

### 10.2 dhcp_add_network

**Purpose**: Add a DHCP network configuration

**Parameters**:
- `device_id` (required): Device to configure
- `address` (required): Network address (e.g., 192.168.1.0/24)
- `gateway` (optional): Gateway IP
- `dns_server` (optional): DNS server(s)
- `domain` (optional): Domain name
- `comment` (optional): Comment

**Example**:
```
You: Configure DHCP network for 192.168.20.0/24
Claude: [Uses dhcp_add_network]
  device_id: "office-router"
  address: "192.168.20.0/24"
  gateway: "192.168.20.1"
  dns_server: "8.8.8.8,8.8.4.4"
  domain: "office.local"
  comment: "Users VLAN network"

Response:
✓ DHCP network added successfully
```

**DHCP Network Configuration**:
Clients will receive:
- IP address from pool
- Gateway (default route)
- DNS servers
- Domain name for DNS suffix

---

### 10.3 dhcp_add_static_lease

**Purpose**: Add a static DHCP lease (IP reservation)

**Parameters**:
- `device_id` (required): Device to configure
- `address` (required): IP address to assign
- `mac_address` (required): Client MAC address
- `server` (optional): DHCP server name
- `comment` (optional): Comment

**Example**:
```
You: Reserve IP 192.168.1.50 for printer with MAC AA:BB:CC:DD:EE:10
Claude: [Uses dhcp_add_static_lease]
  device_id: "office-router"
  address: "192.168.1.50"
  mac_address: "AA:BB:CC:DD:EE:10"
  comment: "Office Printer"

Response:
✓ Static DHCP lease added successfully
```

**Use Cases**:
- Printers (need consistent IP)
- Servers (internal services)
- Network devices (cameras, access points)
- VoIP phones

---

### 10.4 dhcp_create_pool

**Purpose**: Create an IP address pool

**Parameters**:
- `device_id` (required): Device to configure
- `name` (required): Pool name
- `ranges` (required): IP ranges (e.g., 192.168.1.100-192.168.1.200)
- `comment` (optional): Comment

**Example**:
```
You: Create DHCP pool for VLAN 20
Claude: [Uses dhcp_create_pool]
  device_id: "office-router"
  name: "pool-vlan20"
  ranges: "192.168.20.100-192.168.20.200"
  comment: "VLAN 20 address pool"

Response:
✓ Address pool created successfully
```

**Multiple Ranges**:
You can specify multiple ranges separated by commas:
```
ranges: "192.168.1.100-192.168.1.150,192.168.1.160-192.168.1.200"
```

---

### 10.5 dhcp_get_servers

**Purpose**: Get list of DHCP servers

**Parameters**:
- `device_id` (required): Device to query

**Example**:
```
You: Show DHCP servers on office-router
Claude: [Uses dhcp_get_servers with device_id="office-router"]

Response:
 #   NAME          INTERFACE   ADDRESS-POOL    LEASE-TIME  STATUS
 0   dhcp-vlan10   vlan10      pool-vlan10     1d          Running
 1   dhcp-vlan20   vlan20      pool-vlan20     8h          Running
 2   dhcp-guest    vlan99      pool-guest      2h          Disabled
```

---

## 11. VPN Management

### 11.1 vpn_add_ipsec_peer

**Purpose**: Add an IPsec peer

**Parameters**:
- `device_id` (required): Device to configure
- `name` (required): Peer name
- `address` (required): Peer IP address
- `secret` (optional): Pre-shared key
- `exchange_mode` (optional): Exchange mode (main, aggressive)
- `comment` (optional): Comment

**Example**:
```
You: Add IPsec peer for branch office
Claude: [Uses vpn_add_ipsec_peer]
  device_id: "office-router"
  name: "branch-office-vpn"
  address: "203.0.113.50"
  secret: "MySecurePreSharedKey123"
  exchange_mode: "main"
  comment: "Branch office site-to-site VPN"

Response:
✓ IPsec peer added successfully
```

**IPsec Use Cases**:
- Site-to-site VPN
- Remote office connectivity
- Secure network interconnection

---

### 11.2 vpn_get_ipsec_peers

**Purpose**: Get IPsec peers

**Parameters**:
- `device_id` (required): Device to query

**Example**:
```
You: Show IPsec peers on office-router
Claude: [Uses vpn_get_ipsec_peers with device_id="office-router"]

Response:
 #   NAME              ADDRESS         SECRET  EXCHANGE-MODE  STATUS
 0   branch-vpn        203.0.113.50    ***     main          Connected
 1   datacenter-vpn    203.0.113.100   ***     main          Disconnected
```

---

### 11.3 vpn_add_l2tp_user

**Purpose**: Add an L2TP VPN user

**Parameters**:
- `device_id` (required): Device to configure
- `name` (required): Username
- `password` (required): Password
- `local_address` (optional): Local (server) IP
- `remote_address` (optional): Remote (client) IP
- `comment` (optional): Comment

**Example**:
```
You: Add L2TP user john.doe with password SecurePass123
Claude: [Uses vpn_add_l2tp_user]
  device_id: "office-router"
  name: "john.doe"
  password: "SecurePass123"
  remote_address: "10.10.10.10"
  comment: "John Doe - Sales"

Response:
✓ L2TP user added successfully
```

**VPN User Management**:
- Each user gets unique credentials
- Optional: assign specific IP address
- Set expiration dates in comment field

---

### 11.4 vpn_configure_l2tp_server

**Purpose**: Configure L2TP server settings

**Parameters**:
- `device_id` (required): Device to configure
- `enabled` (optional): Enable server (default: true)
- `use_ipsec` (optional): Use IPsec (default: true)
- `ipsec_secret` (optional): IPsec pre-shared key

**Example**:
```
You: Enable L2TP VPN server with IPsec
Claude: [Uses vpn_configure_l2tp_server]
  device_id: "office-router"
  enabled: true
  use_ipsec: true
  ipsec_secret: "MyVPNSecret123"

Response:
✓ L2TP server configured successfully
```

**L2TP/IPsec**:
- **L2TP**: Layer 2 Tunneling Protocol
- **IPsec**: Encryption layer
- Combined: Secure VPN solution
- Compatible with most clients (Windows, Mac, iOS, Android)

---

### 11.5 vpn_get_l2tp_connections

**Purpose**: Get active L2TP connections

**Parameters**:
- `device_id` (required): Device to query

**Example**:
```
You: Show active VPN connections on office-router
Claude: [Uses vpn_get_l2tp_connections with device_id="office-router"]

Response:
 #   USER          CLIENT-IP       UPTIME      ENCODING
 0   john.doe      10.10.10.10     2h34m       mppe128
 1   jane.smith    10.10.10.11     45m         mppe128
```

**Connection Details**:
- **USER**: Authenticated username
- **CLIENT-IP**: Assigned VPN IP
- **UPTIME**: Connection duration
- **ENCODING**: Encryption type

---

### 11.6 vpn_add_wireguard_interface

**Purpose**: Add a WireGuard interface

**Parameters**:
- `device_id` (required): Device to configure
- `name` (required): Interface name
- `listen_port` (required): UDP listen port
- `private_key` (optional): Private key (auto-generated if not provided)
- `comment` (optional): Comment

**Example**:
```
You: Create WireGuard interface on port 51820
Claude: [Uses vpn_add_wireguard_interface]
  device_id: "office-router"
  name: "wireguard1"
  listen_port: 51820
  comment: "WireGuard VPN"

Response:
✓ WireGuard interface created successfully
Private key: [auto-generated key displayed]
```

**WireGuard Advantages**:
- Modern VPN protocol
- Very fast performance
- Simple configuration
- Strong cryptography
- Lower overhead than IPsec

---

### 11.7 vpn_add_wireguard_peer

**Purpose**: Add a WireGuard peer

**Parameters**:
- `device_id` (required): Device to configure
- `interface` (required): WireGuard interface name
- `public_key` (required): Peer's public key
- `allowed_address` (required): Allowed IP addresses
- `endpoint_address` (optional): Peer endpoint IP
- `endpoint_port` (optional): Peer endpoint port
- `comment` (optional): Comment

**Example**:
```
You: Add WireGuard peer for remote user
Claude: [Uses vpn_add_wireguard_peer]
  device_id: "office-router"
  interface: "wireguard1"
  public_key: "base64EncodedPublicKey=="
  allowed_address: "10.0.0.2/32"
  endpoint_address: "203.0.113.100"
  endpoint_port: 51820
  comment: "Remote User - Alice"

Response:
✓ WireGuard peer added successfully
```

---

### 11.8 vpn_get_wireguard_interfaces

**Purpose**: Get WireGuard interfaces

**Parameters**:
- `device_id` (required): Device to query

**Example**:
```
You: Show WireGuard interfaces on office-router
Claude: [Uses vpn_get_wireguard_interfaces with device_id="office-router"]

Response:
 #   NAME         LISTEN-PORT  PRIVATE-KEY   PUBLIC-KEY   MTU
 0   wireguard1   51820        ***           base64key==  1420
```

---

### 11.9 vpn_get_ppp_secrets

**Purpose**: Get PPP secrets (L2TP/PPTP users)

**Parameters**:
- `device_id` (required): Device to query
- `service` (optional): Filter by service (l2tp, pptp)

**Example**:
```
You: Show all VPN users on office-router
Claude: [Uses vpn_get_ppp_secrets with device_id="office-router"]

Response:
 #   NAME         SERVICE  LOCAL-ADDRESS  REMOTE-ADDRESS  PROFILE
 0   john.doe     l2tp     10.10.10.1     10.10.10.10     vpn-profile
 1   jane.smith   l2tp     10.10.10.1     10.10.10.11     vpn-profile
 2   bob.jones    pptp     10.10.10.1     10.10.10.20     vpn-profile
```

---

## 12. Configuration Profiles

### 12.1 profile_list

**Purpose**: List available configuration profiles

**Parameters**:
- `category` (optional): Filter by category (network, security, vpn, wireless)

**Example 1: All Profiles**
```
You: Show all configuration profiles
Claude: [Uses profile_list]

Response:
[
  {
    "id": "corporate-office",
    "category": "network",
    "name": "Corporate Office Router",
    "description": "Standard office router with VLANs, firewall, and DHCP",
    "variables": ["WAN_INTERFACE", "LAN_BRIDGE"]
  },
  {
    "id": "high-security",
    "category": "security",
    "name": "High Security Baseline",
    "description": "Comprehensive security hardening profile",
    "variables": []
  },
  {
    "id": "remote-access-l2tp",
    "category": "vpn",
    "name": "L2TP VPN for Remote Access",
    "description": "L2TP/IPsec VPN server configuration",
    "variables": ["IPSEC_SECRET", "DNS_SERVER"]
  },
  {
    "id": "guest-wifi",
    "category": "wireless",
    "name": "Guest WiFi Network",
    "description": "Isolated guest WiFi with bandwidth limits",
    "variables": ["WIFI_PASSWORD", "GUEST_SUBNET", "WAN_INTERFACE"]
  }
]
```

**Example 2: Security Profiles Only**
```
You: Show security profiles
Claude: [Uses profile_list with category="security"]

Response:
[
  {
    "id": "high-security",
    "category": "security",
    "name": "High Security Baseline",
    "description": "Comprehensive security hardening profile",
    "variables": []
  }
]
```

---

### 12.2 profile_get

**Purpose**: Get details of a specific profile

**Parameters**:
- `profile_id` (required): Profile identifier
- `category` (optional): Profile category

**Example**:
```
You: Show details of corporate-office profile
Claude: [Uses profile_get with profile_id="corporate-office"]

Response:
{
  "profile": {
    "name": "Corporate Office Router",
    "description": "Standard office router with VLANs, firewall, and DHCP",
    "variables": ["WAN_INTERFACE", "LAN_BRIDGE"],
    "interfaces": {
      "wan": "${WAN_INTERFACE}",
      "lan_bridge": "${LAN_BRIDGE}",
      "vlans": [
        { "id": 10, "name": "Management", "subnet": "192.168.10.0/24" },
        { "id": 20, "name": "Users", "subnet": "192.168.20.0/24" },
        { "id": 30, "name": "Guest", "subnet": "192.168.30.0/24" }
      ]
    },
    "firewall": {
      "default_policy": "drop",
      "rules": [...]
    },
    "dhcp_servers": [...]
  }
}
```

---

### 12.3 profile_preview

**Purpose**: Preview commands that will be executed for a profile

**Parameters**:
- `profile_id` (required): Profile identifier
- `variables` (optional): Variable substitutions (key-value pairs)
- `category` (optional): Profile category

**Example**:
```
You: Preview corporate-office profile with my settings
Claude: [Uses profile_preview]
  profile_id: "corporate-office"
  variables: {
    "WAN_INTERFACE": "ether1",
    "LAN_BRIDGE": "bridge"
  }

Response:
{
  "commands": [
    "/interface vlan add name=Management vlan-id=10 interface=bridge",
    "/interface vlan add name=Users vlan-id=20 interface=bridge",
    "/interface vlan add name=Guest vlan-id=30 interface=bridge",
    "/ip address add address=192.168.10.1/24 interface=Management",
    "/ip address add address=192.168.20.1/24 interface=Users",
    "/ip address add address=192.168.30.1/24 interface=Guest",
    "/ip firewall filter add chain=forward action=accept connection-state=established,related",
    "/ip firewall filter add chain=forward action=drop connection-state=invalid",
    "/ip firewall nat add chain=srcnat action=masquerade out-interface=ether1",
    "/ip pool add name=pool-vlan10 ranges=192.168.10.100-192.168.10.200",
    "/ip pool add name=pool-vlan20 ranges=192.168.20.100-192.168.20.250",
    "/ip pool add name=pool-vlan30 ranges=192.168.30.10-192.168.30.50",
    "/ip dhcp-server add name=dhcp-vlan10 interface=Management address-pool=pool-vlan10",
    "/ip dhcp-server add name=dhcp-vlan20 interface=Users address-pool=pool-vlan20",
    "/ip dhcp-server add name=dhcp-vlan30 interface=Guest address-pool=pool-vlan30"
  ],
  "count": 15
}
```

**Safety First**:
Always preview before applying to:
- Review generated commands
- Verify variable substitution
- Check for potential conflicts
- Understand what will change

---

### 12.4 profile_apply

**Purpose**: Apply a configuration profile to a device

**Parameters**:
- `device_id` (required): Device to configure
- `profile_id` (required): Profile identifier
- `variables` (optional): Variable substitutions
- `category` (optional): Profile category
- `dry_run` (optional): Preview only, don't execute (default: false)

**Example 1: Dry Run (Safe Preview)**
```
You: Test applying corporate-office profile to office-router
Claude: [Uses profile_apply]
  device_id: "office-router"
  profile_id: "corporate-office"
  variables: {
    "WAN_INTERFACE": "ether1",
    "LAN_BRIDGE": "bridge"
  }
  dry_run: true

Response:
{
  "success": true,
  "dry_run": true,
  "commands": [...15 commands listed...],
  "command_count": 15
}
```

**Example 2: Actual Application**
```
You: Apply corporate-office profile to office-router
Claude: [Uses profile_apply]
  device_id: "office-router"
  profile_id: "corporate-office"
  variables: {
    "WAN_INTERFACE": "ether1",
    "LAN_BRIDGE": "bridge"
  }
  dry_run: false

Response:
{
  "success": true,
  "total_commands": 15,
  "successful": 15,
  "failed": 0,
  "results": [
    {
      "command": "/interface vlan add name=Management vlan-id=10 interface=bridge",
      "success": true
    },
    ...
  ]
}
```

**Example 3: Security Hardening**
```
You: Apply high-security profile to office-router
Claude: [Uses profile_apply]
  device_id: "office-router"
  profile_id: "high-security"

Response:
{
  "success": true,
  "total_commands": 32,
  "successful": 32,
  "failed": 0
}

✓ Security hardening complete:
  - Disabled unused services
  - Changed default ports
  - Enabled SSH rate limiting
  - Configured port scan detection
  - Setup SYN flood protection
```

**Profile Application Best Practices**:
1. **Always dry-run first**: Test before applying
2. **Backup first**: Create config backup
3. **Review variables**: Double-check substitutions
4. **Test on non-production**: Try on test device first
5. **Monitor results**: Check for failed commands
6. **Verify functionality**: Test services after apply

---

### 12.5 profile_validate

**Purpose**: Validate a profile structure

**Parameters**:
- `profile_id` (required): Profile identifier
- `category` (optional): Profile category

**Example**:
```
You: Validate corporate-office profile
Claude: [Uses profile_validate with profile_id="corporate-office"]

Response:
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Profile requires variables: WAN_INTERFACE, LAN_BRIDGE"
  ],
  "variables_required": ["WAN_INTERFACE", "LAN_BRIDGE"]
}
```

**Validation Checks**:
- Profile file exists and is readable
- YAML syntax is correct
- Required fields present
- Variables are defined
- Profile structure is valid

---

### 12.6 profile_save_current

**Purpose**: Save current device configuration as a reusable profile

**Parameters**:
- `device_id` (required): Device to export from
- `profile_name` (required): Name for the new profile
- `category` (required): Profile category
- `description` (required): Profile description

**Example**:
```
You: Save office-router configuration as a profile
Claude: [Uses profile_save_current]
  device_id: "office-router"
  profile_name: "Office Template"
  category: "network"
  description: "Standard office router configuration template"

Response:
{
  "success": true,
  "profile_file": "profiles/network/office-template.yaml",
  "profile_id": "office-template"
}

✓ Profile created successfully!
  You can now apply this configuration to other devices:
  profile_apply(device_id="branch-router", profile_id="office-template")
```

**Use Cases**:
- Template creation from working config
- Configuration standardization
- Documentation
- Disaster recovery templates
- Rapid deployment preparation

---

## 13. Best Practices

### 13.1 Security

**Device Access**:
- Use API connection when possible (most secure)
- Use SSH over Telnet
- Strong passwords for RouterOS users
- Restrict management access by IP
- Change default ports (SSH, Winbox, API)

**Credential Management**:
- Store `devices.json` securely
- Use environment variables for passwords
- Rotate passwords regularly
- Separate admin accounts per admin
- Disable default admin user

**Firewall**:
- Apply security profile first
- Block everything by default
- Allow only necessary traffic
- Use address lists for management
- Log suspicious activity

---

### 13.2 Configuration Management

**Backup Strategy**:
- Backup before changes
- Scheduled backups (daily/weekly)
- Version control for backups
- Off-device storage
- Test restore procedures

**Change Management**:
- Test on non-production first
- Use dry-run mode
- Document changes
- Review audit logs
- Monitor after changes

**Profile Usage**:
- Customize profiles for your needs
- Create site-specific profiles
- Version control profiles
- Document variable requirements
- Test profiles thoroughly

---

### 13.3 Monitoring

**Regular Checks**:
- System resources (CPU, memory)
- Connection status
- Firewall logs
- DHCP lease usage
- VPN connections

**Audit Reviews**:
- Review command history weekly
- Check for failed commands
- Analyze performance metrics
- Identify unusual patterns
- Compliance verification

**Fleet Management**:
- Monitor all devices centrally
- Track connection health
- Identify problem devices
- Standardize configurations
- Update RouterOS versions

---

### 13.4 Troubleshooting

**Connection Issues**:
1. Check network connectivity: `ping device_ip`
2. Verify service is running on device
3. Check firewall rules blocking access
4. Verify credentials in devices.json
5. Try different connection type

**Command Failures**:
1. Check audit log for error details
2. Verify RouterOS version compatibility
3. Test command manually on device
4. Check syntax and parameters
5. Review device-specific limitations

**Performance Issues**:
- Use API instead of SSH/Telnet
- Reduce command frequency
- Check device CPU/memory
- Review connection statistics
- Consider device upgrade

---

## 14. Troubleshooting

### 14.1 Common Issues

**Issue: Cannot Connect to Device**
```
Symptoms: Connection timeout, authentication failure
Solutions:
  1. Verify device is online: ping 192.168.1.1
  2. Check port is correct (SSH: 22, API: 8728)
  3. Verify credentials in devices.json
  4. Ensure service is enabled on router
  5. Check firewall not blocking connection
```

**Issue: Command Execution Fails**
```
Symptoms: Command returns error, "no such item"
Solutions:
  1. Check audit log for detailed error
  2. Verify RouterOS version compatibility
  3. Test command manually in terminal
  4. Check command syntax
  5. Verify required parameters are correct
```

**Issue: Profile Application Fails**
```
Symptoms: Some commands fail during profile apply
Solutions:
  1. Preview profile first with dry_run=true
  2. Check variable substitutions are correct
  3. Review failed commands in results
  4. Verify device has required interfaces
  5. Apply profile incrementally
```

**Issue: Audit Database Locked**
```
Symptoms: "database is locked" error
Solutions:
  1. Wait a moment and retry
  2. Close other MCP server instances
  3. Restart Claude Desktop
  4. Check disk space available
```

**Issue: Slow Performance**
```
Symptoms: Commands take long to execute
Solutions:
  1. Switch from SSH to API connection
  2. Check device CPU/memory usage
  3. Reduce command frequency
  4. Check network latency
  5. Consider RouterOS upgrade
```

---

### 14.2 Error Messages

**"Device not found: router1"**
- Device ID not in devices.json
- Check spelling of device_id
- Reload devices: restart server

**"Not connected to device"**
- Must connect before executing commands
- Use connect_device first
- Check connection status

**"Authentication failed"**
- Wrong username/password
- Update devices.json credentials
- Verify user exists on router

**"Connection timeout"**
- Device offline or unreachable
- Network connectivity issue
- Firewall blocking connection
- Wrong IP address/port

**"Command failed: no such interface"**
- Interface doesn't exist on device
- Check interface names: get_interfaces
- Typo in interface name

**"Already have such address"**
- IP address already configured
- Not an error if re-applying config
- Remove existing first if different

---

### 14.3 Getting Help

**Debug Mode**:
Check server logs for detailed information:
```
Location: mikrotik_mcp.log
Contains: All operations, errors, warnings
```

**Audit History**:
Review recent commands:
```
get_command_history(device_id="router1", limit=20)
```

**Test Connection**:
```
1. connect_device(device_id="router1")
2. execute_command(device_id="router1", command="/system identity print")
3. Check response
```

**Support Information**:
- GitHub: https://github.com/anthropics/claude-code/issues
- MikroTik Forums: https://forum.mikrotik.com
- RouterOS Documentation: https://help.mikrotik.com

---

## 15. Appendix

### 15.1 RouterOS Command Reference

**Common Commands**:
```
/system identity print                    # Show device name
/system resource print                    # System status
/system clock print                       # Date and time
/system routerboard print                 # Hardware info
/system license print                     # License info
/interface print                          # List interfaces
/interface print stats                    # Interface statistics
/ip address print                         # IP addresses
/ip route print                           # Routing table
/ip firewall filter print                 # Firewall rules
/ip firewall nat print                    # NAT rules
/ip dhcp-server lease print               # DHCP leases
/log print                                # System logs
/tool ping address=8.8.8.8 count=5        # Ping test
/tool traceroute address=8.8.8.8          # Traceroute
/interface monitor-traffic ether1         # Traffic monitor
```

**Configuration Commands**:
```
/system identity set name=MyRouter
/ip address add address=192.168.1.1/24 interface=ether1
/ip route add dst-address=0.0.0.0/0 gateway=192.168.1.254
/ip dns set servers=8.8.8.8,8.8.4.4
/system ntp client set enabled=yes servers=0.pool.ntp.org
```

---

### 15.2 Quick Reference

**Connection Flow**:
```
1. list_devices()                  # See available devices
2. connect_device("router1")       # Connect
3. get_system_info("router1")      # Check status
4. execute_command(...)            # Run commands
5. disconnect_device("router1")    # Disconnect
```

**Profile Workflow**:
```
1. profile_list()                  # Browse profiles
2. profile_preview(...)            # Preview commands
3. backup_config("router1")        # Backup first
4. profile_apply(dry_run=true)     # Test apply
5. profile_apply(dry_run=false)    # Apply for real
```

**Fleet Management**:
```
1. get_fleet_status()              # Check all devices
2. Connect to multiple devices
3. execute_on_all_devices(...)     # Run command everywhere
4. Compare results
```

---

### 15.3 Configuration Examples

**Example 1: Basic Router Setup**
```yaml
Goal: Configure a basic router with internet sharing

Steps:
1. connect_device(device_id="router1")
2. execute_command: /ip address add address=192.168.1.1/24 interface=bridge
3. execute_command: /ip address add address=dhcp-client interface=ether1
4. firewall_add_nat_rule(chain="srcnat", action="masquerade", out_interface="ether1")
5. dhcp_create_pool(name="pool1", ranges="192.168.1.100-192.168.1.200")
6. dhcp_create_server(name="dhcp1", interface="bridge", address_pool="pool1")
7. dhcp_add_network(address="192.168.1.0/24", gateway="192.168.1.1")
8. backup_config(device_id="router1")
```

**Example 2: Site-to-Site VPN**
```yaml
Goal: Connect two offices via IPsec VPN

Office A (HQ):
1. vpn_add_ipsec_peer(name="branch", address="203.0.113.50", secret="SecretKey")
2. firewall_add_filter_rule(chain="forward", action="accept", src_address="192.168.1.0/24", dst_address="192.168.2.0/24")

Office B (Branch):
1. vpn_add_ipsec_peer(name="hq", address="203.0.113.100", secret="SecretKey")
2. firewall_add_filter_rule(chain="forward", action="accept", src_address="192.168.2.0/24", dst_address="192.168.1.0/24")
```

**Example 3: Guest WiFi**
```yaml
Goal: Isolated guest WiFi with bandwidth limits

Steps:
1. profile_apply(profile_id="guest-wifi", variables={
     "WIFI_PASSWORD": "GuestPass123",
     "GUEST_SUBNET": "192.168.99.0/24",
     "WAN_INTERFACE": "ether1"
   })
```

---

## Conclusion

This manual covers all 48 MCP tools available in the MikroTik MCP Server. For additional support:

- **Documentation**: Review this manual
- **Examples**: See configuration examples in appendix
- **Profiles**: Use pre-built profiles for rapid deployment
- **Testing**: Always use dry-run mode first
- **Backup**: Backup before changes
- **Audit**: Review command history regularly

**Version**: 1.0
**Last Updated**: January 18, 2026
**Total Tools**: 48
**Supported RouterOS**: 6.x, 7.x

---

**Happy Network Automating! 🚀**
