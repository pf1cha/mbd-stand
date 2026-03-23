from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.network_topology.base_topology import BaseTopology
from lib.src.network_lib.network_topology.fat_tree import FatTreeTopology
from lib.src.network_lib.network_topology.spine_leaf import SpineLeafTopology


def _build_topology(topology_cfg):
    topo_type = topology_cfg.type.lower().replace("-", "_").replace(" ", "_")

    if topo_type == "spine_leaf":
        sl = topology_cfg.spine_leaf
        return SpineLeafTopology(sl)

    elif topo_type == "fat_tree":
        ft = topology_cfg.fat_tree
        return FatTreeTopology(ft)

    else:
        raise ValueError(
            f"Unknown topology type '{topology_cfg.type}'. "
            "Supported values: 'spine_leaf', 'fat_tree'."
        )


def create_topology(topology_cfg, processors):
    topology = _build_topology(topology_cfg)
    topology.assign_processors_sequential(processors)
    return topology


def create_topology_from_nodes(topology_cfg, nodes_array):
    topology = _build_topology(topology_cfg)
    topology.assign_processors_to_nodes(nodes_array)
    return topology
