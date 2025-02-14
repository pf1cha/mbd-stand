from lib.src.core.handler import Handler
from lib.src.network_lib.event.reduce_scatter_event import ReduceScatterStepEvent
from lib.src.network_lib.utils.ring_handler import one_step_in_ring
from lib.src.network_lib.utils.halving_doubling_handler import one_step_in_halving_doubling
from lib.src.network_lib.utils.methods import Method


class ReduceScatterStepHandler(Handler):
    def __init__(self, future_event_list):
        super().__init__(future_event_list)

    def do(self, event):
        if event.method == Method.RING:
            applying_time = one_step_in_ring(self, event)
            if event.steps == 1:
                return applying_time
            self.future_event_list.add_event(
                ReduceScatterStepEvent(applying_time, self,
                                       event.network, event.data_size,
                                       event.method, event.steps - 1)
            )
        elif event.method == Method.HALVING_DOUBLING:
            applying_time = one_step_in_halving_doubling(self, event)
            if event.steps == 1:
                return
            next_delta = event.delta * 2
            self.future_event_list.add_event(
                ReduceScatterStepEvent(applying_time, self,
                                       event.network, event.data_size,
                                       event.method, event.steps - 1,
                                       delta=next_delta)
            )
        else:
            pass
