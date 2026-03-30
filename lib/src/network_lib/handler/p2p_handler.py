from lib.src.core.handler import Handler
from lib.src.network_lib.event.p2p_event import P2PStepEvent
from lib.src.network_lib.event.datatransfer_event import DataTransferEvent
from lib.src.network_lib.handler.datatransfer_handler import DataTransferHandler


class P2PStepHandler(Handler):
    def __init__(self, future_event_list, is_start_handler=False, next_handler=None):
        super().__init__(future_event_list, is_start_handler, next_handler)

    def add_event_to_fel(self, applying_time, event):
        self.future_event_list.add_event(
            P2PStepEvent(applying_time, self, event.processors, event.topology, event.data_size,
                         steps=event.steps, crt_step=event.crt_step + 1)
        )

    def do(self, event):
        index = (event.crt_step - 1) % len(event.processors)
        recipient_index = (index - 1
                    if event.crt_step >= event.steps // 2
                    else index + 1)

        data_handler = DataTransferHandler(self.future_event_list)
        sender = event.processors[index]
        receiver = event.processors[recipient_index]

        bandwidth = event.topology.get_bandwidth(sender, receiver)
        latency = event.topology.get_latency(sender, receiver)

        new_event = DataTransferEvent(
            event.applying_time,
            data_handler,
            sender,
            receiver,
            event.data_size,
            bandwidth,
            latency,
            parent_uuid=str(event.uuid),
            parent_type=type(event).__name__
        )
        self.future_event_list.add_event(new_event)
        next_iteration = new_event.time + event.applying_time
        if event.crt_step == event.steps:
            return next_iteration
        self.add_event_to_fel(next_iteration, event)
        return None

    def do_on_start(self, applying_time, processors=None, topology=None, method=None, data_size=0):
        if not processors or not topology:
            raise ValueError("Processors and topology must be provided.")
        if data_size <= 0:
            raise ValueError("Data size must be a positive integer.")
        init_event = P2PStepEvent(applying_time, self, processors, topology, data_size)
        self.future_event_list.add_event(init_event)
