import json


def count_events_in_json(filename):
    with open(filename) as file:
        data = json.load(file)

    # Initialize counters
    all_reduce_count = 0
    all_gather_count = 0
    reduce_scatter_count = 0
    data_transfer_event_count = 0

    # Iterate through the events and count the occurrences
    for event in data['events']:
        if event['event_type'] == 'DataTransferEvent':
            data_transfer_event_count += 1
        elif event['event_type'] == 'AllReduceStepEvent':
            all_reduce_count += 1
        elif event['event_type'] == 'AllGatherStepEvent':
            all_gather_count += 1
        elif event['event_type'] == 'ReduceScatterStepEvent':
            reduce_scatter_count += 1

    # Print the counts
    print(f"DataTransferEvent count: {data_transfer_event_count}")
    print(f"AllReduce count: {all_reduce_count}")
    print(f"ReduceScatter count: {reduce_scatter_count}")
    print(f"AllGather count: {all_gather_count}")