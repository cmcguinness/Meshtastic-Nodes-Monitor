#!/usr/bin/env python3
"""
Fix hop limit mismatch on node 192.168.5.50
"""

from meshtastic.tcp_interface import TCPInterface

def update_hop_limit(address, new_hop_limit):
    """Update the hop limit on a node"""
    print(f"\nConnecting to {address}...")
    try:
        interface = TCPInterface(hostname=address)
        local_node = interface.localNode

        # Get current hop limit
        current_hop_limit = local_node.localConfig.lora.hop_limit
        print(f"Current hop limit: {current_hop_limit}")

        if current_hop_limit == new_hop_limit:
            print(f"✓ Hop limit is already set to {new_hop_limit}")
            interface.close()
            return True

        # Update hop limit
        print(f"Updating hop limit to {new_hop_limit}...")
        local_node.localConfig.lora.hop_limit = new_hop_limit

        # Write the configuration
        print("Writing configuration...")
        local_node.writeConfig('lora')

        print(f"✓ Successfully updated hop limit from {current_hop_limit} to {new_hop_limit}")
        print("\nNote: The change will take effect after the node reboots.")
        print("The node should reboot automatically, but you may need to wait ~30 seconds.")

        interface.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_hop_limit("192.168.5.50", 6)
    exit(0 if success else 1)
