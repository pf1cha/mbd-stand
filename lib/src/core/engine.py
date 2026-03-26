from uuid import uuid4
from lib.src.core.stats import Statistic
from lib.src.core.fel import FutureEventList
from lib.src.core.clock import Clock


class Engine:
    def __init__(self, end_time=None):
        self.uuid = uuid4()
        self.clock = Clock()
        self.future_event_list = FutureEventList()
        self.end_time = end_time
        self.stats = None
        self.model = None

    def init(self, filename_stats, model):
        self.stats = Statistic(filename_stats, self.uuid)
        self.model = model

    def get_next_event_from_model(self):
        if self.future_event_list.is_empty():
            return self.model.get_next_handler()
        return None, None, None, None

    def next_step(self):
        events = self.get_next_event_from_model()
        if events is not None:
            for event in events:
                next_event = event[0]
                method = event[1]
                data_size = event[2]
                processors = event[3]
                topology = event[4]

                if method is None:
                    next_event.do_on_start(self.clock.get_time(), processors=processors, topology=topology,
                                           data_size=data_size)
                else:
                    next_event.do_on_start(self.clock.get_time(), processors=processors, topology=topology,
                                           method=method, data_size=data_size)

    def execute(self):
        if len(self.model.handlers) < 1:
            raise Exception('No handlers defined in the model simulation!')

        self.next_step()
        while not self.future_event_list.is_empty():
            event = self.future_event_list.pop_event()
            self.clock.set_time(event.applying_time)
            if self.end_time and self.clock.get_time() > self.end_time:
                break
            end_time_of_event = event.action()
            self.stats.write_event(event)
            if self.future_event_list.is_empty():
                self.clock.set_time(end_time_of_event)
                self.next_step()

    def save_statistic(self):
        self.stats.save_to_file(total_time=self.clock.get_time())
