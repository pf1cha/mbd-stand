from lib.src.event import Event
from lib.src.handler import Handler
from lib.src.primitives.algorithms.ring import one_step_in_ring
from lib.src.primitives.algorithms.halving_doubling import one_step_in_halving_doubling
from lib.src.primitives.help_functions import count_steps
from lib.src.primitives.methods import Method
from numpy import log2


class AllReduceEvent(Event):
    def __init__(self, applying_time, handler, gpu_cards, data_size, method, steps=None, delta=None):
        super().__init__(applying_time, handler)
        self.gpu_cards = gpu_cards
        self.data_size = data_size
        self.method = method
        self.steps = 2 * count_steps(method, len(gpu_cards)) if steps is None else steps
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


class AllReduceHandler(Handler):
    def __init__(self, future_event_list, clock):
        super().__init__(future_event_list, clock)

    def do(self, event):
        if event.method == Method.RING:
            # Change the first index of the ring when the AllGather starts
            applying_time = one_step_in_ring(self, event)
            if event.steps == 1:
                return applying_time
            ring_handler = AllReduceHandler(self.future_event_list, self.clock)
            self.future_event_list.add_event(
                AllReduceEvent(applying_time, ring_handler,
                               event.gpu_cards, event.data_size, event.method, event.steps - 1)
            )
        elif event.method == Method.HALVING_DOUBLING:
            if event.steps > log2(len(event.gpu_cards)):
                applying_time = one_step_in_halving_doubling(self, event, event.delta)
                halving_handler = AllReduceHandler(self.future_event_list, self.clock)
                next_delta = event.delta * 2 if 2 * event.delta != len(event.gpu_cards) else event.delta
                self.future_event_list.add_event(
                    AllReduceEvent(applying_time, halving_handler,
                                   event.gpu_cards, event.data_size,
                                   event.method, event.steps - 1,
                                   delta=next_delta)
                )
            else:
                applying_time = one_step_in_halving_doubling(self, event, event.delta)
                if event.steps == 1:
                    return
                doubling_handler = AllReduceHandler(self.future_event_list, self.clock)
                self.future_event_list.add_event(
                    AllReduceEvent(applying_time, doubling_handler,
                                   event.gpu_cards, event.data_size,
                                   event.method, event.steps - 1,
                                   delta=event.delta // 2)
                )
        elif event.method == Method.TREE:
            pass
        elif event.method == Method.BRUCK:
            pass
        else:
            pass
