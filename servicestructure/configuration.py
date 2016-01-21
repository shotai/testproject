class Configuration:
    def __init__(self):
        self.enable_acl = False
        self.enable_tcp = False
        self.enable_lb_target = False
        self.enable_lb_tcp_port = False
        self.wait_time = 10
        self.consul_server = ""
        self.consul_client = ""

    def print_config(self):
        print('Enable acl:                                               ' + str(self.enable_acl) + '\n' +
              'Enable tcp register with nginx-defined tag (tcpport):     ' + str(self.enable_tcp) + '\n' +
              'Enable register with load balancer target label:          ' + str(self.enable_lb_target) + '\n' +
              'Enable register with loadbalancer ports which have /tcp): ' + str(self.enable_lb_tcp_port) + '\n' +
              'Registrator loop sleep time:                              ' + str(self.wait_time) + '\n' +
              'Consul server address:                                    ' + self.consul_server + '\n' +
              'Consul client address:                                    ' + self.consul_client + '\n')
