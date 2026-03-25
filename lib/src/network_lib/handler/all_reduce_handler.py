from lib.src.core.handler import Handler
from lib.src.network_lib.event.all_reduce_event import AllReduceStepEvent
from lib.src.network_lib.cc_algorithms.ring_handler import one_step_in_ring_improved
from lib.src.network_lib.cc_algorithms.halving_doubling_handler import one_step_in_halving_doubling
from lib.src.network_lib.enums.methods import Method
from lib.src.network_lib.utils.help_functions import count_steps


class AllReduceStepHandler(Handler):
    def __init__(self, future_event_list, is_start_handler=False, next_handler=None):
        super().__init__(future_event_list, is_start_handler, next_handler)

    def add_event_to_fel(self, applying_time, event):
        self.future_event_list.add_event(
            AllReduceStepEvent(
                applying_time, self, event.processors, event.topology, event.data_size,
                event.method, event.steps, crt_step=event.crt_step + 1
            )
        )

    def do(self, event):
        if event.method == Method.RING:
            applying_time = one_step_in_ring_improved(self, event, 3)
            if event.crt_step == event.steps:
                return applying_time
            self.add_event_to_fel(applying_time, event)
        elif event.method == Method.HALVING_DOUBLING:
            applying_time = one_step_in_halving_doubling(self, event, 3)
            if event.crt_step == event.steps:
                return applying_time
            self.add_event_to_fel(applying_time, event)
        else:
            raise ValueError(
                f"Unsupported method: {event.method}. "
                f"Supported methods are: {', '.join([m.name for m in Method])}."
            )
        return None

    def do_on_start(self, applying_time, processors=None, topology=None, method=None, data_size=0):
        if not processors or not topology:
            raise ValueError("Processors and topology must be provided.")
        if method not in Method:
            raise ValueError(f"Invalid method: {method}. Supported methods are: {', '.join([m.name for m in Method])}.")
        if data_size <= 0:
            raise ValueError("Data size must be a positive integer.")
        total_steps = count_steps(method, len(processors))
        if total_steps is None:
            raise ValueError("Number of steps is not defined or number of processors is not a power of two.")
        init_event = AllReduceStepEvent(
            applying_time=applying_time,
            handler=self,
            processors=processors,
            topology=topology,
            data_size=data_size,
            steps=2 * total_steps,
            method=method,
        )
        self.future_event_list.add_event(init_event)
