from lib.src.network_lib.handler.datatransfer_handler import DataTransferHandler
from lib.src.network_lib.event.datatransfer_event import DataTransferEvent


# Here we are assuming that the number of event.network.processors is a power of two.
# If it is not, the halving-doubling algorithm can't be implemented correctly.
# number of processors = 2 ** d, where d so-called bidirectional exchanges (BDE)

def one_step_in_halving_doubling(handler, event, type_of_alg=None):
    size_of_one_processor = event.data_size / (len(event.network.processors))
    distance = 0
    size_of_message = 0
    if type_of_alg == 3:  # Halving-Doubling
        if event.crt_step <= event.steps // 2:
            distance = len(event.network.processors) // (2 * event.crt_step)
            size_of_message = size_of_one_processor / (2 ** event.crt_step)
        else:
            temp_crt_step = int(event.crt_step - (event.steps / 2))
            distance = 1 << (temp_crt_step - 1)
            size_of_message = size_of_one_processor / (2 ** (event.steps // 2 - temp_crt_step + 1))
    elif type_of_alg == 1:  # Halving
        distance = len(event.network.processors) // (2 * event.crt_step)
        size_of_message = size_of_one_processor / (2 ** event.crt_step)
    elif type_of_alg == 2:  # Doubling
        distance = 1 << (event.crt_step - 1)
        size_of_message = size_of_one_processor / (2 ** (event.steps - event.crt_step + 1))

    applying_time = halving_doubling_walk_improve(handler, event, distance, size_of_message)
    return applying_time


def halving_doubling_walk_improve(handler, event, step_size, chunk_size, index=0):
    if index == len(event.network.processors):
        return event.applying_time

    data_handler = DataTransferHandler(handler.future_event_list)
    recipient_index = index ^ step_size
    sender = event.network.processors[index]
    receiver = event.network.processors[recipient_index]
    bandwidth, latency = event.network.get_transfer_params(sender, receiver)
    new_event = DataTransferEvent(
        event.applying_time,
        data_handler,
        sender,
        receiver,
        chunk_size,
        bandwidth,
        latency,
    )
    handler.future_event_list.add_event(new_event)
    next_applying_time = halving_doubling_walk_improve(
        handler, event, step_size, chunk_size, index + 1
    )
    return max(next_applying_time, new_event.time + event.applying_time)
