from event import Event
from fel import FutureEventList
from clock import Clock
from handler import Handler
from engine import Engine
import random




class StudyEvent(Event):
    def __init__(self, applying_time, handler):
        super().__init__(applying_time, handler)
        self.study_time = random.uniform(1, 7.0)


class SleepEvent(Event):
    def __init__(self, applying_time, handler):
        super().__init__(applying_time, handler)
        self.sleep_time = random.uniform(6.0, 9.0)


class RelaxEvent(Event):
    def __init__(self, applying_time, handler):
        super().__init__(applying_time, handler)
        self.relax_time = random.uniform(0, 1.0)


class StudyHandler(Handler):
    def do(self, event):
        if event.study_time > 3:
            print(f"Study event at {event.applying_time}")
            handler = RelaxHandler(self.future_event_list, self.clock)
            self.future_event_list.add_event(RelaxEvent(self.clock.get_time() + event.study_time, handler))
        else:
            print(f"Study event at {event.applying_time}")
            handler = SleepHandler(self.future_event_list, self.clock)
            self.future_event_list.add_event(SleepEvent(self.clock.get_time() + event.study_time, handler))

class SleepHandler(Handler):
    def do(self, event):
        print(f"Sleep event at {event.applying_time}")
        handler = StudyHandler(self.future_event_list, self.clock)
        self.future_event_list.add_event(StudyEvent(self.clock.get_time() + event.sleep_time, handler))

class RelaxHandler(Handler):
    def do(self, event):
        print(f"Relax event at {event.applying_time}")
        handler = StudyHandler(self.future_event_list, self.clock)
        # self.future_event_list.add_event(StudyEvent(self.clock.get_time() + 1, StudyHandler(self.future_event_list, self.clock)))
        self.future_event_list.add_event(StudyEvent(self.clock.get_time() + event.relax_time, handler))

if __name__ == '__main__':
    # code will be here
    clock = Clock()
    eventList = FutureEventList()
    Handler(eventList, clock)
    engine = Engine(eventList, clock, 100)
    engine.create_start_event(StudyEvent(0, StudyHandler(eventList, clock)))
    engine.start()
