from lib.src.network_lib.model.processor import Processor
from typing import List, Optional


class TopologyManager:
    def __init__(self, processors: List[Processor], tp: int, dp: int, pp: int):
        if len(processors) != tp * dp * pp:
            raise ValueError("The number of processors should be equal to tp * dp * pp")
        self.processors = processors
        self.tp = tp
        self.dp = dp
        self.pp = pp
        self.tp_groups: Optional[List[List[Processor]]] = None
        self.dp_groups: Optional[List[List[Processor]]] = None
        self.pp_pipes: Optional[List[List[Processor]]] = None

        self.get_groups()

    def get_groups(self):
        self.tp_groups = self._build_groups_if_needed(self.tp, self._build_tp_groups)
        self.dp_groups = self._build_groups_if_needed(self.dp, self._build_dp_groups)
        self.pp_pipes = self._build_groups_if_needed(self.pp, self._build_pp_pipes)

    def _build_groups_if_needed(self, size: int, builder_func):
        return builder_func() if size > 1 else None

    def _build_tp_groups(self):
        return [
            [self.processors[d * self.pp * self.tp + p * self.tp + t]
            for t in range(self.tp)]
            for d in range(self.dp)
            for p in range(self.pp)
        ]

    def _build_dp_groups(self):
        return [
            [self.processors[d * self.pp * self.tp + p * self.tp + t]
            for d in range(self.dp)]
            for p in range(self.pp)
            for t in range(self.tp)
        ]

    def _build_pp_pipes(self):
        return [
            [self.processors[d * self.pp * self.tp + p * self.tp + t]
            for p in range(self.pp)]
            for d in range(self.dp)
            for t in range(self.tp)
        ]