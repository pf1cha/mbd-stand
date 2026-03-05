import json
import yaml
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union
from pathlib import Path
from lib.src.network_lib.utils.methods import *
from lib.src.network_lib.utils.primitives import *


@dataclass
class ParallelismConfig:
    TP: int
    PP: int
    DP: int


@dataclass
class DataConfig:
    size: int


@dataclass
class SingleNetworkConfig:
    latency: float
    bandwidth: float
    where: Optional[List[str]] = None


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
                raise ValueError(f"Invalid 'who' value: {self.who}. Must be one of 'tp', 'dp', or 'pp'.")


@dataclass
class AppConfig:
    parallelism: ParallelismConfig
    data: DataConfig
    networks: List[SingleNetworkConfig] = field(default_factory=list)
    collective_communication: List[CollectiveOp] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.parallelism, dict):
            self.parallelism = ParallelismConfig(**self.parallelism)

        if isinstance(self.data, dict):
            self.data = DataConfig(**self.data)

        if len(self.networks) > 1:
            all_where = []
            for net in self.networks:
                if net.where is None:
                    raise ValueError("Field 'where' is required when multiple networks are defined.")
                all_where.extend(net.where)
            seen = set()
            duplicates = set()
            for w in all_where:
                if w in seen:
                    duplicates.add(w)
                seen.add(w)
            if duplicates:
                raise ValueError(f"Duplicate values in 'where' across networks: {list(duplicates)}")

        if self.collective_communication and isinstance(self.collective_communication[0], dict):
            self.collective_communication = [
                CollectiveOp(**item) for item in self.collective_communication
            ]

        if self.collective_communication and isinstance(self.collective_communication[0], dict):
            self.collective_communication = [
                CollectiveOp(**item) for item in self.collective_communication
            ]

        for step in self.collective_communication:
            if step.who == "tp" and self.parallelism.TP == 1:
                raise ValueError(f"Collective operation {step.type} is specified for TP but TP=1 in config. "
                                 f"If you want to use TP specify it in 'parallelism' section of config.")
            if step.who == "dp" and self.parallelism.DP == 1:
                raise ValueError(f"Collective operation {step.type} is specified for DP but DP=1 in config."
                                 f"If you want to use DP specify it in 'parallelism' section of config.")

        if self.parallelism.TP == 1:
            for step in self.collective_communication:
                if step.type != Primitives.P2P:
                    step.who = "dp"
        if self.parallelism.DP == 1:
            for step in self.collective_communication:
                if step.type != Primitives.P2P:
                    step.who = "tp"

        if self.parallelism.TP == 1 or self.parallelism.DP == 1:
            new_receiver = 'dp' if self.parallelism.TP == 1 else 'tp'
            for step in self.collective_communication:
                if step.type == Primitives.P2P:
                    continue
                step.who = new_receiver

    @classmethod
    def load(cls, path: str | Path) -> "AppConfig":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError("Unsupported file format. Use .json or .yaml")

        networks_data = data.pop('networks', [])
        if isinstance(networks_data, dict):
            if 'latency' in networks_data and 'bandwidth' in networks_data:
                data['networks'] = [SingleNetworkConfig(**networks_data)]
            else:
                data['networks'] = [
                    SingleNetworkConfig(**v) for v in networks_data.values()
                ]
        elif isinstance(networks_data, list):
            data['networks'] = [SingleNetworkConfig(**item) for item in networks_data]

        return cls(**data)
