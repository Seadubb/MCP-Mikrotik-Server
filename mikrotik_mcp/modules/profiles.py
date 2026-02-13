"""Configuration profile management module for MikroTik devices."""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from ..logger import get_logger
from ..models import ConnectionResult

if TYPE_CHECKING:
    from ..device_manager import DeviceManager

logger = get_logger(__name__)


class ProfileManager:
    """Manage configuration profiles and templates."""

    def __init__(self, device_manager: 'DeviceManager', profiles_dir: Optional[Path] = None):
        self.device_manager = device_manager

        if profiles_dir:
            self.profiles_dir = Path(profiles_dir)
        else:
            # Default to profiles directory in project root
            package_dir = Path(__file__).parent.parent
            project_root = package_dir.parent
            self.profiles_dir = project_root / "profiles"

        logger.info(f"ProfileManager initialized with profiles directory: {self.profiles_dir}")

    def list_profiles(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available configuration profiles.

        Args:
            category: Filter by category (network, security, vpn, wireless)

        Returns:
            List of profile metadata
        """
        logger.info(f"Listing profiles (category={category})")
        profiles = []

        if category:
            search_dirs = [self.profiles_dir / category]
        else:
            search_dirs = [
                self.profiles_dir / cat
                for cat in ['network', 'security', 'vpn', 'wireless']
                if (self.profiles_dir / cat).exists()
            ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for profile_file in search_dir.glob("*.yaml"):
                try:
                    with open(profile_file, 'r', encoding='utf-8') as f:
                        profile_data = yaml.safe_load(f)

                    profile_info = profile_data.get('profile', {})
                    profiles.append({
                        'id': profile_file.stem,
                        'category': search_dir.name,
                        'name': profile_info.get('name', profile_file.stem),
                        'description': profile_info.get('description', ''),
                        'file': str(profile_file),
                        'variables': profile_info.get('variables', [])
                    })
                except Exception as e:
                    logger.error(f"Error reading profile {profile_file}: {e}")

        logger.info(f"Found {len(profiles)} profiles")
        return profiles

    def get_profile(self, profile_id: str, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get a specific profile by ID.

        Args:
            profile_id: Profile identifier (filename without extension)
            category: Optional category to narrow search

        Returns:
            Profile data or None
        """
        logger.info(f"Getting profile: {profile_id} (category={category})")

        if category:
            search_dirs = [self.profiles_dir / category]
        else:
            search_dirs = [
                self.profiles_dir / cat
                for cat in ['network', 'security', 'vpn', 'wireless']
                if (self.profiles_dir / cat).exists()
            ]

        for search_dir in search_dirs:
            profile_file = search_dir / f"{profile_id}.yaml"
            if profile_file.exists():
                try:
                    with open(profile_file, 'r', encoding='utf-8') as f:
                        profile_data = yaml.safe_load(f)
                    logger.info(f"Found profile: {profile_file}")
                    return profile_data
                except Exception as e:
                    logger.error(f"Error reading profile {profile_file}: {e}")
                    return None

        logger.warning(f"Profile not found: {profile_id}")
        return None

    def _substitute_variables(self, config: Any, variables: Dict[str, str]) -> Any:
        """
        Recursively substitute variables in configuration.

        Args:
            config: Configuration data (dict, list, or string)
            variables: Variable substitutions

        Returns:
            Configuration with variables substituted
        """
        if isinstance(config, dict):
            return {k: self._substitute_variables(v, variables) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_variables(item, variables) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with variable values
            result = config
            for var_name, var_value in variables.items():
                result = result.replace(f"${{{var_name}}}", str(var_value))
            return result
        else:
            return config

    def preview_profile_commands(
        self,
        profile_id: str,
        variables: Optional[Dict[str, str]] = None,
        category: Optional[str] = None
    ) -> List[str]:
        """
        Preview commands that would be executed for a profile.

        Args:
            profile_id: Profile identifier
            variables: Variable substitutions
            category: Optional category

        Returns:
            List of RouterOS commands
        """
        logger.info(f"Previewing commands for profile: {profile_id}")

        profile_data = self.get_profile(profile_id, category)
        if not profile_data:
            return []

        variables = variables or {}
        profile_config = profile_data.get('profile', {})

        # Substitute variables
        profile_config = self._substitute_variables(profile_config, variables)

        # Generate commands based on profile structure
        commands = []
        commands.extend(self._generate_commands_from_config(profile_config))

        logger.info(f"Generated {len(commands)} commands")
        return commands

    def _generate_commands_from_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Generate RouterOS commands from profile configuration.

        Args:
            config: Profile configuration

        Returns:
            List of RouterOS commands
        """
        commands = []

        # Process interfaces configuration
        if 'interfaces' in config:
            interfaces_config = config['interfaces']

            # VLANs
            if 'vlans' in interfaces_config:
                for vlan in interfaces_config['vlans']:
                    vlan_id = vlan.get('id')
                    name = vlan.get('name', f"vlan{vlan_id}")
                    bridge = interfaces_config.get('lan_bridge', 'bridge')

                    commands.append(f"/interface vlan add name={name} vlan-id={vlan_id} interface={bridge}")

                    # Add IP address
                    if 'subnet' in vlan:
                        subnet = vlan['subnet']
                        # Extract first IP from subnet (e.g., 192.168.10.0/24 -> 192.168.10.1/24)
                        parts = subnet.split('/')
                        if len(parts) == 2:
                            network = parts[0]
                            mask = parts[1]
                            ip_parts = network.split('.')
                            ip_parts[-1] = '1'
                            ip_address = '.'.join(ip_parts)
                            commands.append(f"/ip address add address={ip_address}/{mask} interface={name}")

        # Process firewall configuration
        if 'firewall' in config:
            fw_config = config['firewall']

            if 'rules' in fw_config:
                for rule in fw_config['rules']:
                    if isinstance(rule, str):
                        # Simple rule description, convert to command
                        if 'allow established' in rule.lower():
                            commands.append('/ip firewall filter add chain=forward action=accept connection-state=established,related comment="Allow established/related"')
                        elif 'drop invalid' in rule.lower():
                            commands.append('/ip firewall filter add chain=forward action=drop connection-state=invalid comment="Drop invalid"')
                        elif 'allow icmp' in rule.lower():
                            commands.append('/ip firewall filter add chain=input action=accept protocol=icmp comment="Allow ICMP"')
                        elif 'nat outbound' in rule.lower():
                            wan_interface = config.get('interfaces', {}).get('wan', 'ether1')
                            commands.append(f'/ip firewall nat add chain=srcnat action=masquerade out-interface={wan_interface} comment="NAT outbound"')

        # Process DHCP servers
        if 'dhcp_servers' in config:
            for dhcp in config['dhcp_servers']:
                vlan = dhcp.get('vlan')
                range_str = dhcp.get('range', '')

                if vlan and range_str:
                    vlan_name = f"vlan{vlan}"
                    pool_name = f"pool-vlan{vlan}"
                    server_name = f"dhcp-vlan{vlan}"

                    # Create pool
                    commands.append(f"/ip pool add name={pool_name} ranges={range_str}")

                    # Create DHCP server
                    commands.append(f"/ip dhcp-server add name={server_name} interface={vlan_name} address-pool={pool_name}")

                    # Add network (assuming gateway is .1)
                    if 'subnet' in [v for v in config.get('interfaces', {}).get('vlans', []) if v.get('id') == vlan]:
                        subnet_obj = next(v for v in config.get('interfaces', {}).get('vlans', []) if v.get('id') == vlan)
                        subnet = subnet_obj.get('subnet', '')
                        if subnet:
                            parts = subnet.split('/')
                            if len(parts) == 2:
                                network = parts[0]
                                mask = parts[1]
                                ip_parts = network.split('.')
                                ip_parts[-1] = '1'
                                gateway = '.'.join(ip_parts)
                                commands.append(f"/ip dhcp-server network add address={subnet} gateway={gateway}")

        # Process VPN configuration
        if 'vpn_config' in config:
            vpn = config['vpn_config']
            vpn_type = vpn.get('type', '')

            if vpn_type == 'l2tp':
                use_ipsec = vpn.get('use_ipsec', True)
                ipsec_secret = vpn.get('ipsec_secret', '')

                commands.append(f'/interface l2tp-server server set enabled=yes use-ipsec={"yes" if use_ipsec else "no"}')

                if ipsec_secret:
                    commands.append(f'/interface l2tp-server server set ipsec-secret={ipsec_secret}')

                # Create address pool
                if 'address_pool' in vpn:
                    pool = vpn['address_pool']
                    commands.append(f'/ip pool add name=vpn-pool ranges={pool}')

        # Process wireless configuration
        if 'wireless' in config:
            wl = config['wireless']
            ssid = wl.get('ssid', '')
            security = wl.get('security', 'wpa2')
            password = wl.get('password', '')

            if ssid:
                # Create security profile
                profile_name = f"profile-{ssid}"
                if security == 'wpa2':
                    commands.append(f'/interface wireless security-profiles add name={profile_name} mode=dynamic-keys authentication-types=wpa2-psk wpa2-pre-shared-key={password}')

                # Configure wireless interface (assumes wlan1)
                commands.append(f'/interface wireless set wlan1 ssid={ssid} security-profile={profile_name}')

                if wl.get('isolation', False):
                    commands.append('/interface wireless set wlan1 station-bridge-clone-mac=no')

        # Process custom commands
        if 'commands' in config:
            commands.extend(config['commands'])

        return commands

    async def apply_profile(
        self,
        device_id: str,
        profile_id: str,
        variables: Optional[Dict[str, str]] = None,
        category: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Apply a configuration profile to a device.

        Args:
            device_id: Device to configure
            profile_id: Profile identifier
            variables: Variable substitutions
            category: Optional category
            dry_run: If True, only preview commands without executing

        Returns:
            Result dictionary with status and details
        """
        logger.info(f"Applying profile '{profile_id}' to device '{device_id}' (dry_run={dry_run})")

        # Get commands
        commands = self.preview_profile_commands(profile_id, variables, category)

        if not commands:
            return {
                'success': False,
                'error': f"Profile '{profile_id}' not found or contains no commands",
                'commands': []
            }

        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'commands': commands,
                'command_count': len(commands)
            }

        # Execute commands
        results = []
        successful = 0
        failed = 0

        for i, cmd in enumerate(commands):
            try:
                result = await self.device_manager.execute_command(device_id, cmd, use_cache=False)
                results.append({
                    'command': cmd,
                    'success': result.success,
                    'output': result.output,
                    'error': result.error
                })

                if result.success:
                    successful += 1
                else:
                    failed += 1
                    logger.warning(f"Command {i+1}/{len(commands)} failed: {cmd} - {result.error}")

            except Exception as e:
                results.append({
                    'command': cmd,
                    'success': False,
                    'output': None,
                    'error': str(e)
                })
                failed += 1
                logger.error(f"Exception executing command {i+1}/{len(commands)}: {e}")

        return {
            'success': failed == 0,
            'total_commands': len(commands),
            'successful': successful,
            'failed': failed,
            'results': results
        }

    def validate_profile(self, profile_id: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate a profile structure.

        Args:
            profile_id: Profile identifier
            category: Optional category

        Returns:
            Validation result
        """
        logger.info(f"Validating profile: {profile_id}")

        profile_data = self.get_profile(profile_id, category)

        if not profile_data:
            return {
                'valid': False,
                'error': f"Profile '{profile_id}' not found"
            }

        errors = []
        warnings = []

        # Check required fields
        profile_info = profile_data.get('profile', {})

        if not profile_info.get('name'):
            errors.append("Missing profile name")

        if not profile_info.get('description'):
            warnings.append("Missing profile description")

        # Check for variables that need substitution
        variables_needed = profile_info.get('variables', [])
        if variables_needed:
            warnings.append(f"Profile requires variables: {', '.join(variables_needed)}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'variables_required': variables_needed
        }

    async def save_current_as_profile(
        self,
        device_id: str,
        profile_name: str,
        category: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Export current device configuration as a reusable profile.

        Args:
            device_id: Device to export from
            profile_name: Name for the profile
            category: Profile category
            description: Profile description

        Returns:
            Result dictionary
        """
        logger.info(f"Saving device '{device_id}' configuration as profile '{profile_name}'")

        # Export current configuration
        config_text = await self.device_manager.export_config(device_id)

        # Create profile structure
        profile_data = {
            'profile': {
                'name': profile_name,
                'description': description,
                'source_device': device_id,
                'commands': config_text.split('\n')
            }
        }

        # Save to file
        category_dir = self.profiles_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        profile_file = category_dir / f"{profile_name.lower().replace(' ', '-')}.yaml"

        try:
            with open(profile_file, 'w', encoding='utf-8') as f:
                yaml.dump(profile_data, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Profile saved to {profile_file}")

            return {
                'success': True,
                'profile_file': str(profile_file),
                'profile_id': profile_file.stem
            }
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            return {
                'success': False,
                'error': str(e)
            }
