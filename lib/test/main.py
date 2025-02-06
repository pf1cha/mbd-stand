from lib.src.core.engine import Engine
from lib.src.network_lib.handler.all_reduce_handler import AllReduceEvent, AllReduceHandler
from lib.src.network_lib.handler.all_gather_handler import AllGatherEvent, AllGatherHandler
from lib.src.network_lib.handler.reduce_scatter_handler import ReduceScatterEvent, ReduceScatterHandler
from lib.src.network_lib.helpers.processor import Processor
from lib.src.network_lib.helpers.methods import Method
import json


def test_all_reduce(engine, processors):
    start_handler = AllReduceHandler(engine.future_event_list)
    start_event = AllReduceEvent(0, start_handler,
                                 processors, 1600,
                                 Method.HALVING_DOUBLING)
    return start_event


def test_all_gather(engine, processors):
    start_handler = AllGatherHandler(engine.future_event_list)
    start_event = AllGatherEvent(0, start_handler,
                                 processors, 1600,
                                 Method.HALVING_DOUBLING)
    return start_event


def test_reduce_scatter(engine, processors):
    start_handler = ReduceScatterHandler(engine.future_event_list)
    start_event = ReduceScatterEvent(0, start_handler,
                                     processors, 1600,
                                     Method.HALVING_DOUBLING)
    return start_event


if __name__ == '__main__':
    engine = Engine()
    processors = [Processor(6, 0.2) for _ in range(2 ** 2)]
    # TODO change the first iteration in all reduce for all gather
    engine.future_event_list.add_event(test_all_reduce(engine, processors))
    engine.execute("lib/results/all_reduce_ring_stats.json")

    with open('lib/results/all_reduce_ring_stats.json', 'r') as file:
        data = json.load(file)

    # Initialize counters
    all_reduce_count = 0
    all_gather_count = 0
    reduce_scatter_count = 0
    data_transfer_event_count = 0

    # Iterate through the events and count the occurrences
    for event in data['events']:
        if event['event_type'] == 'AllReduceEvent':
            all_reduce_count += 1
        elif event['event_type'] == 'DataTransferEvent':
            data_transfer_event_count += 1
        elif event['event_type'] == 'AllGatherEvent':
            all_gather_count += 1
        elif event['event_type'] == 'ReduceScatterEvent':
            reduce_scatter_count += 1

    # Print the counts
    print(f"DataTransferEvent count: {data_transfer_event_count}")
    print(f"AllReduce count: {all_reduce_count}")
    print(f"ReduceScatter count: {reduce_scatter_count}")
    print(f"AllGather count: {all_gather_count}")
