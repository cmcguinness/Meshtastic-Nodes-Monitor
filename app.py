import socket
import os
from flask import Flask, render_template, jsonify, request, abort
from status import Status
from listener import Listener
from mesh import Mesh
from nodedata import NodeData
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


app = Flask(__name__)

status = Status()

@app.route('/')
def index():
    m = Mesh()
    return render_template('index.html', name=m.full_name)


@app.route('/api/updates')
def get_updates():
    # Demo data - replace with your actual data source
    summary_data = status.get_counts()

    messages_data =  status.get_messages()

    packets_data = status.get_packets()

    return jsonify({
        "summary": summary_data,
        "messages": messages_data,
        "packets": packets_data
    })


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
    app.run(port=port, debug=False)

