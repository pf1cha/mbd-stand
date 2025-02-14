from lib.src.core.engine import Engine
from lib.src.network_lib.utils.primitives import Primitives
from lib.src.network_lib.event.all_gather_event import AllGatherStepEvent
from lib.src.network_lib.handler.all_gather_handler import AllGatherStepHandler
from lib.src.network_lib.event.all_reduce_event import AllReduceStepEvent
from lib.src.network_lib.handler.all_reduce_handler import AllReduceStepHandler
from lib.src.network_lib.event.reduce_scatter_event import ReduceScatterStepEvent
from lib.src.network_lib.handler.reduce_scatter_handler import ReduceScatterStepHandler


def create_events(primitive, method, network, data_size, applying_time, engine):
    if primitive == Primitives.ALL_GATHER:
        all_gather_handler = AllGatherStepHandler(engine.future_event_list)
        return AllGatherStepEvent(applying_time, all_gather_handler, network, data_size, method)
    elif primitive == Primitives.ALL_REDUCE:
        all_reduce_handler = AllReduceStepHandler(engine.future_event_list)
        return AllReduceStepEvent(applying_time, all_reduce_handler, network, data_size, method)
    elif primitive == Primitives.REDUCE_SCATTER:
        reduce_scatter_handler = ReduceScatterStepHandler(engine.future_event_list)
        return ReduceScatterStepEvent(applying_time, reduce_scatter_handler, network, data_size, method)
    elif primitive == Primitives.BROADCAST:
        pass


# Example of array of events:
# events = [(Primitives.ALL_GATHER, Method.RING),
# (Primitives.ALL_REDUCE, Method.HALVING_DOUBLING),
# (Primitives.REDUCE_SCATTER, Method.RING)]

class Model:
    def __init__(self, network, events, data_size):
        self.events = events
        self.network = network
        self.data_size = data_size

    def process(self, filename_stats):
        engine = Engine()
        engine.init(filename_stats)
        applying_time = 0
        for primitive, method in self.events:
            event = create_events(primitive, method, self.network, self.data_size, applying_time, engine)
            engine.execute(event)
            applying_time = engine.clock.get_time()
        engine.save_statistic()
