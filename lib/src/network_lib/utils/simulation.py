from lib.src.core.engine import Engine
from lib.src.network_lib.experiment.experiment_layout import ExperimentLayoutGenerator
from lib.src.network_lib.model.model import Model
from lib.src.network_lib.model.network import NetworkManager
from lib.src.network_lib.model.parallelism_manager import ParallelismManager
from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.network_topology.topology_factory import create_topology, create_topology_from_nodes
from lib.src.network_lib.utils.starter_helper import get_batch_sizes, create_sequence


def run_single(config, output_path):
    n_procs = config.parallelism.TP * config.parallelism.DP * config.parallelism.PP
    processors = [Processor(i) for i in range(n_procs)]
    topo_mgr = ParallelismManager(
        processors,
        config.parallelism.TP,
        config.parallelism.DP,
        config.parallelism.PP,
    )
    cluster_topology = create_topology(config.cluster_topology, processors)
    cluster_topology.print_full_info()

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
    # TODO think about how to print the result time
    print(f"Total simulation time : {total_time:.6e} s")
    print(f"Statistics saved to   : {output_path}")
    print(f"Program finished successfully.")


def run_iteration_of_experiment(layout, config, output_path, topo_mgr, nodes):
    # TODO implement this function to run a single iteration of the experiment with the given layout and config
    #  and save the results to the output path
    cluster_topology = create_topology_from_nodes(config.cluster_topology, nodes)

    # TODO think about this question: Do I neet to keep it in experiment and should I use it as an option for permutations?
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

    sim_engine.init(None, model)
    sim_engine.execute()

    total_time = sim_engine.clock.get_time()
    print(f"Layout: {layout} -> Simulation time: {total_time:.6e} s")
    return total_time


def run_experiment(config, output_path):
    n_procs = config.parallelism.TP * config.parallelism.DP * config.parallelism.PP
    processors = [Processor(i) for i in range(n_procs)]
    topo_mgr = ParallelismManager(
        processors,
        config.parallelism.TP,
        config.parallelism.DP,
        config.parallelism.PP,
    )

    exp = ExperimentLayoutGenerator(processors,
                                    config.parallelism.TP, config.parallelism.DP,
                                    config.parallelism.PP, config.cluster_topology.gpus_per_node
                                    )
    all_layouts = exp.generate_all_permutations()
    best_time = float('inf')
    best_layout = None

    for layout, nodes in all_layouts.items():
        result_time = run_iteration_of_experiment(layout, config, output_path, topo_mgr, nodes)
        if result_time < best_time:
            best_time = result_time
            best_layout = layout

    print(f"Best simulation time : {best_time:.6e} s")
    print(f"Best layout         : {best_layout}")
    # TODO add saving best layout information to the output path as well
