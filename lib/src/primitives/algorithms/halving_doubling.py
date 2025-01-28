from lib.src.p2p import DataTransferEvent, DataTransferHandler
from lib.src.primitives.help_functions import max_time


def one_step_in_halving_doubling(handler, event, delta):
    chunk_size = event.data_size / ( len(event.gpu_cards) * 2 * delta)
    halving_doubling_walk(handler, event, chunk_size, delta)
    applying_time = handler.clock.get_time() + max_time(event.gpu_cards, chunk_size)
    return applying_time


def halving_doubling_walk(handler, event, chunk_size, delta, index=0):
    if index >= len(event.gpu_cards) // 2:
        return
    data_handler = DataTransferHandler(handler.future_event_list, handler.clock)
    first_index = index
    second_index = index + delta
    handler.future_event_list.add_event(
        DataTransferEvent(handler.clock.get_time(), data_handler,
                          event.gpu_cards[first_index], event.gpu_cards[second_index], chunk_size)
    )
    handler.future_event_list.add_event(
        DataTransferEvent(handler.clock.get_time(), data_handler,
                          event.gpu_cards[second_index], event.gpu_cards[first_index], chunk_size)
    )
    halving_doubling_walk(handler, event, chunk_size, delta, index + 1)
