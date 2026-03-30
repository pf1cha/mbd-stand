class ParallelismManager:
    def __init__(self, processors, tp, dp, pp):
        self.processors = processors
        self.tp = tp
        self.dp = dp
        self.pp = pp

        self.tp_groups = self._build_tp_groups() if tp > 1 else None
        self.dp_groups = self._build_dp_groups() if dp > 1 else None
        self.pp_pipes = self._build_pp_pipes() if pp > 1 else None

        self.get_groups()

    def get_groups(self):
        self.tp_groups = self._build_groups_if_needed(self.tp, self._build_tp_groups)
        self.dp_groups = self._build_groups_if_needed(self.dp, self._build_dp_groups)
        self.pp_pipes = self._build_groups_if_needed(self.pp, self._build_pp_pipes)

    def _build_groups_if_needed(self, size, builder_func):
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

    def print_groups(self):
        print(f"TP groups: {len(self.tp_groups) if self.tp_groups else 'N/A'}, "
              f"DP groups: {len(self.dp_groups) if self.dp_groups else 'N/A'}, "
              f"PP pipes: {len(self.pp_pipes) if self.pp_pipes else 'N/A'}")
        print("TP groups:")
        for i, group in enumerate(self.tp_groups or []):
            print(f"  Group {i}: {[str(proc.id) for proc in group]}")
        print("DP groups:")
        for i, group in enumerate(self.dp_groups or []):
            print(f"  Group {i}: {[str(proc.id) for proc in group]}")
        print("PP pipes:")
        for i, pipe in enumerate(self.pp_pipes or []):
            print(f"  Pipe {i}: {[str(proc.id) for proc in pipe]}")

    def get_groups_by_type(self, parallelism_type):
        mapping = {
            'tp': self.tp_groups,
            'dp': self.dp_groups,
            'pp': self.pp_pipes
        }
        return mapping.get(parallelism_type) or []
