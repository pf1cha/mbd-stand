from lib.src.core.handler import Handler


class DataTransferHandler(Handler):
    def __init__(self, future_event_list):
        super().__init__(future_event_list)

    def do(self, event):
        return
