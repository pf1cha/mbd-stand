from lib.src.engine import Engine
from lib.src.primitives import AllReduceRingEvent, AllReduceRingHandler
from lib.src.graphic_card import GraphicCard
import json


if __name__ == '__main__':
    engine = Engine()
    graphic_cards_array = [GraphicCard(6, 0.2) for _ in range(5)]
    start_handler = AllReduceRingHandler(engine.future_event_list, engine.clock)
    engine.create_start_event(AllReduceRingEvent(0, start_handler, graphic_cards_array, 100))
    engine.start("stats.json")

    with open('stats.json', 'r') as file:
        data = json.load(file)

    # Initialize counters
    all_reduce_ring_count = 0
    data_transfer_event_count = 0

    # Iterate through the events and count the occurrences
    for event in data['events']:
        if event['event_type'] == 'AllReduceRing':
            all_reduce_ring_count += 1
        elif event['event_type'] == 'DataTransferEvent':
            data_transfer_event_count += 1

    # Print the counts
    print(f"AllReduceRing count: {all_reduce_ring_count}")
    print(f"DataTransferEvent count: {data_transfer_event_count}")
