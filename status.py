from pydantic import BaseModel

class MSG(BaseModel):
    msg_time: str
    msg_from: str
    msg_to: str
    msg_channel: str
    msg_text: str


class MSGs():
    def __init__(self):
        self.messages : list[MSG] = []
        self.msg_limit = 256

    def add(self, dt, mf, mto, ch, mtxt):
        msg = MSG(msg_time = dt, msg_from = mf, msg_to = mto, msg_channel = ch, msg_text = mtxt)

        if len(self.messages) == self.msg_limit:
            del self.messages[-1]

        # insert msg at the front of self.messages
        self.messages.insert(0, msg)

    def get_msgs(self):
        msgs = []
        for msg in self.messages:
            msgs.append(
                {
                    "datetime": msg.msg_time,
                    "from": msg.msg_from,
                    "to": msg.msg_to,
                    "channel": msg.msg_channel,
                    "message": msg.msg_text
                }
            )

        return msgs


class PKT(BaseModel):
    pk_time: str
    pk_from: str
    pk_hops: str
    pk_rssi: str
    pk_type: str
    pk_info: str

class PKTs():
    def __init__(self):
        self.packets : list[PKT] = []
        self.msg_limit = 256

    def add(self, pti, pf, ph, pr, pty, pi):
        pkt = PKT(pk_time = pti, pk_from=pf, pk_hops=str(ph), pk_rssi=str(pr), pk_type=pty, pk_info=pi)

        if len(self.packets) == self.msg_limit:
            del self.packets[-1]

        # insert msg at the front of self.messages
        self.packets.insert(0, pkt)

    def get_pkts(self):
        pkts = []
        for pkt in self.packets:
            pkts.append(
                {
                    "datetime": pkt.pk_time,
                    "node": pkt.pk_from,
                    "hops": pkt.pk_hops,
                    "rssi": pkt.pk_rssi,
                    "type": pkt.pk_type,
                    "information": pkt.pk_info
                }
            )

        return pkts


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
            self.counts = {'Total': 0, 'Text': 0, 'Telemetry': 0, 'Position': 0, 'NodeInfo': 0, 'Other': 0}
            self.packets = PKTs()
            self.messages = MSGs()
        self.initialized = True

    def get_counts(self):
        r = {'columns': [key for key in self.counts], 'values': [self.counts[key] for key in self.counts]}
        return r

    def get_messages(self):
        return self.messages.get_msgs()

    def get_packets(self):
        return self.packets.get_pkts()

    def add_msg(self, dt, mf, mto, ch, mtxt):
        self.messages.add(dt, mf, mto, ch, mtxt)

    def add_pkt(self, pti, pf, ph, pr, pty, pi):
        self.packets.add(pti, pf, ph, pr, pty, pi)

    def add_count(self, name):
        self.counts[name] = 1 + self.counts.get(name, 0)
        self.counts['Total'] = 1 + self.counts.get('Total', 0)



