class Network:
    def __init__(self, bandwidth, latency, processors):
        self.bandwidth = bandwidth
        self.latency = latency
        self.processors = processors


class NetworkManager:
    def __init__(self, net_config, topology_config):
        self.networks = {'tp': [], 'dp': [], 'pp': []}
        self._init_group_network_processor(net_config, topology_config.tp_groups,
                                           topology_config.dp_groups,
                                           topology_config.pp_pipes)

    def _init_group_network_processor(self, net_config, tp_groups, dp_groups, pp_pipes):
        for net in net_config:
            if "tp" in net.where:
                for group in tp_groups:
                    temp = Network(net.bandwidth, net.latency, group)
                    self.networks['tp'].append(temp)
            elif "dp" in net.where:
                for group in dp_groups:
                    temp = Network(net.bandwidth, net.latency, group)
                    self.networks['dp'].append(temp)
            elif "pp" in net.where:
                for pipe in pp_pipes:
                    temp = Network(net.bandwidth, net.latency, pipe)
                    self.networks['pp'].append(temp)

    def get_networks_by_type(self, parallelism_type):
        return self.networks.get(parallelism_type, [])
