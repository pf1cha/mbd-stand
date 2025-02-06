import uuid


class Processor:
    def __init__(self, bandwidth, latency):
        self.uuid = uuid.uuid4()
        self.bandwidth = bandwidth
        self.latency = latency
