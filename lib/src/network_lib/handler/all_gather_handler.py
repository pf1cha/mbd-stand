from lib.src.core.handler import Handler
from lib.src.network_lib.event.all_gather_event import AllGatherEvent
from lib.src.primitives.algorithms.ring import one_step_in_ring
from lib.src.primitives.algorithms.halving_doubling import one_step_in_halving_doubling
from lib.src.network_lib.helpers.methods import Method


class AllGatherHandler(Handler):
    def __init__(self, future_event_list):
        super().__init__(future_event_list)

    def do(self, event):
        if event.method == Method.RING:
            applying_time = one_step_in_ring(self, event)
            if event.steps == 1:
                return applying_time
            ring_handler = AllGatherHandler(self)
            self.future_event_list.add_event(
                AllGatherEvent(applying_time, ring_handler,
                               event.processors, event.data_size,
                               event.method, event.steps - 1)
            )
        elif event.method == Method.HALVING_DOUBLING:
            applying_time = one_step_in_halving_doubling(self, event, event.delta)
            if event.steps == 1:
                return
            halving_handler = AllGatherHandler(self)
            next_delta = event.delta // 2
            self.future_event_list.add_event(
                AllGatherEvent(applying_time, halving_handler,
                               event.processors, event.data_size, event.method,
                               steps=event.steps - 1,
                               delta=next_delta)
            )
        elif event.method == Method.TREE:
            pass
        elif event.method == Method.BRUCK:
            pass
        else:
            pass
