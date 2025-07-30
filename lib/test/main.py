from lib.src.network_lib.handler.all_gather_handler import AllGatherStepHandler
from lib.src.network_lib.handler.all_reduce_handler import AllReduceStepHandler
from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.model.network import Network
from lib.src.network_lib.model.model import Model
from lib.src.network_lib.utils.methods import Method
from lib.test.helper import count_events_in_json
from lib.src.core.engine import Engine

if __name__ == '__main__':
    filename_stats = "lib/results/complex_test.json"
    processors = [Processor() for _ in range(2 ** 2)]
    network = Network(6, 0.2, processors)
    test_engine = Engine()
    test_array = [
        (AllGatherStepHandler(test_engine.future_event_list, is_start_handler=True), Method.RING, 1600),
        (AllReduceStepHandler(test_engine.future_event_list, is_start_handler=True), Method.HALVING_DOUBLING, 1600)
    ]
    model = Model(test_array)
    test_engine.init(filename_stats, model)
    test_engine.execute(network)
    test_engine.save_statistic()
    # count_events_in_json(filename_stats)
