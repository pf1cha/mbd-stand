from lib.src.network_lib.handler.all_gather_handler import AllGatherStepHandler
from lib.src.network_lib.handler.all_reduce_handler import AllReduceStepHandler
from lib.src.network_lib.handler.reduce_scatter_handler import ReduceScatterStepHandler
from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.model.network import Network
from lib.src.network_lib.model.model import Model
from lib.src.network_lib.utils.methods import Method
from lib.test.helper import count_events_in_json, describe_event_in_text
from lib.src.core.engine import Engine
from lib.test.given_model import test_given_model

def old_test():
    # TODO maybe delete, because it is unnecessary test and doesn't provide any meaningful results.
    filename_stats = "lib/results/test.json"
    processors = [Processor() for _ in range(2 ** 2)]
    network = Network(6, 0.0, processors)
    test_engine = Engine()
    test_array = [
        # базовое задаем кол-во данных
        (ReduceScatterStepHandler(test_engine.future_event_list, is_start_handler=True), Method.RING, 6400),
        (AllGatherStepHandler(test_engine.future_event_list, is_start_handler=True), Method.HALVING_DOUBLING, 6400),
        (AllReduceStepHandler(test_engine.future_event_list, is_start_handler=True), Method.RING, 6400),
    ]
    model = Model(test_array)
    test_engine.init(filename_stats, model)
    test_engine.execute(network)
    test_engine.save_statistic()
    describe_event_in_text(filename_stats, network)

if __name__ == '__main__':
    test_given_model()
    # count_events_in_json(filename_stats)
    # I can ask GPT for generate sequence of primitives for any model with specific configuration
    # TODO create super test with GPT