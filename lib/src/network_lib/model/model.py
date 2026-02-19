

class Model:
    def __init__(self, events):
        self.handlers = events
        self.index = 0
        self.length = len(self.handlers)

    def get_next_handler(self):
        if self.index < self.length:
            handler, method, data_size = self.handlers[self.index]
            self.index += 1
            return handler, method, data_size
        return None, None, None
