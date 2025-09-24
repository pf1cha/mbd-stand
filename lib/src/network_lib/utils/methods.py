import enum


class Method(enum.Enum):
    RING = 1,
    HALVING_DOUBLING = 2,
    TREE = 3,
    BRUCK = 4,
    BUTTERFLY = 5

# TODO fix the methods because some of them are not necessary/important for my simulation