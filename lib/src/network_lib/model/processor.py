import uuid


class Processor:
    def __init__(self, bandwidth, latency):
        self.uuid = uuid.uuid4()
        # TODO Delete the following line
        self.bandwidth = bandwidth
        self.latency = latency
