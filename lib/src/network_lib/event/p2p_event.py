from lib.src.core.event import Event

class P2PStepEvent(Event):
    def __init__(self, applying_time, handler, processors, topology, data_size, steps=None, crt_step=None):
        super().__init__(applying_time, handler)
        self.processors = processors
        self.topology = topology
        self.data_size = data_size
        self.steps = 2 * (len(self.processors) - 1) if steps is None else steps
        self.crt_step = 1 if crt_step is None else crt_step

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "handler_type": type(self.handler).__name__,
            "applying_time": self.applying_time,
            "data_size": self.data_size,
        }