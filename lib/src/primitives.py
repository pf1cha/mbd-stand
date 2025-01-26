from lib.src.event import Event
from lib.src.handler import Handler
from lib.src.p2p import DataTransferEvent, DataTransferHandler


def one_step_in_ring(handler, event):
    # Assume that the data is divided into equal chunks
    chunk_size = event.data_size / len(event.gpu_cards)
    ring_walk(handler, event, chunk_size)
    # If the gpu cards are all the same and have the same bandwidth,
    # the time to apply the event is the same for all of them
    applying_time = handler.clock.get_time() + max_time(event.gpu_cards, chunk_size)
    return applying_time

def ring_walk(handler, event, data_size, index=0):
    """
    This function creates the data transfer events for the ring
    """
    if index >= len(event.gpu_cards):
        return
    data_handler = DataTransferHandler(handler.future_event_list, handler.clock)
    second_index = (index + 1) % len(event.gpu_cards)
    handler.future_event_list.add_event(
        DataTransferEvent(handler.clock.get_time(), data_handler,
                          event.gpu_cards[index], event.gpu_cards[second_index], data_size)
    )
    ring_walk(handler, event, data_size, index + 1)


def max_time(gpu_cards, chunk_size):
    return max([gpu.latency + chunk_size / gpu.bandwidth for gpu in gpu_cards])


class AllReduceRingEvent(Event):
    def __init__(self, applying_time, handler, gpu_cards, data_size, steps=None):
        super().__init__(applying_time, handler)
        self.gpu_cards = gpu_cards
        self.data_size = data_size
        self.steps = (len(gpu_cards) - 1) * 2 if steps is None else steps

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "handler_type": type(self.handler).__name__,
            "applying_time": self.applying_time,
            "data_size": self.data_size,
        }

class AllReduceRingHandler(Handler):
    def __init__(self, future_event_list, clock):
        super().__init__(future_event_list, clock)

    def do(self, event):
        applying_time = one_step_in_ring(self, event)
        if event.steps == 1:
            return
        all_reduce_ring_handler = AllReduceRingHandler(self.future_event_list, self.clock)
        self.future_event_list.add_event(
            AllReduceRingEvent(applying_time, all_reduce_ring_handler,
                               event.gpu_cards, event.data_size, event.steps - 1)
        )


class ReduceScatterRingEvent(Event):
    def __init__(self, applying_time, handler, gpu_cards, data_size, steps=None):
        super().__init__(applying_time, handler)
        self.gpu_cards = gpu_cards
        self.data_size = data_size
        self.steps = len(gpu_cards) - 1 if steps is None else steps

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "handler_type": type(self.handler).__name__,
            "applying_time": self.applying_time,
            "data_size": self.data_size,
        }


class ReduceScatterRingHandler(Handler):
    def __init__(self, future_event_list, clock):
        super().__init__(future_event_list, clock)

    def do(self, event):
        applying_time = one_step_in_ring(self, event)
        if event.steps == 1:
            return
        handler = ReduceScatterRingHandler(self.future_event_list, self.clock)
        self.future_event_list.add_event(
            ReduceScatterRingEvent(applying_time, handler,
                          event.gpu_cards, event.data_size, event.steps - 1)
        )


class AllGatherRingEvent(Event):
    def __init__(self, applying_time, handler, gpu_cards, data_size, steps=None):
        super().__init__(applying_time, handler)
        self.gpu_cards = gpu_cards
        self.data_size = data_size
        self.steps = len(gpu_cards) - 1 if steps is None else steps

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "applying_time": self.applying_time,
            "handler_type": type(self.handler).__name__,
            "data_size": self.data_size,
        }


class AllGatherRingHandler(Handler):
    def __init__(self, future_event_list, clock):
        super().__init__(future_event_list, clock)

    def do(self, event):
        applying_time = one_step_in_ring(self, event)
        if event.steps == 1:
            return
        handler = AllGatherRingHandler(self.future_event_list, self.clock)
        self.future_event_list.add_event(
            AllGatherRingEvent(applying_time, handler, event.gpu_cards, event.data_size, event.steps - 1)
        )
