import time
from mesh import Mesh
from utilities import *

class NodeData:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NodeData, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.raw_data = None
        self.data = None
        self.lasttime = None
        self.refresh_frequency = 300  # 5 minutes

    def refresh_data(self):

        self.lasttime = time.time()
        self.raw_data = Mesh().node.nodes
        self.flatten_data()

    def flatten_data(self):
        keys = []
        for node_id, node in self.raw_data.items():
            for key in node.keys():
                if key not in keys:
                    if isinstance(node[key], dict):
                        for subkey in node[key].keys():
                            keys.append(f"{key}.{subkey}")
                    else:
                        keys.append(key)

        self.data = []
        for node_id, node in self.raw_data.items():
            node_data = {'id': node_id}
            for key in keys:
                if '.' in key:
                    subkey = key.split('.')
                    node_data[key] = node.get(subkey[0], {}).get(subkey[1], None)
                else:
                    node_data[key] = node.get(key, None)
            self.data.append(node_data)

    def lookup_by_id(self, node_id):
        try:
            self.refresh_data()
            for node in self.data:
                if node['id'] == node_id:
                    node['distance'] = int(calculate_distance((node.get('position.latitude'),node.get('position.longitude'))))
                    if node.get('deviceMetrics.uptimeSeconds'):
                        node['formatted_uptime'] = format_seconds(node.get('deviceMetrics.uptimeSeconds'))
                    else:
                        node['formatted_uptime'] = ''
                    # print(str(node).replace('\n', ' '))  # Debugging code
                    return node

            print(f'{node_id} not found.')
            return None
        except Exception as e:
            print(e, flush=True)
            raise e

