from enum import Enum
from collections import defaultdict


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

    def assign_processors_to_nodes(self, nodes):
        self._processor_to_node.clear()

        if len(nodes) > len(self._node_to_rack):

            raise ValueError(
                f"Невозможно назначить {len(nodes)} узлов: в текущей топологии "
                f"всего {len(self._node_to_rack)} доступных узлов."
            )

        for node_id, processors_in_node in enumerate(nodes):
            if len(processors_in_node) > self.gpus_per_node:
                raise ValueError(
                    f"В узле {node_id} находится {len(processors_in_node)} процессоров, "
                    f"но топология поддерживает максимум {self.gpus_per_node} GPU на узел."
                )

            for proc in processors_in_node:
                self.assign_processor(proc, node_id)

    def assign_processors_sequential(self, processors):
        if len(processors) > self.total_gpus:
            raise ValueError(
                f"Cannot assign {len(processors)} processors: topology capacity "
                f"is {self.total_gpus} GPUs."
            )
        for i, proc in enumerate(processors):
            self.assign_processor(proc, i // self.gpus_per_node)

    def assign_processors_custom(self, uuid_to_node):
        self._processor_to_node.clear()
        cleaned_map = {str(uid): int(node_id) for uid, node_id in uuid_to_node.items()}

        invalid = [
            (uid, node_id)
            for uid, node_id in cleaned_map.items()
            if node_id not in self._node_to_rack
        ]

        if invalid:
            bad_nodes = sorted({n for _, n in invalid})
            raise ValueError(
                f"Custom assignment references node IDs that do not exist in "
                f"this topology: {bad_nodes}.\n"
                f"Valid node range: 0 – {max(self._node_to_rack.keys()) if self._node_to_rack else 'None'}"
            )

        self._processor_to_node.update(cleaned_map)

    def get_node_id(self, processor):
        key = str(processor.uuid)
        if key not in self._processor_to_node:
            raise KeyError(
                f"Processor {key} has not been assigned to this topology. "
                "Call assign_processors_sequential first."
            )
        return self._processor_to_node[key]

    def get_rack_id(self, processor):
        return self._node_to_rack[self.get_node_id(processor)]

    def get_node_to_rack_map(self):
        return dict(self._node_to_rack)

    def get_num_nodes(self):
        return len(self._node_to_rack)

    def total_gpus(self):
        pass

    def get_communication_level(self, proc_a, proc_b):
        pass

    def get_path_hops(self, proc_a, proc_b):
        pass

    def get_level_params(self, level):
        pass

    def print_structure(self):
        pass

    def print_node_assignment(self):
        if not self._processor_to_node:
            print("  [topology] No processors assigned yet.")
            return

        node_to_proc_uuids = defaultdict(list)
        for proc_uuid, node_id in self._processor_to_node.items():
            node_to_proc_uuids[node_id].append(proc_uuid)

        print("  Processor Assignment Layout:")
        print(f"  {'-' * 60}")
        for node_id in sorted(node_to_proc_uuids.keys()):
            rack_id = self._node_to_rack.get(node_id, -1)
            uuids_str = ", ".join(sorted(node_to_proc_uuids[node_id]))
            print(f"    node={node_id:3d}, rack={rack_id:3d}  |  processors (UUIDs): [{uuids_str}]")
        print(f"  {'-' * 60}\n")

    def print_full_info(self):
        self.print_structure()
        self.print_node_assignment()

    def get_latency(self, proc_a, proc_b):
        return self.get_level_params(self.get_communication_level(proc_a, proc_b))[0]

    def get_bandwidth(self, proc_a, proc_b):
        return self.get_level_params(self.get_communication_level(proc_a, proc_b))[1]

