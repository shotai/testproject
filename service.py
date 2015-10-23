class Service:
    def __init__(self):
        self.containers = []
        self.hostname = ""
        self.kind = ""
        self.labels = {}
        self.metadata = {}
        self.name = ""
        self.ports = []
        self.stack_name = ""
        self.links = []
        self.tags = []
        self.address = ""

    def print_service(self):
        print("SERVICE: " + self.stack_name+"/" + self.name + " TAGS:" + " ".join(self.tags))


