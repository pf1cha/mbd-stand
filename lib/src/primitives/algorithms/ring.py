from lib.src.p2p import DataTransferEvent, DataTransferHandler
from lib.src.primitives.help_functions import max_time


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
