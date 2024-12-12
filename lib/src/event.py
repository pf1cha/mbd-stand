from uuid import uuid4


class Event:
    def __init__(self, applying_time, handler):
        self.uuid = uuid4()
        self.applying_time = applying_time
        self.handler = handler

    def __lt__(self, other):
        return self.applying_time < other.applying_time

    def action(self):
        self.handler.do(self)

    def to_json(self):
        pass
