from lib.src.network_lib.handler.all_gather_handler import AllGatherStepHandler
from lib.src.network_lib.handler.all_reduce_handler import AllReduceStepHandler
from lib.src.network_lib.handler.reduce_scatter_handler import ReduceScatterStepHandler
from lib.src.network_lib.handler.p2p_handler import P2PStepHandler
from lib.src.network_lib.enums.primitives import Primitives


def get_handler_for_primitive(primitive_type):
    mapping = {
        Primitives.ALL_REDUCE: AllReduceStepHandler,
        Primitives.ALL_GATHER: AllGatherStepHandler,
        Primitives.REDUCE_SCATTER: ReduceScatterStepHandler,
        Primitives.P2P: P2PStepHandler,
    }
    return mapping.get(primitive_type)


def create_sequence(collective_communication, engine, net_config, data_size):
    start_events = []
    total_size = data_size
    for op in collective_communication:
        crt_networks = net_config.get_networks_by_type(op.who)
        size_per_group = 1  # placeholder
        for net in crt_networks:
            handler_class = get_handler_for_primitive(op.type)
            if handler_class:
                start_events.append(
                    (handler_class(engine.future_event_list, is_start_handler=True),
                     op.algorithm,
                     size_per_group,
                     net,
                     )
                )
    return start_events
