from lib.src.core.event import Event
from lib.src.network_lib.utils.help_functions import count_steps


class ReduceScatterStepEvent(Event):
    def __init__(self, applying_time, handler, network, data_size, method, steps=None, delta=None):
        super().__init__(applying_time, handler)
        self.network = network
        self.data_size = data_size
        self.method = method
        self.steps = count_steps(method, len(network.processors)) if steps is None else steps
        self.delta = 1 if delta is None else delta

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "handler_type": type(self.handler).__name__,
            "method": self.method.name,
            "applying_time": self.applying_time,
            "data_size": self.data_size,
        }
