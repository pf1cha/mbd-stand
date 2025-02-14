from lib.src.network_lib.handler.p2p_handler import DataTransferHandler
from lib.src.network_lib.event.p2p_event import DataTransferEvent


def one_step_in_halving_doubling(handler, event):
    chunk_size = event.data_size / (len(event.network.processors) * 2 * event.delta)
    applying_time = halving_doubling_walk(handler, event, chunk_size)
    return applying_time


def halving_doubling_walk(handler, event, chunk_size, index=0):
    if index >= len(event.network.processors) // 2:
        return event.applying_time
    data_handler = DataTransferHandler(handler.future_event_list)
    first_index = index
    second_index = index + event.delta
    first_event = DataTransferEvent(event.applying_time, data_handler,
                                    event.network.processors[first_index],
                                    event.network.processors[second_index],
                                    chunk_size, event.network.bandwidth,
                                    event.network.latency)
    second_event = DataTransferEvent(event.applying_time, data_handler,
                                     event.network.processors[second_index],
                                     event.network.processors[first_index],
                                     chunk_size, event.network.bandwidth,
                                     event.network.latency)
    handler.future_event_list.add_event(first_event)
    handler.future_event_list.add_event(second_event)
    next_applying_time = halving_doubling_walk(handler, event, chunk_size, index + 1)
    max_of_two_times = max(first_event.time, second_event.time)
    return max(next_applying_time, max_of_two_times + event.applying_time)
