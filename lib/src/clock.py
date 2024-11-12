class Clock:
    def __init__(self, current_time=0.0):
        self.current_time = current_time

    def advance(self, time):
        self.current_time += time

    def get_time(self):
        return self.current_time
