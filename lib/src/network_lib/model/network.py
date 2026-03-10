class Network:
    def __init__(self, bandwidth, latency, processors):
        self.bandwidth = bandwidth
        self.latency = latency
        self.processors = processors


class NetworkManager:
    def __init__(self, net_config, topology_config, network_groups):
        self.networks = {'tp': [], 'dp': [], 'pp': []}
        self._init_group_network_processor(net_config, topology_config.tp_groups,
                                           topology_config.dp_groups,
                                           topology_config.pp_pipes, network_groups)

    def _init_group_network_processor(self, net_config, tp_groups, dp_groups, pp_pipes, network_groups):
        for net in net_config:
            for t in network_groups:
                groups = None
                if t == "tp":
                    groups = tp_groups
                elif t == "dp":
                    groups = dp_groups
                elif t == "pp":
                    groups = pp_pipes
                for group in groups:
                    temp = Network(net.bandwidth, net.latency, group)
                    self.networks[t].append(temp)

    def get_networks_by_type(self, parallelism_type):
        return self.networks.get(parallelism_type, [])
