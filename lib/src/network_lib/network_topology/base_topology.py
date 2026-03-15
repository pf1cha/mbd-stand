from enum import Enum
from lib.src.network_lib.model.processor import Processor


class CommunicationLevel(Enum):
    INTRA_NODE = "intra_node"
    INTRA_RACK = "intra_rack"
    INTER_RACK = "inter_rack"
    INTER_POD = "inter_pod"

    def label(self):
        _labels = {
            CommunicationLevel.INTRA_NODE: "Within Node",
            CommunicationLevel.INTRA_RACK: "Within Rack",
            CommunicationLevel.INTER_RACK: "Between Racks",
            CommunicationLevel.INTER_POD: "Between Pods",
        }
        return _labels[self]


class BaseTopology:
    def __init__(self, gpus_per_node):
        self.gpus_per_node = gpus_per_node
        self._processor_to_node = {}
        self._node_to_rack = {}
        self.total_gpus = self.total_gpus()

    def assign_processor(self, processor, node_id):
        self._processor_to_node[str(processor.uuid)] = node_id

    def assign_processors_sequential(self, processors):
        if len(processors) > self.total_gpus:
            raise ValueError(
                f"Cannot assign {len(processors)} processors: topology capacity "
                f"is {self.total_gpus} GPUs."
            )
        for i, proc in enumerate(processors):
            self.assign_processor(proc, i // self.gpus_per_node)

    def assign_processors_custom(self, uuid_to_node):
        # TODO not working
        invalid = [
            (uuid, node_id)
            for uuid, node_id in uuid_to_node.items()
            if node_id not in self._node_to_rack
        ]
        if invalid:
            bad_nodes = sorted({n for _, n in invalid})
            raise ValueError(
                f"Custom assignment references node IDs that do not exist in "
                f"this topology: {bad_nodes}.\n"
                f"Valid node range: 0 – {max(self._node_to_rack)}"
            )
        self._processor_to_node.update(uuid_to_node)

    def get_node_id(self, processor):
        key = str(processor.uuid)
        if key not in self._processor_to_node:
            raise KeyError(
                f"Processor {key} has not been assigned to this topology. "
                "Call assign_processors_sequential first."
            )
        return self._processor_to_node[key]

    def total_gpus(self):
        pass

    def get_communication_level(self, proc_a, proc_b):
        pass

    def get_path_hops(self, proc_a, proc_b):
        pass

    def get_level_params(self, level):
        pass

    def get_latency(self, proc_a, proc_b):
        return self.get_level_params(self.get_communication_level(proc_a, proc_b))[0]

    def get_bandwidth(self, proc_a, proc_b):
        return self.get_level_params(self.get_communication_level(proc_a, proc_b))[1]

    def describe_path(self, proc_a, proc_b):
        level = self.get_communication_level(proc_a, proc_b)
        hops = self.get_path_hops(proc_a, proc_b)
        latency, bw = self.get_level_params(level)
        return (
            f"Level: {level.label():20s} | "
            f"Hops: {hops} | "
            f"Latency: {latency * 1e6:7.2f} µs | "
            f"Bandwidth: {bw / 1e9:8.1f} GB/s"
        )
