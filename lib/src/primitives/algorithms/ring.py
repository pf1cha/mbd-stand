from lib.src.network_lib.handler.p2p_handler import DataTransferHandler
from lib.src.network_lib.event.p2p_event import DataTransferEvent
from lib.src.network_lib.helpers.help_functions import max_time


def one_step_in_ring(handler, event):
    # Assume that the data is divided into equal chunks
    chunk_size = event.data_size / len(event.processors)
    ring_walk(handler, event, chunk_size)
    # If the gpu cards are all the same and have the same bandwidth,
    # the time to apply the event is the same for all of them
    applying_time = handler.clock.get_time() + max_time(event.processors, chunk_size)
    return applying_time


def ring_walk(handler, event, data_size, index=0):
    """
    This function creates the data transfer events for the ring
    """
    if index >= len(event.gpu_cards):
        return
    data_handler = DataTransferHandler(handler.future_event_list)
    second_index = (index + 1) % len(event.gpu_cards)
    handler.future_event_list.add_event(
        DataTransferEvent(handler.clock.get_time(), data_handler,
                          event.processors[index], event.processors[second_index], data_size)
    )
    ring_walk(handler, event, data_size, index + 1)
