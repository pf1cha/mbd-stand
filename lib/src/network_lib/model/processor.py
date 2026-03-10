import uuid


class Processor:
    # TODO : get rid of id and use only uuid for identification. It was needed for debugging purposes.
    def __init__(self, id_num):
        self.uuid = uuid.uuid4()
        self.id = id_num
