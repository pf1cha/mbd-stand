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
        # TODO change all those parameters to one config
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

    def print_structure(self):
        total_racks = self.num_pods * self.edge_per_pod
        sep = "-" * 60
        print(f"\n  {sep}")
        print(f"  Topology   : Fat-Tree  (k={self.k})")
        print(f"  {sep}")
        print(f"  Pods                : {self.num_pods}")
        print(f"  Edge switches/pod   : {self.edge_per_pod}")
        print(f"  Agg switches/pod    : {self.agg_per_pod}")
        print(f"  Core switches       : {self.num_core}")
        print(f"  Total racks         : {total_racks}")
        print(f"  Servers/rack        : {self.servers_per_edge}")
        print(f"  GPUs/server         : {self.gpus_per_node}")
        print(f"  Total GPUs          : {self.total_gpus}")
        print(f"  Total servers       : {total_racks * self.servers_per_edge}")
        print(f"  {sep}")
        print(f"  {'Level':<18}  {'Latency':>12}  {'Bandwidth':>12}  {'Hops':>5}  {'Capacity':>10}")
        print(f"  {'-' * 18}  {'-' * 12}  {'-' * 12}  {'-' * 5}  {'-' * 10}")
        for level in self.get_available_levels():
            lat, bw = self._level_params[level]
            hops = self._HOP_MAP[level]
            cap = self.get_capacity(level)
            print(
                f"  {level.label():<18}  "
                f"{lat:>9.6f} µs  "
                f"{bw:>9.1f} GB/s  "
                f"{hops:>5}  "
                f"{cap:>8} GPUs"
            )
        print(f"  {sep}")
        print(f"  Pod / Rack structure:")
        for pod_id in range(self.num_pods):
            rack_ids = [
                r for n, r in self._node_to_rack.items()
                if self._node_to_pod.get(n) == pod_id
            ]
            unique_racks = sorted(set(rack_ids))
            print(f"    pod={pod_id:2d}  racks: {unique_racks}")
        print(f"  {sep}\n")

    def __repr__(self):
        total_racks = self.num_pods * self.edge_per_pod
        return (
            f"FatTreeTopology("
            f"k={self.k}, pods={self.num_pods}, "
            f"racks={total_racks}, "
            f"gpus/node={self.gpus_per_node}, "
            f"total={self.total_gpus} GPUs)"
        )
