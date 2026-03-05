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
        next_event, method, data_size, net = self.get_next_event_from_model()
        if next_event:
            if method is None:
                next_event.do_on_start(self.clock.get_time(), network=net, data_size=data_size)
            else:
                next_event.do_on_start(self.clock.get_time(), network=net,
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
            event.action()
            self.stats.write_event(event)
            if self.future_event_list.is_empty():
                self.next_step()

    def save_statistic(self):
        self.stats.save_to_file()
