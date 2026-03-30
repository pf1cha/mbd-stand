import json
import yaml
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from lib.src.network_lib.enums.methods import *
from lib.src.network_lib.enums.primitives import *


@dataclass
class ParallelismConfig:
    TP: int
    PP: int
    DP: int


@dataclass
class DataConfig:
    size: int


@dataclass
class CollectiveOp:
    type: Primitives
    algorithm: Optional[Method] = None
    who: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = Primitives.from_string(self.type)
        if isinstance(self.algorithm, str):
            self.algorithm = Method.from_string(self.algorithm)
        if isinstance(self.who, str):
            self.who = self.who.lower()
            if self.who not in ['tp', 'dp', 'pp']:
                raise ValueError(
                    f"Invalid 'who' value: '{self.who}'. Must be one of 'tp', 'dp', 'pp'."
                )


@dataclass
class SingleNetworkConfig:
    latency: float
    bandwidth: float
    where: Optional[List[str]] = None


@dataclass
class SpineLeafNetworkConfig:
    num_spine: int
    num_leaf: int
    servers_per_leaf: int
    intra_node_latency: float
    intra_node_bandwidth: float
    intra_rack_latency: float
    intra_rack_bandwidth: float
    inter_rack_latency: float
    inter_rack_bandwidth: float


@dataclass
class FatTreeNetworkConfig:
    k: int
    intra_node_latency: float
    intra_node_bandwidth: float
    intra_rack_latency: float
    intra_rack_bandwidth: float
    inter_rack_latency: float
    inter_rack_bandwidth: float
    inter_pod_latency: float
    inter_pod_bandwidth: float


@dataclass
class ClusterTopologyConfig:
    type: str
    gpus_per_node: int
    spine_leaf: Optional[SpineLeafNetworkConfig] = None
    fat_tree: Optional[FatTreeNetworkConfig] = None

    def __post_init__(self):
        if isinstance(self.spine_leaf, dict):
            self.spine_leaf = SpineLeafNetworkConfig(**self.spine_leaf)
        if isinstance(self.fat_tree, dict):
            self.fat_tree = FatTreeNetworkConfig(**self.fat_tree)

        topo_type = self.type.lower().replace("-", "_").replace(" ", "_")
        if topo_type not in ("spine_leaf", "fat_tree"):
            raise ValueError(
                f"Unknown topology type '{self.type}'. "
                "Supported values: 'spine_leaf', 'fat_tree'."
            )
        if topo_type == "spine_leaf" and self.spine_leaf is None:
            raise ValueError(
                "cluster_topology.type is 'spine_leaf' but the 'spine_leaf' "
                "sub-section is missing from the config."
            )
        if topo_type == "fat_tree" and self.fat_tree is None:
            raise ValueError(
                "cluster_topology.type is 'fat_tree' but the 'fat_tree' "
                "sub-section is missing from the config."
            )


@dataclass
class AppConfig:
    parallelism: ParallelismConfig
    data: DataConfig
    cluster_topology: ClusterTopologyConfig  # REQUIRED
    collective_communication: List[CollectiveOp] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.parallelism, dict):
            self.parallelism = ParallelismConfig(**self.parallelism)

        if isinstance(self.data, dict):
            self.data = DataConfig(**self.data)

        if isinstance(self.cluster_topology, dict):
            self.cluster_topology = ClusterTopologyConfig(**self.cluster_topology)

        if self.collective_communication and isinstance(
                self.collective_communication[0], dict
        ):
            self.collective_communication = [
                CollectiveOp(**item) for item in self.collective_communication
            ]

        for step in self.collective_communication:
            if step.type == Primitives.P2P and step.who is None:
                step.who = 'pp'
            if step.who == "tp" and self.parallelism.TP == 1:
                raise ValueError(
                    f"Collective op '{step.type.name}' targets 'tp' but TP=1 in config. "
                    "Either set TP > 1 in parallelism or change 'who'."
                )
            if step.who == "dp" and self.parallelism.DP == 1:
                raise ValueError(
                    f"Collective op '{step.type.name}' targets 'dp' but DP=1 in config. "
                    "Either set DP > 1 in parallelism or change 'who'."
                )

        if self.parallelism.TP == 1 or self.parallelism.DP == 1:
            redirect_to = 'dp' if self.parallelism.TP == 1 else 'tp'
            for step in self.collective_communication:
                if step.type != Primitives.P2P:
                    step.who = redirect_to

    @classmethod
    def load(cls, path: str | Path) -> "AppConfig":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, 'r') as f:
            if path.suffix in ('.yaml', '.yml'):
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(
                    f"Unsupported config format '{path.suffix}'. "
                    "Use .yaml / .yml or .json."
                )

        if 'cluster_topology' not in data:
            raise ValueError(
                "Missing required field 'cluster_topology' in config file.\n"
                "Every config must define the physical cluster topology.\n"
            )

        return cls(**data)
