class Engine:
    def __init__(self, clock, future_event_list, end_time=None):
        self.clock = clock
        self.future_event_list = future_event_list
        self.end_time = end_time

    def start(self):
        while not self.future_event_list.is_empty():
            event = self.future_event_list.pop_event()
            self.clock.advance(event.applying_time - self.clock.get_time())
            if self.end_time and self.clock.get_time() > self.end_time:
                break
            event.do()
