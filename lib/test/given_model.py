"""
Description of test:

Model for testing: Nemotron-4 340B
Information: (TP=16, PP=8, DP=4)
Total GPUs: 4*8*16 = 512

Forward Pipeline Pass
    * For each (dp, tp) chain:
    * p2p send/recv between pp stages.

Tensor Parallel Sync (per layer forward)
    * Within (pp, dp) groups:
    * AllReduce (HD) across tp=0..15.

Backward Pipeline Pass
    * For each (dp, tp) chain:
    * p2p send/recv backward between pp stages.

Tensor Parallel Sync (per layer backward)
    * Within (pp, dp) groups:
    * AllReduce (HD) across tp=0..15.

Gradient Synchronization
    * Within (pp, tp) groups:
    * AllReduce (Ring) across dp=0..3.

Execution sequence per micro-batch is:
[ p2p (forward) ] → [ TP AllReduce ] → [ p2p (backward) ] → [ TP AllReduce ] → [ DP AllReduce ]

"""
from lib.src.network_lib.handler.all_gather_handler import AllGatherStepHandler
from lib.src.network_lib.handler.all_reduce_handler import AllReduceStepHandler
from lib.src.network_lib.handler.reduce_scatter_handler import ReduceScatterStepHandler
from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.model.network import Network
from lib.src.network_lib.model.model import Model
from lib.src.network_lib.utils.methods import Method
from lib.test.helper import describe_event_in_text
from lib.src.core.engine import Engine
from lib.test.playground_delete import visualisation_of_primitives


def test_given_model():
    filename_results = "lib/results/given_model_simple_version.json"
    processors = [Processor() for _ in range(2 ** 9)] # 4*8*16 = 2 ** 9 = 512
    network = Network(9, 1 / 900, processors)
    engine = Engine()
    data_size = 512 * (1024 ** 3)  # 680 GB
    sequence_of_actions = [
        # Forward pipeline pass
        (AllReduceStepHandler(engine.future_event_list, is_start_handler=True), Method.HALVING_DOUBLING, data_size),
        # Backward pipeline pass
        (AllReduceStepHandler(engine.future_event_list, is_start_handler=True), Method.HALVING_DOUBLING, data_size),
        # Gradient synchronization
        (AllReduceStepHandler(engine.future_event_list, is_start_handler=True), Method.RING, data_size),
    ]
    visualisation_of_primitives(sequence_of_actions)
    model = Model(sequence_of_actions)
    engine.init(filename_results, model)
    engine.execute(network)
    engine.save_statistic()
    describe_event_in_text(filename_results, network)
