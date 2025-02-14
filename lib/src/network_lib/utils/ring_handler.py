from lib.src.network_lib.handler.p2p_handler import DataTransferHandler
from lib.src.network_lib.event.p2p_event import DataTransferEvent


def one_step_in_ring(handler, event, flag_all_gather=False):
    # Assume that the data is divided into equal chunks
    chunk_size = event.data_size / len(event.network.processors)
    start_index = 1 if flag_all_gather else 0
    applying_time = ring_walk(handler, event, chunk_size, flag_all_gather, index=start_index)
    return applying_time


# ring_walk return max applying time
def ring_walk(handler, event, data_size, flag, index=0):
    """
    This function creates the data transfer events for the ring
    """
    if flag and index == len(event.network.processors) + 1:
        return event.applying_time
    if not flag and index >= len(event.network.processors):
        return event.applying_time
    data_handler = DataTransferHandler(handler.future_event_list)
    first_index = index % len(event.network.processors)
    second_index = (index + 1) % len(event.network.processors)
    print(bool(flag), event.steps, " sender: " , first_index, " receiver: " , second_index)
    new_event = DataTransferEvent(event.applying_time, data_handler,
                                  event.network.processors[first_index],
                                  event.network.processors[second_index],
                                  data_size, event.network.bandwidth,
                                  event.network.latency)
    handler.future_event_list.add_event(new_event)
    next_applying_time = ring_walk(handler, event, data_size, flag, index + 1)
    return max(next_applying_time, new_event.time + event.applying_time)
