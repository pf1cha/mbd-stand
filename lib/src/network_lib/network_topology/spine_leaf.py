from lib.src.network_lib.network_topology.base_topology import BaseTopology, CommunicationLevel
from lib.src.network_lib.model.processor import Processor


class SpineLeafTopology(BaseTopology):
    _HOP_MAP = {
        CommunicationLevel.INTRA_NODE: 0,
        CommunicationLevel.INTRA_RACK: 2,
        CommunicationLevel.INTER_RACK: 4,
    }

    def __init__(
            self,
            num_spine,
            num_leaf,
            servers_per_leaf,
            gpus_per_node,
            intra_node_latency,
            intra_node_bandwidth,
            intra_rack_latency,
            intra_rack_bandwidth,
            inter_rack_latency,
            inter_rack_bandwidth,
    ):
        self.num_spine = num_spine
        self.num_leaf = num_leaf
        self.servers_per_leaf = servers_per_leaf
        self._level_params = {
            CommunicationLevel.INTRA_NODE: (intra_node_latency, intra_node_bandwidth),
            CommunicationLevel.INTRA_RACK: (intra_rack_latency, intra_rack_bandwidth),
            CommunicationLevel.INTER_RACK: (inter_rack_latency, inter_rack_bandwidth),
        }
        super().__init__(gpus_per_node)

        for leaf_id in range(num_leaf):
            for srv in range(servers_per_leaf):
                node_id = leaf_id * servers_per_leaf + srv
                self._node_to_rack[node_id] = leaf_id

    def total_gpus(self):
        return self.num_leaf * self.servers_per_leaf * self.gpus_per_node

    def get_communication_level(self, proc_a, proc_b):
        if str(proc_a.uuid) == str(proc_b.uuid):
            return CommunicationLevel.INTRA_NODE
        node_a = self.get_node_id(proc_a)
        node_b = self.get_node_id(proc_b)
        if node_a == node_b:
            return CommunicationLevel.INTRA_NODE
        if self._node_to_rack[node_a] == self._node_to_rack[node_b]:
            return CommunicationLevel.INTRA_RACK
        return CommunicationLevel.INTER_RACK

    def get_path_hops(self, proc_a, proc_b):
        return self._HOP_MAP[self.get_communication_level(proc_a, proc_b)]

    def get_level_params(self, level):
        if level not in self._level_params:
            raise ValueError(
                f"Level '{level.value}' is not available in SpineLeafTopology. "
                f"Available: {[l.value for l in self._level_params]}"
            )
        return self._level_params[level]

    def get_capacity(self, level):
        if level == CommunicationLevel.INTRA_NODE:
            return self.gpus_per_node
        if level == CommunicationLevel.INTRA_RACK:
            return self.servers_per_leaf * self.gpus_per_node
        if level == CommunicationLevel.INTER_RACK:
            return self.total_gpus
        raise ValueError(
            f"Level '{level.value}' is not supported by SpineLeafTopology."
        )

    def get_available_levels(self):
        return [
            CommunicationLevel.INTRA_NODE,
            CommunicationLevel.INTRA_RACK,
            CommunicationLevel.INTER_RACK,
        ]

    def __repr__(self):
        return (
            f"SpineLeafTopology("
            f"spine={self.num_spine}, leaf={self.num_leaf}, "
            f"srv/leaf={self.servers_per_leaf}, "
            f"gpus/node={self.gpus_per_node}, "
            f"total={self.total_gpus} GPUs)"
        )