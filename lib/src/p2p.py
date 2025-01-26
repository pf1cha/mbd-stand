from lib.src.event import Event
from lib.src.handler import Handler


class DataTransferEvent(Event):
    def __init__(self, applying_time, handler, source, destination, data_size):
        super().__init__(applying_time, handler)
        self.source = str(source.id)
        self.destination = str(destination.id)
        self.data_size = data_size
        self.time = data_size / source.bandwidth

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "handler_type": type(self.handler).__name__,
            "applying_time": self.applying_time,
            "transfer_time": self.time,
            "gpu_source": self.source,
            "gpu_destination": self.destination,
            "data_size": self.data_size,
        }


class DataTransferHandler(Handler):
    def __init__(self, future_event_list, clock):
        super().__init__(future_event_list, clock)

    def do(self, event):
        return