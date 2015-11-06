class Service:
    def __init__(self):
        self.containers = []
        self.hostname = ""
        self.kind = ""
        self.labels = {}
        self.name = ""
        self.ports = []
        self.stack_name = ""
        self.links = []
        self.tags = []
        self.location = []
        self.tcp_ports = []
        self.public_ports = []

    def print_service(self):
        print("SERVICE: " + self.stack_name+"/" + self.name + " TAGS:" + " ".join(self.tags))


