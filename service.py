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
        print(" ".join(self.tags) + " " + self.name+" "+ self.stack_name)

    # def add_container(self, name):
    #     self.containers.append(name)
    #
    # def add_port(self, port):
    #     self.ports.append(port)
    #
    # def add_label(self, key, value):
    #     if key in self.labels:
    #         self.labels[key].append(value)
    #     else:
    #         self.labels[key] = [value]
    #
    # def add_metadata(self, key, value):
    #     if key in self.metadata:
    #         self.metadata[key].append(value)
    #     else:
    #         self.metadata[key] = [value]
    #
    # def add_link(self, name):
    #     self.links.append(name)


