class Service:
    def __init__(self):
        self.containers = []
        self.external_ips = []
        self.hostname = ""
        self.kind = ""
        self.labels = []
        self.metadata = {}
        self.name = ""
        self.ports = []
        self.stack_name=""

    def add_container(self, name):
        self.containers.append(name)


    def add_port(self, port):
        self.ports.append(port)
