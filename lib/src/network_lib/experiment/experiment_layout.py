from itertools import permutations


class ExperimentLayoutGenerator:
    def __init__(self, processors, tp, dp, pp, gpus_per_node):
        self.processors = processors
        self.tp = tp
        self.dp = dp
        self.pp = pp
        self.gpus_per_node = gpus_per_node

        expected_total = tp * dp * pp
        if len(processors) != expected_total:
            raise ValueError(f"The number of processors ({len(processors)}) is not the same as "
                             f"tp*dp*pp ({expected_total})")

    def _get_processor_by_indices(self, d, p, t):
        idx = d * (self.pp * self.tp) + p * self.tp + t
        return self.processors[idx]

    def _generate_1d_layout(self, priority_order):
        sizes = {'tp': self.tp, 'dp': self.dp, 'pp': self.pp}
        outer_dim = priority_order[2]
        middle_dim = priority_order[1]
        inner_dim = priority_order[0]
        layout_1d = []
        for outer_idx in range(sizes[outer_dim]):
            for middle_idx in range(sizes[middle_dim]):
                for inner_idx in range(sizes[inner_dim]):
                    indices = {
                        outer_dim: outer_idx,
                        middle_dim: middle_idx,
                        inner_dim: inner_idx
                    }
                    d = indices['dp']
                    p = indices['pp']
                    t = indices['tp']
                    layout_1d.append(self._get_processor_by_indices(d, p, t))

        return layout_1d

    def _chunk_into_nodes(self, layout_1d):
        nodes_2d = []
        for i in range(0, len(layout_1d), self.gpus_per_node):
            nodes_2d.append(layout_1d[i:i + self.gpus_per_node])
        return nodes_2d

    def generate_all_permutations(self, dimensions=None):
        if dimensions is None:
            dimensions = ['tp', 'dp', 'pp']
        all_layouts = {}

        for perm in permutations(dimensions):
            layout_1d = self._generate_1d_layout(perm)
            nodes_2d = self._chunk_into_nodes(layout_1d)
            name = f"{perm[0].upper()} -> {perm[1].upper()} -> {perm[2].upper()}"
            all_layouts[name] = nodes_2d

        return all_layouts
