from lib.src.network_lib.network_topology.base_topology import BaseTopology, CommunicationLevel


class SpineLeafTopology(BaseTopology):
    _HOP_MAP = {
        CommunicationLevel.INTRA_NODE: 0,
        CommunicationLevel.INTRA_RACK: 2,
        CommunicationLevel.INTER_RACK: 4,
    }

    def __init__(self, spine_leaf_config):
        self.num_spine = spine_leaf_config.num_spine
        self.num_leaf = spine_leaf_config.num_leaf
        self.servers_per_leaf = spine_leaf_config.servers_per_leaf

        self._level_params = {
            CommunicationLevel.INTRA_NODE: (spine_leaf_config.intra_node_latency, spine_leaf_config.intra_node_bandwidth),
            CommunicationLevel.INTRA_RACK: (spine_leaf_config.intra_rack_latency, spine_leaf_config.intra_rack_bandwidth),
            CommunicationLevel.INTER_RACK: (spine_leaf_config.inter_rack_latency, spine_leaf_config.inter_rack_bandwidth),
        }
        super().__init__(spine_leaf_config.gpus_per_node)

        for leaf_id in range(spine_leaf_config.num_leaf):
            for srv in range(spine_leaf_config.servers_per_leaf):
                node_id = leaf_id * spine_leaf_config.servers_per_leaf + srv
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

    def print_structure(self):
        sep = "-" * 60
        print(f"\n  {sep}")
        print(f"  Topology   : Spine-Leaf (Clos)")
        print(f"  {sep}")
        print(f"  Spine switches  : {self.num_spine}")
        print(f"  Leaf switches   : {self.num_leaf}  (= racks)")
        print(f"  Servers/rack    : {self.servers_per_leaf}")
        print(f"  GPUs/server     : {self.gpus_per_node}")
        print(f"  Total GPUs      : {self.total_gpus}")
        print(f"  Total servers   : {self.num_leaf * self.servers_per_leaf}")
        print(f"  {sep}")
        print(f"  {'Level':<18}  {'Latency':>12}  {'Bandwidth':>12}  {'Hops':>5}  {'Capacity':>10}")
        print(f"  {'-' * 18}  {'-' * 12}  {'-' * 12}  {'-' * 5}  {'-' * 10}")
        for level in self.get_available_levels():
            lat, bw = self._level_params[level]
            hops = self._HOP_MAP[level]
            cap = self.get_capacity(level)
            print(
                f"  {level.label():<18}  "
                f"{lat:>9.6f} s  "
                f"{bw:>9.1f} GB/s  "
                f"{hops:>5}  "
                f"{cap:>8} GPUs"
            )
        print(f"  {sep}")
        print(f"  Rack structure:")
        for rack_id in range(self.num_leaf):
            nodes = [
                n for n, r in self._node_to_rack.items() if r == rack_id
            ]
            print(f"    rack={rack_id:3d}  nodes: {sorted(nodes)}")
        print(f"  {sep}\n")

    def __repr__(self):
        return (
            f"SpineLeafTopology("
            f"spine={self.num_spine}, leaf={self.num_leaf}, "
            f"srv/leaf={self.servers_per_leaf}, "
            f"gpus/node={self.gpus_per_node}, "
            f"total={self.total_gpus} GPUs)"
        )
