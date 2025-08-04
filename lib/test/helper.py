import json


def describe_event_in_text(json_data, network):
    with open(json_data, "r") as file:
        json_data = json.load(file)

    uuid_to_simple_id = {
        str(p.uuid): idx for idx, p in enumerate(network.processors)
    }
    events = json_data.get("events", [])
    for event in events:
        event_type = event.get("event_type")
        time = event.get("applying_time")

        if event_type == "AllReduceStepEvent" or event_type == "AllGatherStepEvent" or event_type == "ReduceScatterStepEvent":
            method = event.get("method", "UNKNOWN")
            data_size_of_full_step = event.get("data_size", 0)
            print(
                f"[{time:.2f}] {event_type} (Method: {method}) "
                f"occurred with total data size of {data_size_of_full_step}."
            )
            print(f"The data in each processor is {data_size_of_full_step / len(network.processors)}.")

        elif event_type == "DataTransferEvent":
            src_uuid = event.get("gpu_source")
            dst_uuid = event.get("gpu_destination")
            data_size = event.get("data_size", "UNKNOWN")

            src_idx = uuid_to_simple_id.get(src_uuid, "Unknown")
            dst_idx = uuid_to_simple_id.get(dst_uuid, "Unknown")

            print(
                f"[{time:.2f}] DataTransfer: From processor {src_idx} "
                f"to processor {dst_idx} with data size: {data_size}"
            )


def count_events_in_json(filename):
    with open(filename) as file:
        data = json.load(file)

    # Initialize counters
    all_reduce_count = 0
    all_gather_count = 0
    reduce_scatter_count = 0
    data_transfer_event_count = 0

    # Iterate through the handlers and count the occurrences
    for event in data['handlers']:
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