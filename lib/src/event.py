class Event:
    def __init__(self, creation_time, applying_time, handler):
        self.creation_time = creation_time
        self.applying_time = applying_time
        self.handler = handler

    def __lt__(self, other):
        return self.applying_time < other.applying_time

    def do(self):
        self.handler.do(self)
