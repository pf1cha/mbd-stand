from lib.src.network_lib.handler.datatransfer_handler import DataTransferHandler
from lib.src.network_lib.event.datatransfer_event import DataTransferEvent


def define_ring_direction(event, type_of_primitive):
    if type_of_primitive == 1:  # ReduceScatter
        return 0
    elif type_of_primitive == 2:  # AllGather
        return 1
    # AllReduce
    return 0 if event.crt_step <= event.steps // 2 else 1



def one_step_in_ring(handler, event, type_of_primitive=None):
    # Assuming that the data is divided into equal chunks and each processor sends its own chunk
    # direction: 0 for clockwise, 1 for counter-clockwise
    data_size = event.data_size / (len(event.processors))
    index = 0
    direction = define_ring_direction(event, type_of_primitive)
    applying_time = ring_walk(handler, event, data_size, index, direction)
    return applying_time


def define_sender_receiver(event, index, direction):
    sender, receiver = None, None
    if direction == 0:  # Clockwise
        sender = event.processors[index]
        receiver = event.processors[(index + 1) % len(event.processors)]
    elif direction == 1:
        sender = event.processors[index]
        receiver = event.processors[(index - 1) % len(event.processors)]
    return sender, receiver


def ring_walk(handler, event, data_size, index=0, direction=None):
    if direction is None or data_size is None:
        raise ValueError("Direction and data_size must be specified for improved ring walk.")
    if index >= len(event.processors):
        return event.applying_time

    sender, receiver = define_sender_receiver(event, index, direction)
    data_handler = DataTransferHandler(handler.future_event_list)

    bandwidth = event.topology.get_bandwidth(sender, receiver)
    latency = event.topology.get_latency(sender, receiver)
    new_event = DataTransferEvent(
        event.applying_time, data_handler,
        sender, receiver, data_size,
        bandwidth, latency,
        parent_uuid=str(event.uuid),
        parent_type=type(event).__name__
    )
    handler.future_event_list.add_event(new_event)
    next_applying_time = ring_walk(handler, event, data_size, index + 1, direction)
    return max(next_applying_time, new_event.time + event.applying_time)
