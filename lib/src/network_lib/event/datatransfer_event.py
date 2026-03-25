from lib.src.core.event import Event


class DataTransferEvent(Event):
    # TODO get rid off class variables like source_id, target_id, latency, bandwidth. They are temporary solutions.
    def __init__(self, applying_time, handler, source, target,
                 data_size, bandwidth, latency, parent_uuid=None, parent_type=None):
        super().__init__(applying_time, handler)
        self.source = str(source.uuid)
        self.source_id = source.id
        self.target = str(target.uuid)
        self.target_id = target.id
        self.data_size = data_size
        self.bandwidth = bandwidth
        self.latency = latency
        self.time = data_size / bandwidth + latency
        self.parent_uuid = parent_uuid
        self.parent_type = parent_type

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "handler_type": type(self.handler).__name__,
            "applying_time": self.applying_time,
            "transfer_time": self.time,
            "gpu_source": self.source,
            "gpu_destination": self.target,
            "gpu_source_id": self.source_id,
            "gpu_destination_id": self.target_id,
            "data_size": self.data_size,
            "bandwidth": self.bandwidth,
            "latency": self.latency,
            "parent_uuid": self.parent_uuid,
            "parent_type": self.parent_type,
        }
