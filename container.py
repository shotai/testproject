class Container:
    def __init__(self):
        self.create_index = 0
        self.hostname = ""
        self.ports = []
        self.name = ""
        self.service_name = ""
        self.stack_name = ""
        self.labels = {}
        self.primary_ip = ""
        self.host_uuid = ""
        self.uuid = ""
        self.tcp_ports = []
        self.locations = []
        self.lb_locations = []

    def print_container(self):
        print("CONTAINER: " + self.name+" host: " + self.hostname + " stack_name: "+self.stack_name +
              " primary_ip: " + self.primary_ip + " uuid: " + self.uuid)

