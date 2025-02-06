from lib.src.core.event import Event
from lib.src.core.handler import Handler


class DataTransferEvent(Event):
    def __init__(self, applying_time, handler, source, target, data_size):
        super().__init__(applying_time, handler)
        self.source = str(source.uuid)
        self.target = str(target.uuid)
        self.data_size = data_size
        # TODO add latency here
        self.time = data_size / source.bandwidth

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "handler_type": type(self.handler).__name__,
            "applying_time": self.applying_time,
            "transfer_time": self.time,
            "gpu_source": self.source,
            "gpu_destination": self.target,
            "data_size": self.data_size,
        }


class DataTransferHandler(Handler):
    def __init__(self, future_event_list):
        super().__init__(future_event_list)

    def do(self, event):
        return