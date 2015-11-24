class Host:
    def __init__(self):
        self.agent_ip = ""
        self.name = ""
        self.labels = {}
        self.port = 0
        self.dc = ""
        self.uuid = ""

    def print_host(self):
        print("HOST: " + self.agent_ip + " NAME: "+self.name + " uuid: " + self.uuid)
