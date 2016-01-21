class Host:
    def __init__(self):
        self.agent_ip = ""
        self.name = ""
        self.labels = {}
        self.dc = ""
        self.uuid = ""

    def print_host(self):
<<<<<<< HEAD:host.py
        print("HOST: " + self.agent_ip + "\n" +
              "NAME: "+self.name + "\n" +
              "uuid: " + self.uuid)
=======
        print("HOST: " + self.agent_ip + "\n"
              "NAME: " + self.name + "\n"
              "IP:   " + self.agent_ip + "\n"
              "UUID: " + self.uuid + "\n")
>>>>>>> origin/dev:servicestructure/host.py
