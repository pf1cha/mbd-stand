import enum

class Primitives(enum.Enum):
    ALL_GATHER = 1,
    ALL_REDUCE = 2,
    REDUCE_SCATTER = 3,
    BROADCAST = 4 # Maybe change to