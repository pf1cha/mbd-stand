"""
Model for testing: Nemotron-4 340B
Information: (TP=8, PP=4, DP=16)
Total GPUs: 8*4*16 = 512

Forward pass:
    * p2p send/recv between pipeline stages
    * AllReduce (HD) inside each TP = 8 group
Backward pass
    * p2p send/recv between pipeline stages
    * AllReduce (HD) again for TP = 8 group
Gradient sync
    * AllReduce (HD) across DP-16 replicas

[ p2p (forward) ] → [ TP AllReduce (HD) ] → [ p2p (backward) ] →
→ [ TP AllReduce (HD) ] → [ DP AllReduce (Ring) ]

Training was done by 768 DGX H100 nodes.
Each node contains 8 H100 80GB SXM5 GPUs based on the NVIDIA Hopper architecture.
Bandwidth is 900 GB/s (450 GB/s in each direction).

Total size of training dataset is approximately 680GB based on calculation.
The information about that wasn't found in the Internet.
"""

from lib.src.network_lib.handler.all_gather_handler import AllGatherStepHandler
from lib.src.network_lib.handler.all_reduce_handler import AllReduceStepHandler
from lib.src.network_lib.handler.reduce_scatter_handler import ReduceScatterStepHandler
from lib.src.network_lib.model.processor import Processor
from lib.src.network_lib.model.network import Network
from lib.src.network_lib.model.model import Model
from lib.src.network_lib.utils.methods import Method
from lib.test.helper import count_events_in_json, describe_event_in_text
from lib.src.core.engine import Engine


# def test_nemotron_4_340b():
#     filename_results = "lib/results/test_nemotron_4_340b.json"
#     processors = [Processor() for _ in range(2 ** 9)]
#     network = Network(9, 1 / 900, processors)
#     engine = Engine()
#     data_size = 680 * (1024 ** 3)  # 680 GB
#     sequence_per_microbatch = [
#         # Forward pipeline pass
#         (AllReduceStepHandler(engine.future_event_list, is_start_handler=True), Method.HALVING_DOUBLING, 6400),
#         # Backward pipeline pass
#         (AllReduceStepHandler(engine.future_event_list, is_start_handler=True), Method.HALVING_DOUBLING, 6400),
#         # Gradient synchronization
#         (AllReduceStepHandler(engine.future_event_list, is_start_handler=True), Method.RING, 6400),
#     ]
#     model = Model(sequence_per_microbatch)
#     engine.init(filename_results, model)
#     engine.execute(network)
#     engine.save_statistic()
#     describe_event_in_text(filename_results, network)
