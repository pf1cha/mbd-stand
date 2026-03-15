import argparse
import sys
from lib.src.core.engine import Engine
from lib.src.network_lib.model.network import NetworkManager
from lib.src.network_lib.model.model import Model
from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.model.topology_manager import TopologyManager
from lib.src.network_lib.network_topology.topology_factory import create_topology
from lib.src.network_lib.utils.starter_helper import create_sequence, get_batch_sizes
from lib.src.network_lib.utils.config import AppConfig


def _build_parser():
    parser = argparse.ArgumentParser(prog="main.py")
    parser.add_argument("-c", "--config", required=True, )
    parser.add_argument("-o", "--output", required=True)
    # # TODO think about the two parameters requirement, maybe it's a not necessary restriction
    # parser.add_argument("-e", "--experiment", action="store_true", default=False)
    return parser


def run_single(config, output_path):
    n_procs = config.parallelism.TP * config.parallelism.DP * config.parallelism.PP
    processors = [Processor(i) for i in range(n_procs)]
    topo_mgr = TopologyManager(
        processors,
        config.parallelism.TP,
        config.parallelism.DP,
        config.parallelism.PP,
    )

    cluster_topology = create_topology(config.cluster_topology, processors)

    necessary_groups = set()
    for step in config.collective_communication:
        if step.who:
            necessary_groups.add(step.who)

    sim_engine = Engine()
    all_networks = NetworkManager(
        topo_mgr,
        necessary_groups,
        cluster_topology,
    )

    batches = get_batch_sizes(config.data.size, topo_mgr)
    sequence = create_sequence(
        collective_communication=config.collective_communication,
        engine=sim_engine,
        net_config=all_networks,
        data=batches,
    )
    model = Model(sequence)

    sim_engine.init(output_path, model)
    sim_engine.execute()
    sim_engine.save_statistic()

    total_time = sim_engine.clock.get_time()
    print(f"Total simulation time : {total_time:.6e} s")
    print(f"Statistics saved to   : {output_path}")


if __name__ == "__main__":
    parser = _build_parser()
    args = parser.parse_args()

    try:
        config = AppConfig.load(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[error] Failed to load config: {exc}", file=sys.stderr)
        sys.exit(1)

    run_single(config, args.output)
