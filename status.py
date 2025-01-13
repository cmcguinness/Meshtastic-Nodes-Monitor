from pydantic import BaseModel
from config import Config
import pickle
import os

class MSG(BaseModel):
    msg_time: str
    msg_fromId: str
    msg_from: str
    msg_to: str
    msg_channel: str
    msg_text: str


class MSGs():
    def __init__(self):
        self.messages : list[MSG] = []
        self.msg_limit = Config().get('data.max_messages', 1024)

    def add(self, dt, mf, mto, ch, mtxt, from_id):
        msg = MSG(msg_time = dt, msg_from = mf, msg_to = mto, msg_channel = ch, msg_text = mtxt, msg_fromId = from_id)

        if len(self.messages) == self.msg_limit:
            del self.messages[-1]

        # insert msg at the front of self.messages
        self.messages.insert(0, msg)

    def get_msgs(self, rowmax):
        msgs = []
        for msg in self.messages:
            msgs.append(
                {
                    "datetime": msg.msg_time,
                    "id": msg.msg_fromId,
                    "from": msg.msg_from,
                    "to": msg.msg_to,
                    "channel": msg.msg_channel,
                    "message": msg.msg_text
                }
            )

        return msgs[:rowmax]


class PKT(BaseModel):
    pk_time: str
    pk_from: str
    pk_id: str
    pk_hops: str
    pk_rssi: str
    pk_type: str
    pk_info: str

class PKTs():
    def __init__(self):
        self.packets : list[PKT] = []
        self.msg_limit = Config().get('data.max_packets', 1024)

    def add(self, pti, pf, ph, pr, pty, pi, pid):
        pkt = PKT(pk_time = pti, pk_from=pf, pk_id=pid, pk_hops=str(ph), pk_rssi=str(pr), pk_type=pty, pk_info=pi)

        if len(self.packets) == self.msg_limit:
            del self.packets[-1]

        # insert msg at the front of self.messages
        self.packets.insert(0, pkt)

    def get_pkts(self, rowmax):
        pkts = []
        for pkt in self.packets:
            pkts.append(
                {
                    "datetime": pkt.pk_time,
                    "id": pkt.pk_id,
                    "name": pkt.pk_from,
                    "hops": pkt.pk_hops,
                    "rssi": pkt.pk_rssi,
                    "type": pkt.pk_type,
                    "information": pkt.pk_info
                }
            )

        return pkts[:rowmax]


class Status:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Status, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            print("Status Initializing")
            self.config = Config()
            self.counts = None
            self.messages = None
            self.packets = None
            if self.config.get('data.persist_data'):
                if os.path.exists('persisted_data.pkl'):
                    with open('persisted_data.pkl', 'rb') as f:
                        data = pickle.load(f)

                    self.counts = data.get('counts')
                    self.messages = data.get('messages')
                    self.packets = data.get('packets')

            if self.counts is None:
                self.counts = {'Total': 0, 'Text': 0, 'Telemetry': 0, 'Position': 0, 'NodeInfo': 0, 'Other': 0}
            if self.packets is None:
                self.packets = PKTs()
            if self.messages is None:
                self.messages = MSGs()

        self.initialized = True

    def persist(self):
        if self.config.get('data.persist_data'):
            data = { 'counts': self.counts, 'messages': self.messages, 'packets': self.packets}
            with open('persisted_data.pkl', 'wb') as f:
                pickle.dump(data, f)

    def get_counts(self):
        r = {'columns': [key for key in self.counts], 'values': [self.counts[key] for key in self.counts]}
        return r

    def get_messages(self, rowmax):
        return self.messages.get_msgs(rowmax)

    def get_packets(self, rowmax):
        return self.packets.get_pkts(rowmax)

    def add_msg(self, dt, mf, mto, ch, mtxt, id):
        self.messages.add(dt, mf, mto, ch, mtxt, id)
        self.persist()

    def add_pkt(self, pti, pf, ph, pr, pty, pi, pid):
        self.packets.add(pti, pf, ph, pr, pty, pi, pid)
        self.persist()

    def add_count(self, name):
        self.counts[name] = 1 + self.counts.get(name, 0)
        self.counts['Total'] = 1 + self.counts.get('Total', 0)
        self.persist()



