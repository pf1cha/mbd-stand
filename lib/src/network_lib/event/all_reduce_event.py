from lib.src.core.event import Event
from lib.src.network_lib.utils.help_functions import count_steps


class AllReduceStepEvent(Event):
    def __init__(self, applying_time, handler, processors, topology, data_size, method, steps=None, delta=None, crt_step=None):
        super().__init__(applying_time, handler)
        self.processors = processors
        self.topology = topology
        self.data_size = data_size
        self.method = method
        self.steps = 2 * count_steps(method, len(processors)) if steps is None else steps
        self.delta = 1 if delta is None else delta
        self.crt_step = 1 if crt_step is None else crt_step

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "handler_type": type(self.handler).__name__,
            "method": self.method.name,
            "applying_time": self.applying_time,
            "data_size": self.data_size,
        }
