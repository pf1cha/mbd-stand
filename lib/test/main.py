from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.model.network import Network
from lib.src.network_lib.utils.methods import Method
from lib.src.network_lib.utils.primitives import Primitives
from lib.src.network_lib.model.model import Model
from lib.test.helper import count_events_in_json

if __name__ == '__main__':
    filename_stats = "lib/results/complex_simulation_stats.json"
    processors = [Processor() for _ in range(2 ** 2)]
    network = Network(6, 0.2, processors)

    # Example of array of events:
    events = [(Primitives.ALL_REDUCE, Method.HALVING_DOUBLING),
              (Primitives.ALL_GATHER, Method.RING),
              (Primitives.REDUCE_SCATTER, Method.RING)]

    simulation = Model(network, events, 1600)
    simulation.process(filename_stats)

    count_events_in_json(filename_stats)
