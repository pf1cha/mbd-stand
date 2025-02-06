from lib.src.core.engine import Engine
from lib.src.network_lib.handler.all_reduce_handler import AllReduceEvent, AllReduceHandler
from lib.src.network_lib.helpers.processor import Processor
from lib.src.network_lib.helpers.methods import Method
import json


def test_all_reduce_ring(engine, processors):
    start_handler = AllReduceHandler(engine.future_event_list)
    start_event = AllReduceEvent(0, start_handler,
                                 processors, 1600,
                                 Method.RING)
    return start_event


if __name__ == '__all_reduce_ring__':
    engine = Engine()
    processors = [Processor(6, 0.2) for _ in range(2 ** 2)]
    engine.future_event_list.add_event(test_all_reduce_ring(engine, processors))
    engine.execute("../results/all_reduce_ring.json")

    with open('../results/stats.json', 'r') as file:
        data = json.load(file)

    # Initialize counters
    all_reduce_count = 0
    data_transfer_event_count = 0

    # Iterate through the events and count the occurrences
    for event in data['events']:
        if event['event_type'] == 'AllReduceEvent':
            all_reduce_count += 1
        elif event['event_type'] == 'DataTransferEvent':
            data_transfer_event_count += 1

    # Print the counts
    print(f"AllReduce count: {all_reduce_count}")
    print(f"DataTransferEvent count: {data_transfer_event_count}")
