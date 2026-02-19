from lib.src.network_lib.utils.config import AppConfig
from lib.src.network_lib.model.network import Network
from lib.src.network_lib.model.model import Model
from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.handler.all_gather_handler import AllGatherStepHandler
from lib.src.network_lib.handler.all_reduce_handler import AllReduceStepHandler
from lib.src.network_lib.handler.reduce_scatter_handler import ReduceScatterStepHandler
from lib.src.core.engine import Engine
import argparse


def create_sequence(config, engine, total_groups):
    start_events = []
    total_size = config.data.size
    size_for_pipeline = total_size // total_groups
    for op in config.collective_communication:
        if op.type == "AllReduce":
            start_events.append((AllReduceStepHandler(engine.future_event_list, is_start_handler=True),
                                op.algorithm, size_for_pipeline))
        elif op.type == "AllGather":
            start_events.append((AllGatherStepHandler(engine.future_event_list, is_start_handler=True),
                                op.algorithm, size_for_pipeline))
        elif op.type == "ReduceScatter":
            start_events.append((ReduceScatterStepHandler(engine.future_event_list, is_start_handler=True),
                                op.algorithm, size_for_pipeline))
        elif op.type == "p2p":
            pass
        else:
            raise ValueError(f"Unknown operation {op.type}. Program supports only 'AllReduce', 'AllGather', "
                             f"'ReduceScatter' and 'p2p'")
    return start_events

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, help="json or yaml file for configuration.")
    parser.add_argument("-o", "--output", required=True, help="File where will be saved simulation.")
    args = parser.parse_args()
    path = args.config
    filename_results = args.output
    config = AppConfig.load(path)
    for op in config.collective_communication:
        print(f"{op.type}: {op.algorithm}")

    engine = Engine()
    number_of_processors = config.parallelism.TP * config.parallelism.DP * config.parallelism.PP
    processors_in_cc = config.parallelism.TP * config.parallelism.DP
    processors = [Processor() for _ in range(number_of_processors)]
    network = Network(config.network.bandwidth, config.network.latency, processors)

    sequence_of_actions = create_sequence(config, engine, processors_in_cc)
    model = Model(sequence_of_actions)
    engine.init(filename_results, model)
    engine.execute(network)
    engine.save_statistic()
