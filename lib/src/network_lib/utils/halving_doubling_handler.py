from lib.src.network_lib.handler.p2p_handler import DataTransferHandler
from lib.src.network_lib.event.p2p_event import DataTransferEvent
from lib.src.network_lib.utils.help_functions import max_time


def one_step_in_halving_doubling(handler, event, delta):
    chunk_size = event.data_size / (len(event.network) * 2 * delta)
    halving_doubling_walk(handler, event, chunk_size, delta)
    applying_time = event.applying_time + max_time(event.network, chunk_size)
    return applying_time


def halving_doubling_walk(handler, event, chunk_size, delta, index=0):
    if index >= len(event.network) // 2:
        return
    data_handler = DataTransferHandler(handler.future_event_list)
    first_index = index
    second_index = index + delta
    handler.future_event_list.add_event(
        DataTransferEvent(event.applying_time, data_handler,
                          event.network[first_index], event.network[second_index], chunk_size)
    )
    handler.future_event_list.add_event(
        DataTransferEvent(event.applying_time, data_handler,
                          event.network[second_index], event.network[first_index], chunk_size)
    )
    halving_doubling_walk(handler, event, chunk_size, delta, index + 1)
