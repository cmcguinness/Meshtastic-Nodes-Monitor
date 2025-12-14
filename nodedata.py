import time
from datetime import datetime
from threading import Lock
from utilities import calculate_distance, format_seconds
_lock = Lock()

class NodeData:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NodeData, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.raw_data = None
        self.data = None
        self.lasttime = None
        self.refresh_frequency = 300  # 5 minutes
        self._initialized = True

    def refresh_data(self, force=False):
        from mesh import Mesh
        # Only refresh if cache expired or forced
        if not force and self.lasttime is not None:
            if time.time() - self.lasttime < self.refresh_frequency:
                return  # Use cached data
        self.lasttime = time.time()
        self.raw_data = Mesh().node.nodes
        self.flatten_data()

    def flatten_data(self):
        keys = []
        with _lock:
            for node_id, node in self.raw_data.items():
                for key in node.keys():
                    if key not in keys:
                        if isinstance(node[key], dict):
                            for subkey in node[key].keys():
                                keys.append(f"{key}.{subkey}")
                        else:
                            keys.append(key)

            self.data = []
            rd = self.raw_data.copy()
            for node_id, node in rd.items():
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
                    node['distance'] = int(calculate_distance((node.get('position.latitude'), node.get('position.longitude'))))
                    if node.get('deviceMetrics.uptimeSeconds'):
                        node['formatted_uptime'] = format_seconds(node.get('deviceMetrics.uptimeSeconds'))
                    else:
                        node['formatted_uptime'] = ''
                    # print(str(node).replace('\n', ' '))  # Debugging code
                    return node

            # print(f'{node_id} not found.')  # Debugging code
            return None
        except Exception as e:
            print(e, flush=True)
            raise e

    def get_nodes(self):
        self.refresh_data()
        nodes = []
        mapping = [
            ('id', 'id'),
            ('hopsAway', 'hopsAway'),
            ('publicKey', 'publicKey'),
            ('latitude', 'position.latitude'),
            ('longitude', 'position.longitude'),
            ('altitude', 'position.altitude'),
            ('hwModel', 'user.hwModel')
        ]

        for node in self.data:
            ndata = {}
            for m in mapping:
                ndata[m[0]] = node.get(m[1])
            name = node['id']
            probe = node.get('user.shortName')
            if probe:
                name = probe
            probe = node.get('user.longName')
            if probe:
                name = probe + '[' + name + ']'
            ndata['name'] = name

            if node.get('position.latitude') and node.get('position.longitude'):
                lat = node.get('position.latitude')
                long = node.get('position.longitude')
                ndata['distance'] = f'{calculate_distance((lat, long)):.2f}  km'
            else:
                ndata['distance'] = 'Unknown'

            if node.get('lastHeard'):
                ndata['lastHeard'] = datetime.fromtimestamp(node.get('lastHeard')).strftime("%Y-%m-%d %H:%M:%S")
            else:
                ndata['lastHeard'] = '0000'

            nodes.append(ndata)

        # Sort nodes by nodes['lastHeard']
        nodes = sorted(nodes, key=lambda x: x['lastHeard'], reverse=True)

        # Hack to make unknown go to the bottom

        for n in nodes:
            if n['lastHeard'] == '0000':
                n['lastHeard'] = 'Unknown'

        return nodes


__all__ = ['NodeData']
