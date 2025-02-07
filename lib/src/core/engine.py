from uuid import uuid4
from lib.src.core.stats import Statistic
from lib.src.core.fel import FutureEventList
from lib.src.core.clock import Clock


class Engine:
    def __init__(self, end_time=None, filename_stats=None):
        self.uuid = uuid4()
        self.clock = Clock()
        self.future_event_list = FutureEventList()
        self.end_time = end_time
        self.stats = Statistic(filename_stats, self.uuid)


    def execute(self):
        while not self.future_event_list.is_empty():
            event = self.future_event_list.pop_event()
            self.clock.set_time(event.applying_time)
            if self.end_time and self.clock.get_time() > self.end_time:
                break
            event.action()
            self.stats.write_event(event)

    def save_statistic(self):
        self.stats.save_to_file()

    def create_start_event(self, event):
        self.future_event_list.add_event(event)
