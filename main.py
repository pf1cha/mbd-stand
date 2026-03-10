import argparse
from lib.src.core.engine import Engine
from lib.src.network_lib.model.network import NetworkManager
from lib.src.network_lib.model.model import Model
from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.model.topology_manager import TopologyManager
from lib.src.network_lib.utils.starter_helper import create_sequence, get_batch_sizes
from lib.src.network_lib.utils.config import AppConfig

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, help="json or yaml file for configuration.")
    parser.add_argument("-o", "--output", required=True, help="File where will be saved simulation.")
    args = parser.parse_args()
    path = args.config
    filename_results = args.output
    config = AppConfig.load(path)

    sim_engine = Engine()
    number_of_processors = config.parallelism.TP * config.parallelism.DP * config.parallelism.PP
    processors_in_cc = config.parallelism.TP * config.parallelism.DP
    processors = [Processor(i) for i in range(number_of_processors)]
    topology = TopologyManager(processors, config.parallelism.TP, config.parallelism.DP, config.parallelism.PP)

    necessary_groups = set()
    for step in config.collective_communication:
        if step.who == "tp":
            necessary_groups.add("tp")
        elif step.who == "dp":
            necessary_groups.add("dp")
        elif step.who == "pp":
            necessary_groups.add("pp")

    all_networks = NetworkManager(config.networks, topology, necessary_groups)
    batches = get_batch_sizes(config.data.size, topology)
    sequence_of_actions = create_sequence(
        collective_communication=config.collective_communication,
        engine=sim_engine,
        net_config=all_networks,
        data=batches
    )
    model = Model(sequence_of_actions)

    sim_engine.init(filename_results, model)
    sim_engine.execute()
    sim_engine.save_statistic()
