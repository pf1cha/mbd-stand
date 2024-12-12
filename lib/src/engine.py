from uuid import uuid4
from lib.src.stats import Statistic
from lib.src.fel import FutureEventList
from lib.src.clock import Clock
from lib.src.handler import Handler

class Engine:
    def __init__(self, end_time=None):
        self.uuid = uuid4()
        self.clock = Clock()
        self.future_event_list = FutureEventList()
        Handler(self.future_event_list, self.clock)
        self.end_time = end_time


    def start(self, filename_stats):
        stat = Statistic(filename_stats, self.uuid)
        while not self.future_event_list.is_empty():
            event = self.future_event_list.pop_event()
            self.clock.set(event.applying_time)
            if self.end_time and self.clock.get_time() > self.end_time:
                break
            event.action()
            stat.write_event(event)
        stat.save_to_file()


    def create_start_event(self, event):
        self.future_event_list.add_event(event)
