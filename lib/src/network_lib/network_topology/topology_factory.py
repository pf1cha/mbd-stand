from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.network_topology.base_topology import BaseTopology
from lib.src.network_lib.network_topology.fat_tree import FatTreeTopology
from lib.src.network_lib.network_topology.spine_leaf import SpineLeafTopology


def _build_topology(topology_cfg):
    topo_type = topology_cfg.type.lower().replace("-", "_").replace(" ", "_")

    if topo_type == "spine_leaf":
        sl = topology_cfg.spine_leaf
        return SpineLeafTopology(
            num_spine=sl.num_spine,
            num_leaf=sl.num_leaf,
            servers_per_leaf=sl.servers_per_leaf,
            gpus_per_node=topology_cfg.gpus_per_node,
            intra_node_latency=sl.intra_node_latency,
            intra_node_bandwidth=sl.intra_node_bandwidth,
            intra_rack_latency=sl.intra_rack_latency,
            intra_rack_bandwidth=sl.intra_rack_bandwidth,
            inter_rack_latency=sl.inter_rack_latency,
            inter_rack_bandwidth=sl.inter_rack_bandwidth,
        )

    elif topo_type == "fat_tree":
        ft = topology_cfg.fat_tree
        return FatTreeTopology(
            k=ft.k,
            gpus_per_node=topology_cfg.gpus_per_node,
            intra_node_latency=ft.intra_node_latency,
            intra_node_bandwidth=ft.intra_node_bandwidth,
            intra_rack_latency=ft.intra_rack_latency,
            intra_rack_bandwidth=ft.intra_rack_bandwidth,
            inter_rack_latency=ft.inter_rack_latency,
            inter_rack_bandwidth=ft.inter_rack_bandwidth,
            inter_pod_latency=ft.inter_pod_latency,
            inter_pod_bandwidth=ft.inter_pod_bandwidth,
        )

    else:
        raise ValueError(
            f"Unknown topology type '{topology_cfg.type}'. "
            "Supported values: 'spine_leaf', 'fat_tree'."
        )


def create_topology(topology_cfg, processors):
    topology = _build_topology(topology_cfg)
    topology.assign_processors_sequential(processors)
    return topology


def create_topology_unassigned(topology_cfg):
    return _build_topology(topology_cfg)
