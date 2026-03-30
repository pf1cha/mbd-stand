from enum import Enum


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
