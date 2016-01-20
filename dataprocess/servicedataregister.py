from registerrequest import consulrequest
from servicestructure import container


class ServiceDataRegister:
    def __init__(self, consul_url, host_ip, consul_token):
        self._consul_url = consul_url
        self._consul_token = consul_token
        self._host_ip = host_ip

    def register_containers(self, curr_container, registered_containers):
        payloads = self.__generate_tcp_payload__(curr_container)
        payloads.extend(self.__generate_http_payload__(curr_container))
        return consulrequest.ConsulRequest.agent_register_container(payloads, registered_containers,
                                                                    self._consul_url, self._consul_token)

    def register_consul_client(self, service, host):
        tmp_container = container.Container()
        tmp_container.locations = service.locations
        tmp_container.service_name = service.stack_name
        tmp_container.service_name = service.name
        tmp_container.name = host.name
        tmp_container.is_lb = False
        payloads = self.__generate_http_payload__(tmp_container)
        return consulrequest.ConsulRequest.agent_register_container(payloads=payloads,
                                                                    consul_url=self._consul_url,
                                                                    consul_token=self._consul_token,
                                                                    registered_containers=[])

    def __generate_tcp_payload__(self, curr_container):
        payloads = []
        for i in curr_container.tcp_ports:
            p = i.split(":")
            if len(p) < 2:
                print("Bad eze.routing.registrator.tcp format: " + i + ", ignored.")
                continue
            tmp = {
                "ID": (curr_container.name + "-" + i).replace(":", "-"),
                "Name": curr_container.stack_name + '-' + curr_container.service_name,
                "Tags": ["tcpport:"+p[0]],
                "Address": self._host_ip,
                "Port": int(p[0]),
                "Check": {}
            }
            try:
                for sp in p[2:]:
                    tmp["Tags"].append(sp)
            except IndexError:
                pass
            payloads.append(tmp)
        return payloads

    def __generate_http_payload__(self, curr_container):
        payloads = []
        for i in curr_container.locations:
            tmp = {
                "Name": curr_container.stack_name + '-' + curr_container.service_name,
                "Address": self._host_ip,
                "Tags": [],
                "Check": {}
            }
            loc = i.replace("loc:", "")
            provide_location = loc.split(":")
            if len(provide_location) < 3:
                print("Bad eze.routing.registrator.http format: " + i)
                continue
            public_port = provide_location[0]
            private_port = provide_location[1]
            loc = provide_location[2]
            try:
                path = provide_location[3]
                if path:
                    tmp["Tags"].append("path:"+path)
                enable_health_check = provide_location[4]
                if enable_health_check.lower() == "true":
                    health_check_addr = provide_location[5] if len(provide_location) > 5 \
                                                               and provide_location[5] else loc
                    tmp["Check"] = self.__generate_http_health_check__(is_lb=curr_container.is_lb,
                                                                       curr_ip=curr_container.ips[0],
                                                                       public_port=public_port,
                                                                       private_port=private_port,
                                                                       health_check_addr=health_check_addr)
                for sp in provide_location[6:]:
                    tmp["Tags"].append(sp)
            except IndexError:
                pass

            tmp["Port"] = int(public_port)
            tmp["ID"] = (curr_container.name + '-' + public_port + '-' + loc).replace("/", "-")
            tmp["Tags"].append("loc:"+loc)
            payloads.append(tmp)
        return payloads

    def __generate_http_health_check__(self, is_lb, curr_ip, public_port, private_port, health_check_addr):
        if is_lb:
            health = {
                "HTTP": "http://" + curr_ip + ":" + public_port + health_check_addr,
                "Interval": "10s"
            }
        else:
            health = {
                "HTTP": "http://" + curr_ip + ":" + private_port + health_check_addr,
                "Interval": "10s"
            }
        return health







