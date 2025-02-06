from lib.src.core.event import Event
from lib.src.core.handler import Handler
from lib.src.primitives.algorithms.ring import one_step_in_ring
from lib.src.primitives.algorithms.halving_doubling import one_step_in_halving_doubling
from lib.src.primitives.help_functions import count_steps
from lib.src.primitives.methods import Method


class ReduceScatterEvent(Event):
    def __init__(self, applying_time, handler, gpu_cards, data_size, method, steps=None, delta=None):
        super().__init__(applying_time, handler)
        self.gpu_cards = gpu_cards
        self.data_size = data_size
        self.method = method
        self.steps = count_steps(method, len(gpu_cards)) if steps is None else steps
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


class ReduceScatterHandler(Handler):
    def __init__(self, future_event_list):
        super().__init__(future_event_list)

    def do(self, event):
        if event.method == Method.RING:
            applying_time = one_step_in_ring(self, event)
            if event.steps == 1:
                return applying_time
            ring_handler = ReduceScatterHandler(self.future_event_list)
            self.future_event_list.add_event(
                ReduceScatterEvent(applying_time, ring_handler,
                                   event.gpu_cards, event.data_size, event.method, event.steps - 1)
            )
        elif event.method == Method.HALVING_DOUBLING:
            applying_time = one_step_in_halving_doubling(self, event, event.delta)
            if event.steps == 1:
                return
            halving_handler = ReduceScatterHandler(self.future_event_list)
            next_delta = event.delta * 2
            self.future_event_list.add_event(
                ReduceScatterEvent(applying_time, halving_handler,
                                   event.gpu_cards, event.data_size,
                                   event.method, event.steps - 1,
                                   delta=next_delta)
            )
        elif event.method == Method.TREE:
            pass
        elif event.method == Method.BRUCK:
            pass
        else:
            pass
