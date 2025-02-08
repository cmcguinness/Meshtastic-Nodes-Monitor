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


# This prevents the Werkzeug logger from printing to the console all the requests we receive
if not Config().get('debug.http_logging', False):
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

app = Flask(__name__)

status = Status()

flash_message = None

@app.route('/')
def index():
    m = Mesh()
    voltage = m.node_data['deviceMetrics']['voltage']
    batt_level = m.node_data['deviceMetrics']['batteryLevel']
    firmware_version = m.node.metadata.firmware_version
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
        # print('Sending traceroute...', flush=True)
        Mesh().node.sendTraceRoute(dest, hopLimit, channelIndex=channelIndex)
    except Exception as e:
        l = logging.getLogger(__name__)
        l.info(f'TraceRoute EXCEPTION: {e}')
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

