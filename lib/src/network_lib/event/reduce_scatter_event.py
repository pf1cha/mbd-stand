from lib.src.core.event import Event
from lib.src.network_lib.utils.help_functions import count_steps


# This class implements the collective operation of Reduce Scatter.
# Network - the network on which the operation is performed.
# Data size - the total size of the data being scattered across the processors in the given network.
# Method - the method used for the Reduce Scatter operation (e.g., RING, HALVING_DOUBLING).
# Notice Halving-Doubling method for Reduce Scatter is a Recursive-Halving.
# Steps - the remaining steps to complete the Reduce Scatter operation.
# At the beginning, it is calculated based on the method and the number of processors.
# Delta - ...


class ReduceScatterStepEvent(Event):
    def __init__(self, applying_time, handler, network, data_size, method, steps=None, delta=None, crt_step=None):
        super().__init__(applying_time, handler)
        self.network = network
        self.data_size = data_size
        self.method = method
        self.steps = count_steps(method, len(network.processors)) if steps is None else steps
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
