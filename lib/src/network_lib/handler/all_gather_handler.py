from lib.src.core.handler import Handler
from lib.src.network_lib.event.all_gather_event import AllGatherStepEvent
from lib.src.network_lib.utils.ring_handler import one_step_in_ring_improved
from lib.src.network_lib.utils.halving_doubling_handler import one_step_in_halving_doubling
from lib.src.network_lib.utils.methods import Method


class AllGatherStepHandler(Handler):
    def __init__(self, future_event_list, is_start_handler=False, next_handler=None):
        super().__init__(future_event_list, is_start_handler, next_handler)

    def do(self, event):
        if event.method == Method.RING:
            applying_time = one_step_in_ring_improved(self, event, 2)
            if event.crt_step == event.steps:
                return applying_time
            self.future_event_list.add_event(
                AllGatherStepEvent(applying_time, self,
                                   event.network, event.data_size,
                                   event.method, event.steps,
                                   crt_step=event.crt_step + 1)
            )
        elif event.method == Method.HALVING_DOUBLING:
            applying_time = one_step_in_halving_doubling(self, event, 2)
            if event.crt_step == event.steps:
                return
            self.future_event_list.add_event(
                AllGatherStepEvent(applying_time, self,
                                   event.network, event.data_size,
                                   event.method, steps=event.steps,
                                   crt_step=event.crt_step + 1)
            )
        else:
            pass

    def do_on_start(self, applying_time, network=None, method=None, data_size=0):
        init_event = AllGatherStepEvent(
            applying_time=applying_time,
            handler=self,
            network=network,
            data_size=data_size,
            method=method,
        )
        self.future_event_list.add_event(init_event)

