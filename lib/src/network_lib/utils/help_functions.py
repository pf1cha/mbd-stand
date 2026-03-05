from lib.src.network_lib.enums.methods import Method
from numpy import log2


def count_steps(method, processors_length):
    """ TODO Maybe add an event parameter to the function,
    which will help to calculate the number of steps in one function"""
    if method == Method.RING:
        return processors_length - 1
    elif method == Method.HALVING_DOUBLING:
        if processors_length % 2 != 0:
            return None
        return log2(processors_length)
    else:
        return 0
