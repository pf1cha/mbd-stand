class Handler:
    def __init__(self, future_event_list, is_start_handler=False, index=0,
                 next_handler=None):
        self.future_event_list = future_event_list
        self.is_start_handler = is_start_handler
        self.next_handler = next_handler  # указатели на следующий(ие) обработчик(и)
        # Maybe delete next_handler because it is not used anywhere

    def do(self, event):
        pass

    def do_on_start(self, applying_time):
        pass
