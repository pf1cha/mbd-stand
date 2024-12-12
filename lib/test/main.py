from lib.src.event import Event
from lib.src.handler import Handler
from lib.src.engine import Engine
import random



class StudyEvent(Event):
    def __init__(self, applying_time, handler):
        super().__init__(applying_time, handler)
        self.study_time = random.uniform(1, 12.0)

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "applying_time": self.applying_time,
            "study_time": self.study_time,
            "handler_type": type(self.handler).__name__,
        }


class SleepEvent(Event):
    def __init__(self, applying_time, handler):
        super().__init__(applying_time, handler)
        self.sleep_time = random.uniform(6.0, 9.0)
    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "applying_time": self.applying_time,
            "sleep_time": self.sleep_time,
            "handler_type": type(self.handler).__name__,
        }


class RelaxEvent(Event):
    def __init__(self, applying_time, handler):
        super().__init__(applying_time, handler)
        self.relax_time = random.uniform(0, 1.0)
    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "applying_time": self.applying_time,
            "relax_time": self.relax_time,
            "handler_type": type(self.handler).__name__,
        }


class DeadEvent(Event):
    def __init__(self, applying_time, handler):
        super().__init__(applying_time, handler)

    def to_json(self):
        return {
            "uuid": str(self.uuid),
            "event_type": type(self).__name__,
            "applying_time": self.applying_time,
            "handler_type": type(self.handler).__name__,
        }


class StudyHandler(Handler):
    def do(self, event):
        print(f"Study event at {event.applying_time}")
        if event.study_time < 3:
            handler = RelaxHandler(self.future_event_list, self.clock)
            self.future_event_list.add_event(RelaxEvent(self.clock.get_time() + event.study_time, handler))
        elif event.study_time < 10:
            handler = SleepHandler(self.future_event_list, self.clock)
            self.future_event_list.add_event(SleepEvent(self.clock.get_time() + event.study_time, handler))
        else:
            handler = DeadHandler(self.future_event_list, self.clock)
            self.future_event_list.add_event(DeadEvent(self.clock.get_time() + event.study_time, handler))


class SleepHandler(Handler):
    def do(self, event):
        print(f"Sleep event at {event.applying_time}")
        handler = StudyHandler(self.future_event_list, self.clock)
        self.future_event_list.add_event(StudyEvent(self.clock.get_time() + event.sleep_time, handler))


class RelaxHandler(Handler):
    def do(self, event):
        print(f"Relax event at {event.applying_time}")
        handler = StudyHandler(self.future_event_list, self.clock)
        self.future_event_list.add_event(StudyEvent(self.clock.get_time() + event.relax_time, handler))


class DeadHandler(Handler):
    def do(self, event):
        print(f"Dead at {event.applying_time}")


if __name__ == '__main__':
    engine = Engine(100)
    engine.create_start_event(StudyEvent(0, StudyHandler(engine.future_event_list, engine.clock)))
    engine.start("stats.json")
