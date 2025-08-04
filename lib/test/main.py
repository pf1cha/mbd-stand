from lib.src.network_lib.handler.all_gather_handler import AllGatherStepHandler
from lib.src.network_lib.handler.all_reduce_handler import AllReduceStepHandler
from lib.src.network_lib.handler.reduce_scatter_handler import ReduceScatterStepHandler
from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.model.network import Network
from lib.src.network_lib.model.model import Model
from lib.src.network_lib.utils.methods import Method
from lib.test.helper import count_events_in_json, describe_event_in_text
from lib.src.core.engine import Engine

if __name__ == '__main__':
    filename_stats = "lib/results/all_reduce_halving_doubling_results.json"
    processors = [Processor() for _ in range(2 ** 3)]
    network = Network(6, 0.0, processors)
    test_engine = Engine()
    test_array = [
        # (ReduceScatterStepHandler(test_engine.future_event_list, is_start_handler=True), Method.HALVING_DOUBLING, 6400),
        # (AllGatherStepHandler(test_engine.future_event_list, is_start_handler=True), Method.HALVING_DOUBLING, 6400),
        (AllReduceStepHandler(test_engine.future_event_list, is_start_handler=True), Method.HALVING_DOUBLING, 6400),
    ]
    model = Model(test_array)
    test_engine.init(filename_stats, model)
    test_engine.execute(network)
    test_engine.save_statistic()
    describe_event_in_text(filename_stats, network)
    # count_events_in_json(filename_stats)
