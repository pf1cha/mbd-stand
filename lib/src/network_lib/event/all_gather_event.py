from lib.src.core.event import Event
from lib.src.network_lib.helpers.help_functions import count_steps


class AllGatherEvent(Event):
    def __init__(self, applying_time, handler, processors, data_size, method, steps=None, delta=None):
        super().__init__(applying_time, handler)
        self.processors = processors
        self.data_size = data_size
        self.method = method
        self.steps = count_steps(method, len(processors)) if steps is None else steps
        self.delta = len(processors) // 2 if delta is None else delta

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "handler_type": type(self.handler).__name__,
            "method": self.method.name,
            "applying_time": self.applying_time,
            "data_size": self.data_size,
        }
