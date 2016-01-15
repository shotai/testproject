class Host:
    def __init__(self):
        self.agent_ip = ""
        self.name = ""
        self.labels = {}
        self.dc = ""
        self.uuid = ""

    def print_host(self):
        print("HOST: " + self.agent_ip + "\n" +
              "NAME: "+self.name + "\n" +
              "uuid: " + self.uuid)
