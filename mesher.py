import socket
import os
from flask import Flask, render_template, jsonify, request, abort
from status import Status
from listener import Listener
from mesh import Mesh
from nodedata import NodeData
import logging
import threading
from config import Config
from nodeconfig import NodeConfig


# This prevents the Werkzeug logger from printing to the console all the requests we receive
if not Config().get('debug.http_logging', False):
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

app = Flask(__name__)

status = Status()

flash_message = None
flash_message_lock = threading.Lock()

@app.route('/')
def index():
    m = Mesh()
    device_metrics = m.node_data.get('deviceMetrics', {})
    voltage = device_metrics.get('voltage', 'N/A')
    batt_level = device_metrics.get('batteryLevel', 'N/A')
    firmware_version = m.node.metadata.firmware_version if m.node.metadata else 'Unknown'
    return render_template('index.html', name=m.full_name, voltage=voltage, batt_level=batt_level, version=firmware_version,
                           channels=m.channels)


@app.route('/api/updates')
def get_updates():
    rowmax =int(request.args.get('rowmax'))

    # Demo data - replace with your actual data source
    summary_data = status.get_counts()

    messages_data = status.get_messages(rowmax)

    packets_data = status.get_packets(rowmax)

    nodes_data = NodeData().get_nodes()[:rowmax]

    global flash_message
    with flash_message_lock:
        f = flash_message
        flash_message = None
    return jsonify({
        "summary": summary_data,
        "messages": messages_data,
        "packets": packets_data,
        "nodes": nodes_data,
        "flash": f
    })

# sendTraceRoute waits for a response.  We don't care, we'll see the packet
# coming back.  So we'll stick this in a thread so the rest of the app can
# get on with things..
def send_trace_route_in_thread(dest, hopLimit, channelIndex):
    global flash_message
    try:
        print(f'Sending traceroute ({dest} {hopLimit} {channelIndex}) ({type(dest)})', flush=True)
        Mesh().node.sendTraceRoute(dest, hopLimit, channelIndex=channelIndex)
    except Exception as e:
        l = logging.getLogger(__name__)
        l.info(f'TraceRoute EXCEPTION: {e}')
        with flash_message_lock:
            flash_message = 'Trace Route Failed'

    # print('Traceroute finished', flush=True)


@app.route('/api/traceroute')
def do_traceroute():
    # Get the ID from the request arguments
    item_id = request.args.get('id')
    if not item_id:
        abort(400, description="Missing required 'id' parameter")

    node = NodeData().lookup_by_id('!' + item_id)

    if node is None:
        node = {}

    hopLimit = 4
    dest = int(item_id, 16)
    if 'hopsAway' in node and node['hopsAway']:
        hopLimit = min(7,max(node['hopsAway']+1, hopLimit))
    print(f'Trace Route to {item_id} with {hopLimit} hops')
    channelIndex = 0

    thread = threading.Thread(target=send_trace_route_in_thread, args=(dest, hopLimit, channelIndex))
    thread.start()
    return 'Trace Route sent.'

@app.route('/api/details')
def get_details():
    # Get the ID from the request arguments
    item_id = request.args.get('id')
    if not item_id:
        abort(400, description="Missing required 'id' parameter")

    try:
        # Fetch the data for the given ID
        # Replace this with your actual data fetching logic
        item_data = NodeData().lookup_by_id('!' + item_id)

        return render_template('details.html', data = item_data)

    except ValueError as e:
        abort(404, description=f"Item {item_id} not found")
    except Exception as e:
        print(e, flush=True)
        abort(500, description=f"Error fetching details: {str(e)}")


@app.route('/api/dm', methods=['GET'])
def send_dm():
    # Get the ID from the request arguments
    item_id = request.args.get('id')
    if not item_id:
        abort(400, description="Missing required 'id' parameter")

    # Get the message from the request arguments
    message = request.args.get('message')
    if not message:
        abort(400, description="Missing required 'message' parameter")

    err = Mesh().send_dm(item_id, message)

    if err is None:
        return 'Message sent'

    return err

@app.route('/api/sendchannel', methods=['GET'])
def send_channel():
    # Get the ID from the request arguments
    item_id = request.args.get('id')
    if not item_id:
        abort(400, description="Missing required 'id' parameter")

    # Get the message from the request arguments
    message = request.args.get('message')
    if not message:
        abort(400, description="Missing required 'message' parameter")

    err = Mesh().send_channel(item_id, message)

    if err is None:
        return 'Message sent'

    return err


@app.route('/api/localnode')
def get_local_node_info():
    """Return detailed information about the local node"""
    m = Mesh()

    # Basic node data
    node_data = m.node_data
    user = node_data.get('user', {})
    device_metrics = node_data.get('deviceMetrics', {})
    position = node_data.get('position', {})

    # Metadata from device
    metadata = m.node.metadata

    # Get role from device config (not user info)
    # Role is an integer: 0=CLIENT, 1=CLIENT_MUTE, 2=ROUTER, 3=ROUTER_CLIENT, etc.
    role_names = {
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
        10: 'TAK_TRACKER'
    }
    try:
        role_int = m.node.localNode.localConfig.device.role
        role = role_names.get(role_int, f'Unknown ({role_int})')
    except Exception as e:
        role = user.get('role', 'Unknown')

    # Connection info
    connection_type = 'Serial' if m.device.startswith('/') else 'TCP/IP'

    # Node count
    node_count = len(m.node.nodes)

    # Channel count
    channel_count = len(m.channels)

    info = {
        'nodeId': m.nodenum,
        'longName': user.get('longName', 'Unknown'),
        'shortName': user.get('shortName', 'Unknown'),
        'hwModel': user.get('hwModel', 'Unknown'),
        'role': role,
        'connectionType': connection_type,
        'connectionAddress': m.device,
        'firmwareVersion': metadata.firmware_version if metadata else 'Unknown',
        'deviceStateVersion': metadata.device_state_version if metadata else 'Unknown',
        'canShutdown': metadata.canShutdown if metadata else False,
        'hasWifi': metadata.hasWifi if metadata else False,
        'hasBluetooth': metadata.hasBluetooth if metadata else False,
        'hasEthernet': metadata.hasEthernet if metadata else False,
        'batteryLevel': device_metrics.get('batteryLevel', 'N/A'),
        'voltage': device_metrics.get('voltage', 'N/A'),
        'channelUtilization': device_metrics.get('channelUtilization', 'N/A'),
        'airUtilTx': device_metrics.get('airUtilTx', 'N/A'),
        'uptimeSeconds': device_metrics.get('uptimeSeconds', 0),
        'latitude': position.get('latitude'),
        'longitude': position.get('longitude'),
        'altitude': position.get('altitude'),
        'nodeCount': node_count,
        'channelCount': channel_count,
        'channels': m.channels
    }

    return render_template('localnode.html', data=info)


@app.route('/api/config')
def get_config_page():
    """Return the configuration page HTML"""
    nc = NodeConfig()
    all_config = nc.get_all_config()
    return render_template('nodeconfig.html', config=all_config)


@app.route('/api/config/all')
def get_all_config():
    """Return all configuration as JSON"""
    nc = NodeConfig()
    return jsonify(nc.get_all_config())


@app.route('/api/config/device', methods=['GET', 'POST'])
def handle_device_config():
    """Get or update device configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_device_config())
    else:
        data = request.get_json()
        result = nc.update_device_config(**data)
        return jsonify(result)


@app.route('/api/config/lora', methods=['GET', 'POST'])
def handle_lora_config():
    """Get or update LoRa configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_lora_config())
    else:
        data = request.get_json()
        result = nc.update_lora_config(**data)
        return jsonify(result)


@app.route('/api/config/position', methods=['GET', 'POST'])
def handle_position_config():
    """Get or update position configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_position_config())
    else:
        data = request.get_json()
        result = nc.update_position_config(**data)
        return jsonify(result)


@app.route('/api/config/power', methods=['GET', 'POST'])
def handle_power_config():
    """Get or update power configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_power_config())
    else:
        data = request.get_json()
        result = nc.update_power_config(**data)
        return jsonify(result)


@app.route('/api/config/network', methods=['GET', 'POST'])
def handle_network_config():
    """Get or update network configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_network_config())
    else:
        data = request.get_json()
        result = nc.update_network_config(**data)
        return jsonify(result)


@app.route('/api/config/display', methods=['GET', 'POST'])
def handle_display_config():
    """Get or update display configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_display_config())
    else:
        data = request.get_json()
        result = nc.update_display_config(**data)
        return jsonify(result)


@app.route('/api/config/bluetooth', methods=['GET', 'POST'])
def handle_bluetooth_config():
    """Get or update Bluetooth configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_bluetooth_config())
    else:
        data = request.get_json()
        result = nc.update_bluetooth_config(**data)
        return jsonify(result)


@app.route('/api/config/security', methods=['GET', 'POST'])
def handle_security_config():
    """Get or update security configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_security_config())
    else:
        data = request.get_json()
        result = nc.update_security_config(**data)
        return jsonify(result)


@app.route('/api/config/mqtt', methods=['GET', 'POST'])
def handle_mqtt_config():
    """Get or update MQTT module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_mqtt_config())
    else:
        data = request.get_json()
        result = nc.update_mqtt_config(**data)
        return jsonify(result)


@app.route('/api/config/serial', methods=['GET', 'POST'])
def handle_serial_config():
    """Get or update Serial module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_serial_config())
    else:
        data = request.get_json()
        result = nc.update_serial_config(**data)
        return jsonify(result)


@app.route('/api/config/telemetry', methods=['GET', 'POST'])
def handle_telemetry_config():
    """Get or update Telemetry module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_telemetry_config())
    else:
        data = request.get_json()
        result = nc.update_telemetry_config(**data)
        return jsonify(result)


@app.route('/api/config/store_forward', methods=['GET', 'POST'])
def handle_store_forward_config():
    """Get or update Store & Forward module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_store_forward_config())
    else:
        data = request.get_json()
        result = nc.update_store_forward_config(**data)
        return jsonify(result)


@app.route('/api/config/external_notification', methods=['GET', 'POST'])
def handle_external_notification_config():
    """Get or update External Notification module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_external_notification_config())
    else:
        data = request.get_json()
        result = nc.update_external_notification_config(**data)
        return jsonify(result)


@app.route('/api/config/range_test', methods=['GET', 'POST'])
def handle_range_test_config():
    """Get or update Range Test module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_range_test_config())
    else:
        data = request.get_json()
        result = nc.update_range_test_config(**data)
        return jsonify(result)


@app.route('/api/config/neighbor_info', methods=['GET', 'POST'])
def handle_neighbor_info_config():
    """Get or update Neighbor Info module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_neighbor_info_config())
    else:
        data = request.get_json()
        result = nc.update_neighbor_info_config(**data)
        return jsonify(result)


@app.route('/api/config/detection_sensor', methods=['GET', 'POST'])
def handle_detection_sensor_config():
    """Get or update Detection Sensor module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_detection_sensor_config())
    else:
        data = request.get_json()
        result = nc.update_detection_sensor_config(**data)
        return jsonify(result)


@app.route('/api/config/audio', methods=['GET', 'POST'])
def handle_audio_config():
    """Get or update Audio module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_audio_config())
    else:
        data = request.get_json()
        result = nc.update_audio_config(**data)
        return jsonify(result)


@app.route('/api/config/remote_hardware', methods=['GET', 'POST'])
def handle_remote_hardware_config():
    """Get or update Remote Hardware module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_remote_hardware_config())
    else:
        data = request.get_json()
        result = nc.update_remote_hardware_config(**data)
        return jsonify(result)


@app.route('/api/config/ambient_lighting', methods=['GET', 'POST'])
def handle_ambient_lighting_config():
    """Get or update Ambient Lighting module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_ambient_lighting_config())
    else:
        data = request.get_json()
        result = nc.update_ambient_lighting_config(**data)
        return jsonify(result)


@app.route('/api/config/paxcounter', methods=['GET', 'POST'])
def handle_paxcounter_config():
    """Get or update Paxcounter module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_paxcounter_config())
    else:
        data = request.get_json()
        result = nc.update_paxcounter_config(**data)
        return jsonify(result)


@app.route('/api/config/canned_message', methods=['GET', 'POST'])
def handle_canned_message_config():
    """Get or update Canned Message module configuration"""
    nc = NodeConfig()
    if request.method == 'GET':
        return jsonify(nc.get_canned_message_config())
    else:
        data = request.get_json()
        result = nc.update_canned_message_config(**data)
        return jsonify(result)


@app.route('/api/config/channels', methods=['GET'])
def get_channels():
    """Get all channel configurations"""
    nc = NodeConfig()
    return jsonify(nc.get_channels_config())


@app.route('/api/config/channel/<int:channel_index>', methods=['POST'])
def update_channel(channel_index):
    """Update a specific channel configuration"""
    nc = NodeConfig()
    data = request.get_json()
    result = nc.update_channel_config(channel_index, **data)
    return jsonify(result)


@app.route('/api/config/reboot', methods=['POST'])
def reboot_node():
    """Reboot the Meshtastic node"""
    nc = NodeConfig()
    result = nc.reboot_node()
    return jsonify(result)


#    ┌──────────────────────────────────────────────────────────┐
#    │                       Startup Code                       │
#    └──────────────────────────────────────────────────────────┘

#    ┌──────────────────────────────────────────────────────────┐
#    │                                                          │
#    │    On the Mac, port 5000, which is the default port,     │
#    │    is often busy.  So the first thing I need to do is    │
#    │    find a free port and use it instead.                  │
#    │                                                          │
#    └──────────────────────────────────────────────────────────┘

def find_free_port():
    # This is just some sort of magic incantation that works
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # Bind to an available port provided by the host.
        return s.getsockname()[1]  # Return the port number assigned.


#    ┌──────────────────────────────────────────────────────────┐
#    │                                                          │
#    │    This version of the Flask launch code will            │
#    │    automatically open a browser, saving you from         │
#    │    having to click.                                      │
#    └──────────────────────────────────────────────────────────┘
if __name__ == '__main__':
    listener = Listener()
    port = find_free_port()
    if os.name == 'nt':
        os.system(f'explorer "http:/127.0.0.1:{port}"')
    else:
        os.system(f'open http://127.0.0.1:{port}')

    print(f'To reopen browser, go to: http://127.0.0.1:{port}')
    app.run(port=port, debug=False)

