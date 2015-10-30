class Host:
    def __init__(self):
        self.agent_ip = ""
        self.name = ""
        self.labels = {}
        self.port = 0
        self.dc = ""

    def print_host(self):
        print("HOST: " + self.agent_ip+":"+str(self.port)+" NAME: "+self.name)
