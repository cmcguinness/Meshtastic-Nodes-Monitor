#!/usr/bin/env python3
"""
Compare configurations between two Meshtastic nodes to identify mismatches
"""

import sys
from meshtastic.tcp_interface import TCPInterface

def get_node_config(address):
    """Connect to a node and retrieve its configuration"""
    print(f"\nConnecting to {address}...")
    try:
        interface = TCPInterface(hostname=address)
        local_node = interface.localNode
        node_num = local_node.nodeNum
        node_id = f"!{node_num:08x}"

        # Get user info
        node_data = interface.nodes.get(node_id, {})
        user_info = node_data.get('user', {})

        config = {
            'address': address,
            'node_id': node_id,
            'long_name': user_info.get('longName', 'Unknown'),
            'short_name': user_info.get('shortName', 'Unknown'),
            'hw_model': user_info.get('hwModel', 'Unknown'),

            # LoRa settings
            'lora': {
                'region': local_node.localConfig.lora.region,
                'modem_preset': local_node.localConfig.lora.modem_preset,
                'hop_limit': local_node.localConfig.lora.hop_limit,
                'tx_enabled': local_node.localConfig.lora.tx_enabled,
                'tx_power': local_node.localConfig.lora.tx_power,
                'use_preset': local_node.localConfig.lora.use_preset,
            },

            # Channels
            'channels': []
        }

        # Get channel info
        for i, ch in enumerate(local_node.channels):
            if ch.role != 0:  # Skip disabled channels
                config['channels'].append({
                    'index': i,
                    'role': ch.role,
                    'name': ch.settings.name,
                    'psk': ch.settings.psk.hex() if ch.settings.psk else '',
                })

        interface.close()
        return config
    except Exception as e:
        print(f"Error connecting to {address}: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_configs(config1, config2):
    """Compare two node configurations and report differences"""
    print("\n" + "="*70)
    print("CONFIGURATION COMPARISON")
    print("="*70)

    print(f"\nNode 1: {config1['long_name']} ({config1['short_name']}) - {config1['address']}")
    print(f"  ID: {config1['node_id']}")

    print(f"\nNode 2: {config2['long_name']} ({config2['short_name']}) - {config2['address']}")
    print(f"  ID: {config2['node_id']}")

    # Compare LoRa settings
    print("\n" + "-"*70)
    print("LoRa Configuration:")
    print("-"*70)

    lora_fields = {
        'region': 'Region',
        'modem_preset': 'Modem Preset',
        'hop_limit': 'Hop Limit',
        'tx_enabled': 'TX Enabled',
        'tx_power': 'TX Power',
        'use_preset': 'Use Preset',
    }

    mismatches = []

    for field, label in lora_fields.items():
        val1 = config1['lora'][field]
        val2 = config2['lora'][field]

        if val1 != val2:
            print(f"⚠️  MISMATCH - {label}:")
            print(f"    Node 1: {val1}")
            print(f"    Node 2: {val2}")
            mismatches.append(label)
        else:
            print(f"✓  {label}: {val1}")

    # Compare channels
    print("\n" + "-"*70)
    print("Channel Configuration:")
    print("-"*70)

    # Check if both have same number of active channels
    if len(config1['channels']) != len(config2['channels']):
        print(f"⚠️  MISMATCH - Number of channels:")
        print(f"    Node 1: {len(config1['channels'])} channels")
        print(f"    Node 2: {len(config2['channels'])} channels")
        mismatches.append('Channel Count')

    # Compare each channel
    for i in range(min(len(config1['channels']), len(config2['channels']))):
        ch1 = config1['channels'][i]
        ch2 = config2['channels'][i]

        print(f"\nChannel {ch1['index']}:")

        if ch1['role'] != ch2['role']:
            print(f"  ⚠️  MISMATCH - Role: {ch1['role']} vs {ch2['role']}")
            mismatches.append(f'Channel {i} Role')

        if ch1['psk'] != ch2['psk']:
            print(f"  ⚠️  MISMATCH - PSK differs!")
            print(f"    Node 1 PSK: {ch1['psk']}")
            print(f"    Node 2 PSK: {ch2['psk']}")
            mismatches.append(f'Channel {i} PSK')
        else:
            print(f"  ✓  PSK: {ch1['psk']}")

        if ch1['name'] != ch2['name']:
            print(f"  ⚠️  Name differs: '{ch1['name']}' vs '{ch2['name']}' (cosmetic only)")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    if mismatches:
        print(f"\n⚠️  Found {len(mismatches)} configuration mismatch(es):")
        for mismatch in mismatches:
            print(f"  - {mismatch}")
        print("\nThese mismatches may prevent the nodes from communicating properly!")
    else:
        print("\n✓  All critical settings match. Nodes should be able to communicate.")
        print("\nIf they still can't see each other, check:")
        print("  - Physical distance and obstacles")
        print("  - Antenna connections")
        print("  - Power levels")
        print("  - Interference from other devices")

    return mismatches

if __name__ == "__main__":
    # Get configurations from both nodes
    config1 = get_node_config("192.168.5.50")
    config2 = get_node_config("192.168.5.51")

    if config1 and config2:
        mismatches = compare_configs(config1, config2)
        sys.exit(1 if mismatches else 0)
    else:
        print("\n❌ Failed to retrieve configuration from one or both nodes")
        sys.exit(2)
