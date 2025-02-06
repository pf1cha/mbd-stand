from lib.src.core.handler import Handler
from lib.src.network_lib.event.all_reduce_event import AllReduceEvent
from lib.src.primitives.algorithms.ring import one_step_in_ring
from lib.src.primitives.algorithms.halving_doubling import one_step_in_halving_doubling
from lib.src.network_lib.helpers.methods import Method
from numpy import log2


class AllReduceHandler(Handler):
    def __init__(self, future_event_list):
        super().__init__(future_event_list)

    def do(self, event):
        if event.method == Method.RING:
            # TODO Change the first index of the ring when the AllGather starts
            applying_time = one_step_in_ring(self, event)
            if event.steps == 1:
                return applying_time
            ring_handler = AllReduceHandler(self.future_event_list)
            self.future_event_list.add_event(
                AllReduceEvent(applying_time, ring_handler,
                               event.processors, event.data_size, event.method, event.steps - 1)
            )
        elif event.method == Method.HALVING_DOUBLING:
            if event.steps > log2(len(event.gpu_cards)):
                applying_time = one_step_in_halving_doubling(self, event, event.delta)
                halving_handler = AllReduceHandler(self.future_event_list)
                next_delta = event.delta * 2 if 2 * event.delta != len(event.gpu_cards) else event.delta
                self.future_event_list.add_event(
                    AllReduceEvent(applying_time, halving_handler,
                                   event.processors, event.data_size,
                                   event.method, event.steps - 1,
                                   delta=next_delta)
                )
            else:
                applying_time = one_step_in_halving_doubling(self, event, event.delta)
                if event.steps == 1:
                    return
                doubling_handler = AllReduceHandler(self.future_event_list)
                self.future_event_list.add_event(
                    AllReduceEvent(applying_time, doubling_handler,
                                   event.processors, event.data_size,
                                   event.method, event.steps - 1,
                                   delta=event.delta // 2)
                )
        elif event.method == Method.TREE:
            pass
        elif event.method == Method.BRUCK:
            pass
        else:
            pass
