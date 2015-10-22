class Host:
    def __init__(self):
        self.agent_ip = ""
        self.name = ""
        self.labels = {}
        self.port = 0
        self.dc = ""

    def print_host(self):
        print(self.agent_ip+" "+self.port+" "+self.name)

    # def add_labels(self, key, value):
    #     if key in self.labels:
    #         self.labels[key].append(value)
    #     else:
    #         self.labels[key] = [value]

