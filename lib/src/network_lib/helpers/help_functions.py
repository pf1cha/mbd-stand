from lib.src.primitives.methods import Method
from numpy import log2

def count_steps(method, gpu_size):
    if method == Method.RING:
        return gpu_size - 1
    elif method == Method.TREE:
        # TODO change to actual number of steps
        return gpu_size - 1
    elif method == Method.HALVING_DOUBLING:
        if gpu_size % 2 != 0:
            return None
        return log2(gpu_size)
    elif method == Method.BRUCK:
        # TODO change to actual number of steps
        return gpu_size - 1
    else:
        return 0


def max_time(gpu_cards, chunk_size):
    return max([gpu.latency + chunk_size / gpu.bandwidth for gpu in gpu_cards])
