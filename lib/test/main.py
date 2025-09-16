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

if __name__ == '__main__':
    test_given_model()
    # count_events_in_json(filename_stats)
    # I can ask GPT for generate sequence of primitives for any model with specific configuration
    # TODO create super test with GPT
