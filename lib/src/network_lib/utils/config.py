import json
import yaml
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from lib.src.network_lib.utils.methods import *


@dataclass
class ParallelismConfig:
    TP: int
    PP: int
    DP: int


@dataclass
class DataConfig:
    size: int


@dataclass
class NetworkConfig:
    latency: float
    bandwidth: float


@dataclass
class CollectiveOp:
    type: Method
    algorithm: Optional[Method] = None

    def __post_init__(self):
        if isinstance(self.algorithm, str):
            self.algorithm = Method.from_string(self.algorithm)



@dataclass
class AppConfig:
    parallelism: ParallelismConfig
    data: DataConfig
    network: NetworkConfig
    collective_communication: List[CollectiveOp]

    def __post_init__(self):
        if isinstance(self.parallelism, dict):
            self.parallelism = ParallelismConfig(**self.parallelism)

        if isinstance(self.data, dict):
            self.data = DataConfig(**self.data)

        if isinstance(self.network, dict):
            self.network = NetworkConfig(**self.network)

        if self.collective_communication and isinstance(self.collective_communication[0], dict):
            self.collective_communication = [
                CollectiveOp(**item) for item in self.collective_communication
            ]
            # TODO change type of op.type from str to Method



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

        return cls(**data)
