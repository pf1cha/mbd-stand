from json import dump

class Statistic:
    def __init__(self, filename, engine_id):
        self.filename = filename
        self.engine_id = engine_id
        self.events = []

    def write_event(self, event):
        event_data = event.to_json()
        self.events.append(event_data)

    def save_to_file(self):
        data = {
            "engine_id": str(self.engine_id),
            "events": self.events
        }
        with open(self.filename, "w") as file:
            dump(data, file, indent=4)
