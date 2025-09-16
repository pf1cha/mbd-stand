import heapq


class FutureEventList:
    def __init__(self):
        self.events = []

    def add_event(self, event):
        heapq.heappush(self.events, event)

    def pop_event(self):
        return heapq.heappop(self.events) if self.events else None

    def is_empty(self):
        return len(self.events) == 0
