import uuid


class GraphicCard:
    def __init__(self, bandwidth, latency):
        self.id = uuid.uuid4()
        self.bandwidth = bandwidth
        self.latency = latency
