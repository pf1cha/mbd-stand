from lib.src.network_lib.utils.config import AppConfig
from lib.src.network_lib.model.network import NetworkManager
from lib.src.network_lib.model.model import Model
from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.handler.all_gather_handler import AllGatherStepHandler
from lib.src.network_lib.handler.all_reduce_handler import AllReduceStepHandler
from lib.src.network_lib.handler.reduce_scatter_handler import ReduceScatterStepHandler
from lib.src.network_lib.handler.p2p_handler import P2PStepHandler
from lib.src.core.engine import Engine
import argparse
from lib.src.network_lib.model.topology_manager import TopologyManager
from lib.src.network_lib.enums.primitives import Primitives


def create_sequence(collective_communication, engine, net_config, data_size):
    start_events = []
    total_size = data_size
    for op in collective_communication:
        crt_networks = net_config.get_networks_by_type(op.who)
        size_per_group = 1 # placeholder
        for net in crt_networks:
            handler_class = get_handler_for_primitive(op.type)
            if handler_class:
                start_events.append(
                    (handler_class(engine.future_event_list, is_start_handler=True),
                     op.algorithm,
                     size_per_group,
                     net,
                     )
                )
    return start_events


def get_handler_for_primitive(primitive_type):
    mapping = {
        Primitives.ALL_REDUCE: AllReduceStepHandler,
        Primitives.ALL_GATHER: AllGatherStepHandler,
        Primitives.REDUCE_SCATTER: ReduceScatterStepHandler,
        Primitives.P2P: P2PStepHandler,
    }
    return mapping.get(primitive_type)


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
    sequence_of_actions = create_sequence(
        collective_communication=config.collective_communication,
        engine=sim_engine,
        net_config=all_networks,
        data_size=config.data.size
    )
    model = Model(sequence_of_actions)

    sim_engine.init(filename_results, model)
    sim_engine.execute()
    sim_engine.save_statistic()
