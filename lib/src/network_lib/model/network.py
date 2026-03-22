# TODO fix that class. Make it more logical


class Network:
    def __init__(
            self,
            processors,
            cluster_topology=None,
            override_latency=None,
            override_bandwidth=None,
    ):
        if cluster_topology is None:
            if override_latency is None or override_bandwidth is None:
                raise ValueError(
                    "Network requires either a cluster_topology for per-pair routing "
                    "or both override_latency and override_bandwidth for flat mode."
                )
        self.processors = processors
        self._cluster_topology = cluster_topology
        self._override_latency = override_latency
        self._override_bandwidth = override_bandwidth

    def get_transfer_params(self, src, dst):
        if self._cluster_topology is not None:
            latency = self._cluster_topology.get_latency(src, dst)
            bandwidth = self._cluster_topology.get_bandwidth(src, dst)
            return bandwidth, latency
        return self._override_bandwidth, self._override_latency

    def describe(self, src, dst):
        if self._cluster_topology is not None:
            return self._cluster_topology.describe_path(src, dst)
        return (
            f"Override mode | "
            f"Latency: {self._override_latency * 1e6:.2f} µs | "
            f"Bandwidth: {self._override_bandwidth / 1e9:.1f} GB/s"
        )


class NetworkManager:
    def __init__(self, topology_config, network_groups, cluster_topology, override_params=None):
        self.networks = {'tp': [], 'dp': [], 'pp': []}

        group_map = {
            'tp': topology_config.tp_groups,
            'dp': topology_config.dp_groups,
            'pp': topology_config.pp_pipes,
        }
        overrides = override_params or {}

        for par_type in network_groups:
            groups = group_map.get(par_type)
            if not groups:
                continue

            if par_type in overrides:
                lat, bw = overrides[par_type]
                for group in groups:
                    self.networks[par_type].append(
                        Network(group, override_latency=lat, override_bandwidth=bw)
                    )
            else:
                for group in groups:
                    self.networks[par_type].append(
                        Network(group, cluster_topology=cluster_topology)
                    )

    def get_networks_by_type(self, parallelism_type):
        return self.networks.get(parallelism_type, [])
