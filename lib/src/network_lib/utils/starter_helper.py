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


def get_batch_sizes(batch_size, topology):
    global_batch = batch_size  # size for pipelines
    minibatch = batch_size / topology.dp  # size for dp
    microbatch = batch_size / (topology.dp * topology.tp)  # size for tp and dp
    return [global_batch, minibatch, microbatch]


def get_batch_for_parallelism(parallelism, data):
    if parallelism == "pp":
        return data[0]
    elif parallelism == "dp":
        return data[1]
    return data[2]


def create_sequence(collective_communication, engine, net_config, data):
    start_events = []
    for op in collective_communication:
        crt_networks = net_config.get_networks_by_type(op.who)
        size_per_group = get_batch_for_parallelism(op.who, data)
        full_event = []
        for net in crt_networks:
            handler_class = get_handler_for_primitive(op.type)
            if handler_class:
                full_event.append(
                    (handler_class(engine.future_event_list, is_start_handler=True),
                     op.algorithm,
                     size_per_group,
                     net,
                     )
                )
        start_events.append(full_event)
    return start_events
