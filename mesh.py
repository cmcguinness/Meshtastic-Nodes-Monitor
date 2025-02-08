from meshtastic.tcp_interface import TCPInterface
from meshtastic.serial_interface import SerialInterface
from meshtastic.mesh_interface import MeshInterface
from meshtastic import BROADCAST_ADDR
import sys

from nodedata import NodeData

#   If using TCP/IP
DEFAULT_DEVICE = '192.168.5.50'

#   If using Serial
# DEFAULT_DEVICE = "/dev/cu.usbserial-0001"

class Mesh:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Mesh, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        if len(sys.argv) > 1:
            self.device = sys.argv[1]
        else:
            self.device = DEFAULT_DEVICE

        print(f'Initializing mesh at {self.device}')

        # Mac/Linux Specific, not sure what Windows does...
        if self.device.startswith('/'):
            self.node = SerialInterface(self.device)
        else:
            self.node = TCPInterface(hostname=self.device)

        self.mi = MeshInterface()

        ch = self.node.localNode.channels

        self.channels = []
        roles = ['', 'Primary', 'Secondary']
        for i in range(len(ch)):
            if ch[i].role == 0:
                continue

            self.channels.append({
                'index': i,
                'name': ch[i].settings.name,
                'psk': ch[i].settings.psk,
                'psk_bits': 8*len(ch[i].settings.psk),
                'role': roles[ch[i].role]
            })

        print('Local Node Information\n')

        self.nodenum = f'!{self.node.localNode.nodeNum:08x}'
        self.node_data = self.node.nodes[self.nodenum]
        self.full_name = self.node_data['user']['longName'] + ' at ' + self.device

        print(f'Connected to node {self.nodenum}: {self.node_data['user']['longName']} ({self.node_data['user']['shortName']}), Running on a {self.node_data['user']['hwModel']}')
        print('')
        print('Channels')
        for ch in self.channels:
            print(f'{ch["index"]}  {ch["name"]:12}  {ch["role"]:9}  PSK Bits {8*len(ch["psk"])}')

        self._initialized = True


    def reconnect(self):
        self.node = TCPInterface(hostname=self.device)

    def reset(self):
        self._instance = None

    def send_dm(self, dest, message):
        from nodedata import NodeData

        if not dest.startswith('!'):
            dest = '!' + dest

        item_data = NodeData().lookup_by_id(dest)

        if item_data is None:
            return 'Node not found'

        try:
            # Send the message
            r = self.node.sendText(message, dest)
            return None
        except Exception as e:
            return str(e)

    def send_channel(self, dest, message):

        try:
            # Send the message
            r = self.node.sendText(message, BROADCAST_ADDR, channelIndex=int(dest))
            return None
        except Exception as e:
            return str(e)


