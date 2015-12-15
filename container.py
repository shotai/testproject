class Container:
    def __init__(self):
        self.create_index = 0
        self.hostname = ""
        self.ports = []
        self.name = ""
        self.service_name = ""
        self.stack_name = ""
        self.labels = {}
        self.ips = []
        self.host_uuid = ""
        self.tcp_ports = []
        self.locations = []
        self.lb_locations = []

    def print_container(self):
        print("CONTAINER: " + self.name + " host: " + self.hostname + " stack_name: " + self.stack_name +
              " create_index: " + str(self.create_index))

