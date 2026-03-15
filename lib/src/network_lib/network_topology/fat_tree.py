from lib.src.network_lib.network_topology.base_topology import BaseTopology, CommunicationLevel
from lib.src.network_lib.model.processor import Processor


class FatTreeTopology(BaseTopology):
    _HOP_MAP = {
        CommunicationLevel.INTRA_NODE: 0,
        CommunicationLevel.INTRA_RACK: 2,
        CommunicationLevel.INTER_RACK: 4,
        CommunicationLevel.INTER_POD: 6,
    }

    def __init__(self, k, gpus_per_node, intra_node_latency, intra_node_bandwidth,
                 intra_rack_latency, intra_rack_bandwidth, inter_rack_latency,
                 inter_rack_bandwidth, inter_pod_latency, inter_pod_bandwidth
    ):
        if k % 2 != 0:
            raise ValueError(f"k must be even for a fat-tree topology, got k={k}.")

        self.k = k
        half_k = k // 2

        self.num_pods = k
        self.edge_per_pod = half_k
        self.agg_per_pod = half_k
        self.num_core = half_k ** 2
        self.servers_per_edge = half_k
        self.servers_per_pod = half_k * half_k

        self._level_params = {
            CommunicationLevel.INTRA_NODE: (intra_node_latency, intra_node_bandwidth),
            CommunicationLevel.INTRA_RACK: (intra_rack_latency, intra_rack_bandwidth),
            CommunicationLevel.INTER_RACK: (inter_rack_latency, inter_rack_bandwidth),
            CommunicationLevel.INTER_POD: (inter_pod_latency, inter_pod_bandwidth),
        }

        super().__init__(gpus_per_node)
        self._node_to_pod = {}
        for pod in range(self.num_pods):
            for rack_in_pod in range(self.edge_per_pod):
                for srv in range(self.servers_per_edge):
                    node_id = (pod * self.servers_per_pod
                               + rack_in_pod * self.servers_per_edge
                               + srv)
                    global_rack = pod * self.edge_per_pod + rack_in_pod
                    self._node_to_rack[node_id] = global_rack
                    self._node_to_pod[node_id] = pod

    def total_gpus(self):
        return self.num_pods * self.servers_per_pod * self.gpus_per_node

    def get_pod_id(self, processor):
        return self._node_to_pod[self.get_node_id(processor)]

    def get_communication_level(self, proc_a, proc_b):
        if str(proc_a.uuid) == str(proc_b.uuid):
            return CommunicationLevel.INTRA_NODE
        node_a = self.get_node_id(proc_a)
        node_b = self.get_node_id(proc_b)
        if node_a == node_b:
            return CommunicationLevel.INTRA_NODE
        if self._node_to_rack[node_a] == self._node_to_rack[node_b]:
            return CommunicationLevel.INTRA_RACK
        if self._node_to_pod[node_a] == self._node_to_pod[node_b]:
            return CommunicationLevel.INTER_RACK
        return CommunicationLevel.INTER_POD

    def get_path_hops(self, proc_a, proc_b):
        return self._HOP_MAP[self.get_communication_level(proc_a, proc_b)]

    def get_level_params(self, level):
        if level not in self._level_params:
            raise ValueError(
                f"Level '{level.value}' is not available in FatTreeTopology. "
                f"Available: {[l.value for l in self._level_params]}"
            )
        return self._level_params[level]

    def get_capacity(self, level):
        if level == CommunicationLevel.INTRA_NODE:
            return self.gpus_per_node
        if level == CommunicationLevel.INTRA_RACK:
            return self.servers_per_edge * self.gpus_per_node
        if level == CommunicationLevel.INTER_RACK:
            return self.servers_per_pod * self.gpus_per_node
        if level == CommunicationLevel.INTER_POD:
            return self.total_gpus
        raise ValueError(
            f"Level '{level.value}' is not supported by FatTreeTopology."
        )

    def get_available_levels(self):
        return [
            CommunicationLevel.INTRA_NODE,
            CommunicationLevel.INTRA_RACK,
            CommunicationLevel.INTER_RACK,
            CommunicationLevel.INTER_POD,
        ]

    def __repr__(self):
        total_racks = self.num_pods * self.edge_per_pod
        return (
            f"FatTreeTopology("
            f"k={self.k}, pods={self.num_pods}, "
            f"racks={total_racks}, "
            f"gpus/node={self.gpus_per_node}, "
            f"total={self.total_gpus} GPUs)"
        )
