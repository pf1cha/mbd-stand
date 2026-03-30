from lib.src.network_lib.handler.datatransfer_handler import DataTransferHandler
from lib.src.network_lib.event.datatransfer_event import DataTransferEvent


def one_step_in_halving_doubling(handler, event, type_of_alg=None):
    processor_data = event.data_size / (len(event.processors))
    len_of_processors = len(event.processors)
    distance = 0
    size_of_message = 0
    if type_of_alg == 1:  # ReduceScatter (Recursive Halving)
        distance = len_of_processors // (2 * event.crt_step)
        size_of_message = processor_data / (2 ** event.crt_step)

    elif type_of_alg == 2:  # AllGather (Recursive Doubling)
        distance = 1 << (event.crt_step - 1)
        size_of_message = (processor_data / len_of_processors) * (2 ** (event.crt_step - 1))

    elif type_of_alg == 3:  # AllReduce (Halving -> Doubling)
        half_steps = event.steps // 2
        if event.crt_step <= half_steps:
            # Halving
            distance = len_of_processors // (2 * event.crt_step)
            size_of_message = processor_data / (2 ** event.crt_step)
        else:
            # Doubling
            temp_crt_step = int(event.crt_step - half_steps)
            distance = 1 << (temp_crt_step - 1)
            size_of_message = (processor_data / len_of_processors) * (2 ** (temp_crt_step - 1))
    applying_time = halving_doubling_walk_improve(handler, event, distance, size_of_message)
    return applying_time


def halving_doubling_walk_improve(handler, event, step_size, chunk_size, index=0):
    if index == len(event.processors):
        return event.applying_time

    data_handler = DataTransferHandler(handler.future_event_list)
    recipient_index = index ^ step_size
    sender = event.processors[index]
    receiver = event.processors[recipient_index]

    bandwidth = event.topology.get_bandwidth(sender, receiver)
    latency = event.topology.get_latency(sender, receiver)

    new_event = DataTransferEvent(
        event.applying_time,
        data_handler,
        sender,
        receiver,
        chunk_size,
        bandwidth,
        latency,
        parent_uuid=str(event.uuid),
        parent_type=type(event).__name__
    )
    handler.future_event_list.add_event(new_event)
    next_applying_time = halving_doubling_walk_improve(
        handler, event, step_size, chunk_size, index + 1
    )
    return max(next_applying_time, new_event.time + event.applying_time)
