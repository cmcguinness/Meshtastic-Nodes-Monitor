"""
Node Configuration Service for Meshtastic Monitor

This singleton service handles reading and writing Meshtastic node configuration
through the Python API.
"""

from mesh import Mesh


class NodeConfig:
    """Singleton service for Meshtastic node configuration"""

    _instance = None

    # Enum mappings for human-readable values
    DEVICE_ROLES = {
        0: 'CLIENT',
        1: 'CLIENT_MUTE',
        2: 'ROUTER',
        3: 'ROUTER_CLIENT',
        4: 'REPEATER',
        5: 'TRACKER',
        6: 'SENSOR',
        7: 'TAK',
        8: 'CLIENT_HIDDEN',
        9: 'LOST_AND_FOUND',
        10: 'TAK_TRACKER',
        11: 'ROUTER_LATE'
    }

    REBROADCAST_MODES = {
        0: 'ALL',
        1: 'ALL_SKIP_DECODING',
        2: 'LOCAL_ONLY',
        3: 'KNOWN_ONLY',
        4: 'NONE',
        5: 'CORE_PORTNUMS_ONLY'
    }

    REGIONS = {
        0: 'UNSET',
        1: 'US',
        2: 'EU_433',
        3: 'EU_868',
        4: 'CN',
        5: 'JP',
        6: 'ANZ',
        7: 'KR',
        8: 'TW',
        9: 'RU',
        10: 'IN',
        11: 'NZ_865',
        12: 'TH',
        13: 'LORA_24',
        14: 'UA_433',
        15: 'UA_868',
        16: 'MY_433',
        17: 'MY_919',
        18: 'SG_923',
        19: 'PH_433',
        20: 'PH_868',
        21: 'PH_915'
    }

    MODEM_PRESETS = {
        0: 'LONG_FAST',
        1: 'LONG_SLOW',
        2: 'VERY_LONG_SLOW',
        3: 'MEDIUM_SLOW',
        4: 'MEDIUM_FAST',
        5: 'SHORT_SLOW',
        6: 'SHORT_FAST',
        7: 'LONG_MODERATE',
        8: 'SHORT_TURBO'
    }

    GPS_MODES = {
        0: 'DISABLED',
        1: 'ENABLED',
        2: 'NOT_PRESENT'
    }

    GPS_FORMATS = {
        0: 'DEC',
        1: 'DMS',
        2: 'UTM',
        3: 'MGRS',
        4: 'OLC',
        5: 'OSGR'
    }

    DISPLAY_UNITS = {
        0: 'METRIC',
        1: 'IMPERIAL'
    }

    DISPLAY_MODES = {
        0: 'DEFAULT',
        1: 'TWOCOLOR',
        2: 'INVERTED',
        3: 'COLOR'
    }

    BLUETOOTH_MODES = {
        0: 'RANDOM_PIN',
        1: 'FIXED_PIN',
        2: 'NO_PIN'
    }

    ADDRESS_MODES = {
        0: 'DHCP',
        1: 'STATIC'
    }

    SERIAL_MODES = {
        0: 'DEFAULT',
        1: 'SIMPLE',
        2: 'PROTO',
        3: 'TEXTMSG',
        4: 'NMEA',
        5: 'CALTOPO',
        6: 'WS85',
        7: 'VE_DIRECT'
    }

    SERIAL_BAUD = {
        0: 'BAUD_DEFAULT',
        1: 'BAUD_110',
        2: 'BAUD_300',
        3: 'BAUD_600',
        4: 'BAUD_1200',
        5: 'BAUD_2400',
        6: 'BAUD_4800',
        7: 'BAUD_9600',
        8: 'BAUD_19200',
        9: 'BAUD_38400',
        10: 'BAUD_57600',
        11: 'BAUD_115200',
        12: 'BAUD_230400',
        13: 'BAUD_460800',
        14: 'BAUD_576000',
        15: 'BAUD_921600'
    }

    CHANNEL_ROLES = {
        0: 'DISABLED',
        1: 'PRIMARY',
        2: 'SECONDARY'
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NodeConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    def _get_local_node(self):
        """Get the local node from the Mesh singleton"""
        return Mesh().node.localNode

    def _get_local_config(self):
        """Get the localConfig object from the node"""
        return self._get_local_node().localConfig

    def _get_module_config(self):
        """Get the moduleConfig object from the node"""
        return self._get_local_node().moduleConfig

    def _safe_get(self, obj, attr, default=None):
        """Safely get an attribute from a protobuf object"""
        try:
            value = getattr(obj, attr, default)
            # Handle protobuf default values
            if value is None:
                return default
            return value
        except Exception:
            return default

    def _enum_to_options(self, enum_dict, current_value):
        """Convert enum dict to list of options with current selection marked"""
        options = []
        for value, name in enum_dict.items():
            options.append({
                'value': value,
                'name': name,
                'selected': value == current_value
            })
        return options

    def get_device_config(self) -> dict:
        """Get device configuration"""
        try:
            config = self._get_local_config().device
            role = self._safe_get(config, 'role', 0)
            rebroadcast = self._safe_get(config, 'rebroadcast_mode', 0)

            return {
                'success': True,
                'config': {
                    'role': role,
                    'role_name': self.DEVICE_ROLES.get(role, f'Unknown ({role})'),
                    'role_options': self._enum_to_options(self.DEVICE_ROLES, role),
                    'rebroadcast_mode': rebroadcast,
                    'rebroadcast_mode_name': self.REBROADCAST_MODES.get(rebroadcast, f'Unknown ({rebroadcast})'),
                    'rebroadcast_mode_options': self._enum_to_options(self.REBROADCAST_MODES, rebroadcast),
                    'node_info_broadcast_secs': self._safe_get(config, 'node_info_broadcast_secs', 900),
                    'double_tap_as_button_press': self._safe_get(config, 'double_tap_as_button_press', False),
                    'disable_triple_click': self._safe_get(config, 'disable_triple_click', False),
                    'led_heartbeat_disabled': self._safe_get(config, 'led_heartbeat_disabled', False),
                    'tzdef': self._safe_get(config, 'tzdef', ''),
                    'button_gpio': self._safe_get(config, 'button_gpio', 0),
                    'buzzer_gpio': self._safe_get(config, 'buzzer_gpio', 0),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_lora_config(self) -> dict:
        """Get LoRa configuration"""
        try:
            config = self._get_local_config().lora
            region = self._safe_get(config, 'region', 0)
            preset = self._safe_get(config, 'modem_preset', 0)

            return {
                'success': True,
                'config': {
                    'region': region,
                    'region_name': self.REGIONS.get(region, f'Unknown ({region})'),
                    'region_options': self._enum_to_options(self.REGIONS, region),
                    'modem_preset': preset,
                    'modem_preset_name': self.MODEM_PRESETS.get(preset, f'Unknown ({preset})'),
                    'modem_preset_options': self._enum_to_options(self.MODEM_PRESETS, preset),
                    'use_preset': self._safe_get(config, 'use_preset', True),
                    'tx_enabled': self._safe_get(config, 'tx_enabled', True),
                    'tx_power': self._safe_get(config, 'tx_power', 0),
                    'hop_limit': self._safe_get(config, 'hop_limit', 3),
                    'channel_num': self._safe_get(config, 'channel_num', 0),
                    'bandwidth': self._safe_get(config, 'bandwidth', 0),
                    'spread_factor': self._safe_get(config, 'spread_factor', 0),
                    'coding_rate': self._safe_get(config, 'coding_rate', 0),
                    'frequency_offset': self._safe_get(config, 'frequency_offset', 0),
                    'override_duty_cycle': self._safe_get(config, 'override_duty_cycle', False),
                    'override_frequency': self._safe_get(config, 'override_frequency', 0),
                    'ignore_mqtt': self._safe_get(config, 'ignore_mqtt', False),
                    'config_ok_to_mqtt': self._safe_get(config, 'config_ok_to_mqtt', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_position_config(self) -> dict:
        """Get position configuration"""
        try:
            config = self._get_local_config().position
            gps_mode = self._safe_get(config, 'gps_mode', 0)

            return {
                'success': True,
                'config': {
                    'gps_mode': gps_mode,
                    'gps_mode_name': self.GPS_MODES.get(gps_mode, f'Unknown ({gps_mode})'),
                    'gps_mode_options': self._enum_to_options(self.GPS_MODES, gps_mode),
                    'gps_enabled': self._safe_get(config, 'gps_enabled', True),
                    'gps_update_interval': self._safe_get(config, 'gps_update_interval', 0),
                    'position_broadcast_secs': self._safe_get(config, 'position_broadcast_secs', 900),
                    'position_broadcast_smart_enabled': self._safe_get(config, 'position_broadcast_smart_enabled', True),
                    'broadcast_smart_minimum_distance': self._safe_get(config, 'broadcast_smart_minimum_distance', 100),
                    'broadcast_smart_minimum_interval_secs': self._safe_get(config, 'broadcast_smart_minimum_interval_secs', 30),
                    'fixed_position': self._safe_get(config, 'fixed_position', False),
                    'latitude_i': self._safe_get(config, 'latitude_i', 0),
                    'longitude_i': self._safe_get(config, 'longitude_i', 0),
                    'altitude': self._safe_get(config, 'altitude', 0),
                    'gps_en_gpio': self._safe_get(config, 'gps_en_gpio', 0),
                    'rx_gpio': self._safe_get(config, 'rx_gpio', 0),
                    'tx_gpio': self._safe_get(config, 'tx_gpio', 0),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_power_config(self) -> dict:
        """Get power configuration"""
        try:
            config = self._get_local_config().power

            return {
                'success': True,
                'config': {
                    'is_power_saving': self._safe_get(config, 'is_power_saving', False),
                    'on_battery_shutdown_after_secs': self._safe_get(config, 'on_battery_shutdown_after_secs', 0),
                    'wait_bluetooth_secs': self._safe_get(config, 'wait_bluetooth_secs', 60),
                    'sds_secs': self._safe_get(config, 'sds_secs', 4294967295),
                    'ls_secs': self._safe_get(config, 'ls_secs', 300),
                    'min_wake_secs': self._safe_get(config, 'min_wake_secs', 10),
                    'device_battery_ina_address': self._safe_get(config, 'device_battery_ina_address', 0),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_network_config(self) -> dict:
        """Get network configuration"""
        try:
            config = self._get_local_config().network
            address_mode = self._safe_get(config, 'address_mode', 0)

            return {
                'success': True,
                'config': {
                    'wifi_enabled': self._safe_get(config, 'wifi_enabled', False),
                    'wifi_ssid': self._safe_get(config, 'wifi_ssid', ''),
                    'wifi_psk': '********' if self._safe_get(config, 'wifi_psk', '') else '',
                    'ntp_server': self._safe_get(config, 'ntp_server', ''),
                    'eth_enabled': self._safe_get(config, 'eth_enabled', False),
                    'address_mode': address_mode,
                    'address_mode_name': self.ADDRESS_MODES.get(address_mode, f'Unknown ({address_mode})'),
                    'address_mode_options': self._enum_to_options(self.ADDRESS_MODES, address_mode),
                    'ipv6_enabled': self._safe_get(config, 'ipv6_enabled', False),
                    'syslog_server': self._safe_get(config, 'syslog_server', ''),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_display_config(self) -> dict:
        """Get display configuration"""
        try:
            config = self._get_local_config().display
            gps_format = self._safe_get(config, 'gps_format', 0)
            units = self._safe_get(config, 'units', 0)
            displaymode = self._safe_get(config, 'displaymode', 0)

            return {
                'success': True,
                'config': {
                    'screen_on_secs': self._safe_get(config, 'screen_on_secs', 0),
                    'gps_format': gps_format,
                    'gps_format_name': self.GPS_FORMATS.get(gps_format, f'Unknown ({gps_format})'),
                    'gps_format_options': self._enum_to_options(self.GPS_FORMATS, gps_format),
                    'auto_screen_carousel_secs': self._safe_get(config, 'auto_screen_carousel_secs', 0),
                    'compass_north_top': self._safe_get(config, 'compass_north_top', False),
                    'flip_screen': self._safe_get(config, 'flip_screen', False),
                    'units': units,
                    'units_name': self.DISPLAY_UNITS.get(units, f'Unknown ({units})'),
                    'units_options': self._enum_to_options(self.DISPLAY_UNITS, units),
                    'displaymode': displaymode,
                    'displaymode_name': self.DISPLAY_MODES.get(displaymode, f'Unknown ({displaymode})'),
                    'displaymode_options': self._enum_to_options(self.DISPLAY_MODES, displaymode),
                    'heading_bold': self._safe_get(config, 'heading_bold', False),
                    'wake_on_tap_or_motion': self._safe_get(config, 'wake_on_tap_or_motion', False),
                    'use_12h_clock': self._safe_get(config, 'use_12h_clock', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_bluetooth_config(self) -> dict:
        """Get Bluetooth configuration"""
        try:
            config = self._get_local_config().bluetooth
            mode = self._safe_get(config, 'mode', 0)

            return {
                'success': True,
                'config': {
                    'enabled': self._safe_get(config, 'enabled', True),
                    'mode': mode,
                    'mode_name': self.BLUETOOTH_MODES.get(mode, f'Unknown ({mode})'),
                    'mode_options': self._enum_to_options(self.BLUETOOTH_MODES, mode),
                    'fixed_pin': self._safe_get(config, 'fixed_pin', 123456),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_security_config(self) -> dict:
        """Get security configuration"""
        try:
            config = self._get_local_config().security

            return {
                'success': True,
                'config': {
                    'is_managed': self._safe_get(config, 'is_managed', False),
                    'serial_enabled': self._safe_get(config, 'serial_enabled', True),
                    'debug_log_api_enabled': self._safe_get(config, 'debug_log_api_enabled', False),
                    'admin_channel_enabled': self._safe_get(config, 'admin_channel_enabled', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # Module Configurations

    def get_mqtt_config(self) -> dict:
        """Get MQTT module configuration"""
        try:
            config = self._get_module_config().mqtt

            return {
                'success': True,
                'config': {
                    'enabled': self._safe_get(config, 'enabled', False),
                    'address': self._safe_get(config, 'address', ''),
                    'username': self._safe_get(config, 'username', ''),
                    'password': '********' if self._safe_get(config, 'password', '') else '',
                    'encryption_enabled': self._safe_get(config, 'encryption_enabled', True),
                    'json_enabled': self._safe_get(config, 'json_enabled', False),
                    'tls_enabled': self._safe_get(config, 'tls_enabled', False),
                    'root': self._safe_get(config, 'root', 'msh'),
                    'proxy_to_client_enabled': self._safe_get(config, 'proxy_to_client_enabled', False),
                    'map_reporting_enabled': self._safe_get(config, 'map_reporting_enabled', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_serial_config(self) -> dict:
        """Get Serial module configuration"""
        try:
            config = self._get_module_config().serial
            mode = self._safe_get(config, 'mode', 0)
            baud = self._safe_get(config, 'baud', 0)

            return {
                'success': True,
                'config': {
                    'enabled': self._safe_get(config, 'enabled', False),
                    'echo': self._safe_get(config, 'echo', False),
                    'rxd': self._safe_get(config, 'rxd', 0),
                    'txd': self._safe_get(config, 'txd', 0),
                    'baud': baud,
                    'baud_name': self.SERIAL_BAUD.get(baud, f'Unknown ({baud})'),
                    'baud_options': self._enum_to_options(self.SERIAL_BAUD, baud),
                    'timeout': self._safe_get(config, 'timeout', 0),
                    'mode': mode,
                    'mode_name': self.SERIAL_MODES.get(mode, f'Unknown ({mode})'),
                    'mode_options': self._enum_to_options(self.SERIAL_MODES, mode),
                    'override_console_serial_port': self._safe_get(config, 'override_console_serial_port', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_telemetry_config(self) -> dict:
        """Get Telemetry module configuration"""
        try:
            config = self._get_module_config().telemetry

            return {
                'success': True,
                'config': {
                    'device_update_interval': self._safe_get(config, 'device_update_interval', 0),
                    'environment_update_interval': self._safe_get(config, 'environment_update_interval', 0),
                    'environment_measurement_enabled': self._safe_get(config, 'environment_measurement_enabled', False),
                    'environment_screen_enabled': self._safe_get(config, 'environment_screen_enabled', False),
                    'environment_display_fahrenheit': self._safe_get(config, 'environment_display_fahrenheit', False),
                    'air_quality_enabled': self._safe_get(config, 'air_quality_enabled', False),
                    'air_quality_interval': self._safe_get(config, 'air_quality_interval', 0),
                    'power_measurement_enabled': self._safe_get(config, 'power_measurement_enabled', False),
                    'power_update_interval': self._safe_get(config, 'power_update_interval', 0),
                    'power_screen_enabled': self._safe_get(config, 'power_screen_enabled', False),
                    'health_measurement_enabled': self._safe_get(config, 'health_measurement_enabled', False),
                    'health_update_interval': self._safe_get(config, 'health_update_interval', 0),
                    'health_screen_enabled': self._safe_get(config, 'health_screen_enabled', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_store_forward_config(self) -> dict:
        """Get Store & Forward module configuration"""
        try:
            config = self._get_module_config().store_forward

            return {
                'success': True,
                'config': {
                    'enabled': self._safe_get(config, 'enabled', False),
                    'heartbeat': self._safe_get(config, 'heartbeat', False),
                    'records': self._safe_get(config, 'records', 0),
                    'history_return_max': self._safe_get(config, 'history_return_max', 0),
                    'history_return_window': self._safe_get(config, 'history_return_window', 0),
                    'is_server': self._safe_get(config, 'is_server', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_external_notification_config(self) -> dict:
        """Get External Notification module configuration"""
        try:
            config = self._get_module_config().external_notification

            return {
                'success': True,
                'config': {
                    'enabled': self._safe_get(config, 'enabled', False),
                    'output_ms': self._safe_get(config, 'output_ms', 0),
                    'output': self._safe_get(config, 'output', 0),
                    'output_vibra': self._safe_get(config, 'output_vibra', 0),
                    'output_buzzer': self._safe_get(config, 'output_buzzer', 0),
                    'active': self._safe_get(config, 'active', False),
                    'alert_message': self._safe_get(config, 'alert_message', False),
                    'alert_message_vibra': self._safe_get(config, 'alert_message_vibra', False),
                    'alert_message_buzzer': self._safe_get(config, 'alert_message_buzzer', False),
                    'alert_bell': self._safe_get(config, 'alert_bell', False),
                    'use_pwm': self._safe_get(config, 'use_pwm', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_range_test_config(self) -> dict:
        """Get Range Test module configuration"""
        try:
            config = self._get_module_config().range_test

            return {
                'success': True,
                'config': {
                    'enabled': self._safe_get(config, 'enabled', False),
                    'sender': self._safe_get(config, 'sender', 0),
                    'save': self._safe_get(config, 'save', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_neighbor_info_config(self) -> dict:
        """Get Neighbor Info module configuration"""
        try:
            config = self._get_module_config().neighbor_info

            return {
                'success': True,
                'config': {
                    'enabled': self._safe_get(config, 'enabled', False),
                    'update_interval': self._safe_get(config, 'update_interval', 0),
                    'transmit_over_lora': self._safe_get(config, 'transmit_over_lora', True),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_detection_sensor_config(self) -> dict:
        """Get Detection Sensor module configuration"""
        try:
            config = self._get_module_config().detection_sensor

            return {
                'success': True,
                'config': {
                    'enabled': self._safe_get(config, 'enabled', False),
                    'monitor_pin': self._safe_get(config, 'monitor_pin', 0),
                    'detection_trigger_type': self._safe_get(config, 'detection_trigger_type', 0),
                    'minimum_broadcast_secs': self._safe_get(config, 'minimum_broadcast_secs', 0),
                    'send_bell': self._safe_get(config, 'send_bell', False),
                    'name': self._safe_get(config, 'name', ''),
                    'use_pullup': self._safe_get(config, 'use_pullup', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_audio_config(self) -> dict:
        """Get Audio module configuration"""
        try:
            config = self._get_module_config().audio

            return {
                'success': True,
                'config': {
                    'codec2_enabled': self._safe_get(config, 'codec2_enabled', False),
                    'ptt_pin': self._safe_get(config, 'ptt_pin', 0),
                    'bitrate': self._safe_get(config, 'bitrate', 0),
                    'i2s_ws': self._safe_get(config, 'i2s_ws', 0),
                    'i2s_sd': self._safe_get(config, 'i2s_sd', 0),
                    'i2s_din': self._safe_get(config, 'i2s_din', 0),
                    'i2s_sck': self._safe_get(config, 'i2s_sck', 0),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_remote_hardware_config(self) -> dict:
        """Get Remote Hardware module configuration"""
        try:
            config = self._get_module_config().remote_hardware

            return {
                'success': True,
                'config': {
                    'enabled': self._safe_get(config, 'enabled', False),
                    'allow_undefined_pin_access': self._safe_get(config, 'allow_undefined_pin_access', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_ambient_lighting_config(self) -> dict:
        """Get Ambient Lighting module configuration"""
        try:
            config = self._get_module_config().ambient_lighting

            return {
                'success': True,
                'config': {
                    'led_state': self._safe_get(config, 'led_state', False),
                    'current': self._safe_get(config, 'current', 0),
                    'red': self._safe_get(config, 'red', 0),
                    'green': self._safe_get(config, 'green', 0),
                    'blue': self._safe_get(config, 'blue', 0),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_paxcounter_config(self) -> dict:
        """Get Paxcounter module configuration"""
        try:
            config = self._get_module_config().paxcounter

            return {
                'success': True,
                'config': {
                    'enabled': self._safe_get(config, 'enabled', False),
                    'paxcounter_update_interval': self._safe_get(config, 'paxcounter_update_interval', 0),
                    'wifi_threshold': self._safe_get(config, 'wifi_threshold', 0),
                    'ble_threshold': self._safe_get(config, 'ble_threshold', 0),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_canned_message_config(self) -> dict:
        """Get Canned Message module configuration"""
        try:
            config = self._get_module_config().canned_message

            return {
                'success': True,
                'config': {
                    'enabled': self._safe_get(config, 'enabled', False),
                    'rotary1_enabled': self._safe_get(config, 'rotary1_enabled', False),
                    'inputbroker_pin_a': self._safe_get(config, 'inputbroker_pin_a', 0),
                    'inputbroker_pin_b': self._safe_get(config, 'inputbroker_pin_b', 0),
                    'inputbroker_pin_press': self._safe_get(config, 'inputbroker_pin_press', 0),
                    'inputbroker_event_cw': self._safe_get(config, 'inputbroker_event_cw', 0),
                    'inputbroker_event_ccw': self._safe_get(config, 'inputbroker_event_ccw', 0),
                    'inputbroker_event_press': self._safe_get(config, 'inputbroker_event_press', 0),
                    'allow_input_source': self._safe_get(config, 'allow_input_source', 0),
                    'send_bell': self._safe_get(config, 'send_bell', False),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_all_config(self) -> dict:
        """Get all configuration sections"""
        return {
            'device': self.get_device_config(),
            'lora': self.get_lora_config(),
            'channels': self.get_channels_config(),
            'position': self.get_position_config(),
            'power': self.get_power_config(),
            'network': self.get_network_config(),
            'display': self.get_display_config(),
            'bluetooth': self.get_bluetooth_config(),
            'security': self.get_security_config(),
            'mqtt': self.get_mqtt_config(),
            'serial': self.get_serial_config(),
            'telemetry': self.get_telemetry_config(),
            'store_forward': self.get_store_forward_config(),
            'external_notification': self.get_external_notification_config(),
            'range_test': self.get_range_test_config(),
            'neighbor_info': self.get_neighbor_info_config(),
            'detection_sensor': self.get_detection_sensor_config(),
            'audio': self.get_audio_config(),
            'remote_hardware': self.get_remote_hardware_config(),
            'ambient_lighting': self.get_ambient_lighting_config(),
            'paxcounter': self.get_paxcounter_config(),
            'canned_message': self.get_canned_message_config(),
        }

    # Update methods

    def update_device_config(self, **kwargs) -> dict:
        """Update device configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.localConfig.device

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('device')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_lora_config(self, **kwargs) -> dict:
        """Update LoRa configuration"""
        try:
            node = self._get_local_node()
            print(f'[CONFIG] Updating LoRa config with: {kwargs}', flush=True)

            node.ensureSessionKey()
            config = node.localConfig.lora

            print(f'[CONFIG] Current modem_preset before update: {config.modem_preset}', flush=True)

            for key, value in kwargs.items():
                if hasattr(config, key):
                    print(f'[CONFIG] Setting {key} = {value}', flush=True)
                    setattr(config, key, value)
                else:
                    print(f'[CONFIG] WARNING: Config does not have attribute: {key}', flush=True)

            print(f'[CONFIG] modem_preset after setattr: {config.modem_preset}', flush=True)

            node.writeConfig('lora')
            print('[CONFIG] writeConfig completed successfully', flush=True)

            return {'success': True, 'reboot_required': True}
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            # Connection errors might occur if device reboots itself
            print(f'[CONFIG] Connection error during LoRa config write (this may be normal): {e}', flush=True)
            return {'success': True, 'reboot_required': True, 'note': 'Config sent, connection lost (device may have auto-rebooted)'}
        except Exception as e:
            print(f'[CONFIG] ERROR updating LoRa config: {e}', flush=True)
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def update_position_config(self, **kwargs) -> dict:
        """Update position configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.localConfig.position

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('position')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_power_config(self, **kwargs) -> dict:
        """Update power configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.localConfig.power

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('power')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_network_config(self, **kwargs) -> dict:
        """Update network configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.localConfig.network

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('network')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_display_config(self, **kwargs) -> dict:
        """Update display configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.localConfig.display

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('display')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_bluetooth_config(self, **kwargs) -> dict:
        """Update Bluetooth configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.localConfig.bluetooth

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('bluetooth')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_security_config(self, **kwargs) -> dict:
        """Update security configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.localConfig.security

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('security')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # Module update methods

    def update_mqtt_config(self, **kwargs) -> dict:
        """Update MQTT module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.mqtt

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('mqtt')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_serial_config(self, **kwargs) -> dict:
        """Update Serial module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.serial

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('serial')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_telemetry_config(self, **kwargs) -> dict:
        """Update Telemetry module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.telemetry

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('telemetry')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_store_forward_config(self, **kwargs) -> dict:
        """Update Store & Forward module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.store_forward

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('store_forward')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_external_notification_config(self, **kwargs) -> dict:
        """Update External Notification module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.external_notification

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('external_notification')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_range_test_config(self, **kwargs) -> dict:
        """Update Range Test module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.range_test

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('range_test')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_neighbor_info_config(self, **kwargs) -> dict:
        """Update Neighbor Info module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.neighbor_info

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('neighbor_info')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_detection_sensor_config(self, **kwargs) -> dict:
        """Update Detection Sensor module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.detection_sensor

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('detection_sensor')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_audio_config(self, **kwargs) -> dict:
        """Update Audio module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.audio

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('audio')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_remote_hardware_config(self, **kwargs) -> dict:
        """Update Remote Hardware module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.remote_hardware

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('remote_hardware')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_ambient_lighting_config(self, **kwargs) -> dict:
        """Update Ambient Lighting module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.ambient_lighting

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('ambient_lighting')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_paxcounter_config(self, **kwargs) -> dict:
        """Update Paxcounter module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.paxcounter

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('paxcounter')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_canned_message_config(self, **kwargs) -> dict:
        """Update Canned Message module configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()
            config = node.moduleConfig.canned_message

            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            node.writeConfig('canned_message')
            return {'success': True, 'reboot_required': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_channels_config(self) -> dict:
        """Get all channel configurations"""
        try:
            node = self._get_local_node()
            channels_data = []

            for i in range(len(node.channels)):
                ch = node.channels[i]
                role = self._safe_get(ch, 'role', 0)

                channels_data.append({
                    'index': i,
                    'role': role,
                    'role_name': self.CHANNEL_ROLES.get(role, 'UNKNOWN'),
                    'role_options': self._enum_to_options(self.CHANNEL_ROLES, role),
                    'name': self._safe_get(ch.settings, 'name', ''),
                    'psk': ch.settings.psk.hex() if ch.settings.psk else '',
                    'psk_bits': 8 * len(ch.settings.psk) if ch.settings.psk else 0,
                    'uplink_enabled': self._safe_get(ch.settings, 'uplink_enabled', False),
                    'downlink_enabled': self._safe_get(ch.settings, 'downlink_enabled', False),
                })

            return {
                'success': True,
                'channels': channels_data
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_channel_config(self, channel_index: int, **kwargs) -> dict:
        """Update a specific channel configuration"""
        try:
            node = self._get_local_node()
            node.ensureSessionKey()

            if channel_index < 0 or channel_index >= len(node.channels):
                return {'success': False, 'error': f'Invalid channel index: {channel_index}'}

            channel = node.channels[channel_index]

            # Update role if provided
            if 'role' in kwargs:
                channel.role = kwargs['role']

            # Update settings
            if 'name' in kwargs:
                channel.settings.name = kwargs['name']

            if 'psk' in kwargs:
                # Convert hex string to bytes
                psk_hex = kwargs['psk']
                if psk_hex:
                    channel.settings.psk = bytes.fromhex(psk_hex)

            if 'uplink_enabled' in kwargs:
                channel.settings.uplink_enabled = kwargs['uplink_enabled']

            if 'downlink_enabled' in kwargs:
                channel.settings.downlink_enabled = kwargs['downlink_enabled']

            # Write the channel
            node.writeChannel(channel_index)

            return {'success': True, 'reboot_required': False}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def reboot_node(self) -> dict:
        """Reboot the Meshtastic node"""
        try:
            node = self._get_local_node()
            print('[CONFIG] Initiating node reboot...', flush=True)
            node.reboot()
            print('[CONFIG] Reboot command sent successfully. Connection will be lost temporarily.', flush=True)
            return {'success': True, 'message': 'Node is rebooting...'}
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            # These are expected when device reboots - connection is lost
            print(f'[CONFIG] Expected connection error during reboot: {e}', flush=True)
            return {'success': True, 'message': 'Node is rebooting (connection lost as expected)...'}
        except Exception as e:
            print(f'[CONFIG] Unexpected error during reboot: {e}', flush=True)
            return {'success': False, 'error': str(e)}
