import enum


class Primitives(enum.Enum):
    ALL_GATHER = "AllGather",
    ALL_REDUCE = "AllReduce",
    REDUCE_SCATTER = "ReduceScatter",
    P2P = "P2P" # Maybe, it's not appropriate name for this primitive, but it will be used as a placeholder for now.

    @classmethod
    def from_string(cls, value: str):
        normalized = value.lower().replace("_", "-").replace(" ", "-")
        aliases = {
            "allreduce": Primitives.ALL_REDUCE,
            "allgather": Primitives.ALL_GATHER,
            "reducescatter": Primitives.REDUCE_SCATTER,
            "p2p": Primitives.P2P,
        }
        try:
            return aliases[normalized]
        except KeyError:
            valid = ", ".join(sorted(aliases.keys()))
            raise ValueError(
                f"Unknown method '{value}'. "
                f"Valid options are: {valid}. "
                "Input is case-insensitive and may use '-', '_' or spaces."
            )
