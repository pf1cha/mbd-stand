from lib.src.core.handler import Handler
from lib.src.network_lib.event.all_reduce_event import AllReduceStepEvent
from lib.src.network_lib.utils.ring_handler import one_step_in_ring
from lib.src.network_lib.utils.halving_doubling_handler import one_step_in_halving_doubling
from lib.src.network_lib.utils.methods import Method
from numpy import log2


class AllReduceStepHandler(Handler):
    def __init__(self, future_event_list):
        super().__init__(future_event_list)

    def do(self, event):
        if event.method == Method.RING:
            if event.steps >= len(event.network.processors):
                applying_time = one_step_in_ring(self, event)
                self.future_event_list.add_event(
                    AllReduceStepEvent(applying_time, self,
                                       event.network, event.data_size,
                                       event.method, event.steps - 1)
                )
            else:
                applying_time = one_step_in_ring(self, event, flag_all_gather=True)
                if event.steps == 1:
                    return applying_time
                self.future_event_list.add_event(
                    AllReduceStepEvent(applying_time, self,
                                       event.network, event.data_size,
                                       event.method, event.steps - 1)
                )
        elif event.method == Method.HALVING_DOUBLING:
            if event.steps > log2(len(event.network.processors)):
                applying_time = one_step_in_halving_doubling(self, event)
                next_delta = event.delta * 2 if 2 * event.delta != len(event.network.processors) else event.delta
                self.future_event_list.add_event(
                    AllReduceStepEvent(applying_time, self,
                                       event.network, event.data_size,
                                       event.method, event.steps - 1,
                                       delta=next_delta)
                )
            else:
                applying_time = one_step_in_halving_doubling(self, event)
                if event.steps == 1:
                    return
                self.future_event_list.add_event(
                    AllReduceStepEvent(applying_time, self,
                                       event.network, event.data_size,
                                       event.method, event.steps - 1,
                                       delta=event.delta // 2)
                )
        else:
            pass
