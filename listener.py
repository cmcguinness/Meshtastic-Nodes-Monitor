from mesh import Mesh
from utilities import *
# noinspection PyPackageRequirements
from pubsub import pub
from message import Message
import time
import os
from config import Config


class Listener():
    def __init__(self):
        retries = 4
        while retries:
            try:
                self.mesh = Mesh()
                retries = 0
            except Exception as e:
                retries = retries - 1
                if retries == 0:
                    raise e
                else:
                    print('Connection error, retrying in 5')
                    time.sleep(5)

        config = Config()
        if not config.get('data.append_log', False):
            with open('packetlog.txt', 'w') as f:
                f.write(get_datestamp() + ': Initialized\n')
        else:
            with open('packetlog.txt', 'a') as f:
                f.write(get_datestamp() + ': Restarted\n')

        pub.subscribe(self.on_receive, "meshtastic.receive")
        pub.subscribe(self.on_disconnect, "meshtastic.connection.lost")

        print('Listener initialized')

    def __del__(self):
        print("Listener is being destroyed")

    def on_receive(self, packet: dict, interface):
        try:
            msg = Message(interface, packet)
            msg.handle_message()
        except Exception as e:
            print(f'Error processing packet: {e}', flush=True)
            with open('packetlog.txt', 'a') as f:
                f.write(f'{get_datestamp()}: ERROR processing packet: {e}\n')
                f.write(f'{get_datestamp()}: Packet was: {packet}\n')

    def on_disconnect(self):
        print('Disconnected from Mesh')
        self.mesh.reconnect()
        print('Reconnected to Mesh')
