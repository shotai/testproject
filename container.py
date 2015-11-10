class Container:
    def __init__(self):
        self.create_index = 0
        self.hostname = ""
        self.pots = []
        self.name = ""
        self.service_name = ""
        self.stack_name = ""
        self.labels = {}
        self.tcp_ports = []
        self.locations = []
        self.primary_ip = ""

    def print_container(self):
        print("CONTAINER: "+ self.name+" host: " + self.hostname+ " stack_name: "+self.stack_name +
              " primary_ip: " + self.primary_ip)

