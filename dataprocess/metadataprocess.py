import os
from servicestructure import container, service, host
from registerrequest import metadatarequest


class MetaDataProcess:
    def __init__(self):
        self._res = {}

    def get_all_containers(self):
        self._res = metadatarequest.MetadataRequest.get_all_containers_metadata()
        if not self._res:
            return []
        return self.__process_container_data__()

    def get_consul_client(self, name):
        self._res = metadatarequest.MetadataRequest.get_service_metadata(name)
        if not self._res:
            return None
        return self.__process_service_data__()

    def get_host(self):
        self._res = metadatarequest.MetadataRequest.get_self_host_metadata()
        if not self._res:
            return None
        return self.__process_host_data__()

    def __process_host_data__(self):
        tmp_host = host.Host()
        tmp_host.agent_ip = self._res["agent_ip"]
        tmp_host.name = self._res['name']
        tmp_host.uuid = self._res["uuid"]
        tmp_host.print_host()
        return tmp_host

    def __process_service_data__(self):
        tmp_service = service.Service()
        tmp_service.name = self._res['name']
        tmp_service.stack_name = self._res['stack_name']
        tmp_service.labels = self._res['labels']
        try:
            for loc in tmp_service.labels["eze.routing.registrator.http"].split(","):
                tmp_service.locations.append(loc)
        except KeyError:
            pass

        if tmp_service.stack_name and tmp_service.name:
            if tmp_service.locations:
                return tmp_service
            else:
                print("no eze.routing.registrator.http label, ignored")
                return None
        else:
            print("cannot find service")
            return None

    def __process_container_data__(self):
        tmp_containers = []
        for i in self._res:
            tmp_container = container.Container()
            tmp_container.create_index = i['create_index']
            tmp_container.hostname = i['hostname']
            tmp_container.stack_name = i['stack_name']
            tmp_container.name = i['name']
            tmp_container.service_name = i['service_name']
            tmp_container.ports = i['ports']
            tmp_container.labels = i['labels']
            tmp_container.ips = i['ips']
            tmp_container.host_uuid = i['host_uuid']

            # tcp port
            try:
                for prt in tmp_container.labels["eze.routing.registrator.tcp"].split(","):
                    tmp_container.tcp_ports.append(prt)
            except KeyError:
                pass

            # location
            try:
                for loc in tmp_container.labels["eze.routing.registrator.http"].split(","):
                    tmp_container.locations.append(loc)
            except KeyError:
                pass

            # load balancer labels
            default_http_port = None
            enable_target = os.environ.get("LOADBALANCER", "False")
            try:
                if tmp_container.labels["io.rancher.container.agent.role"] == "LoadBalancerAgent":
                    tmp_container.is_lb = True
                    if enable_target == "True":
                        tmp_tcp_port, default_http_port = self.__process_load_balancer_ports__(
                            tmp_container.service_name)
                        tmp_container.tcp_ports.extend(tmp_tcp_port)
            except KeyError:
                pass

            if tmp_container.is_lb:
                for k, v in tmp_container.labels.items():
                    if k.startswith("io.rancher.loadbalancer.target") and enable_target == "True":
                        tmp_location = self.__process_target_label__(v, default_http_port)
                        tmp_container.locations.extend(tmp_location)

            if tmp_container.stack_name and tmp_container.service_name \
                    and (tmp_container.tcp_ports or tmp_container.locations):
                tmp_containers.append(tmp_container)
        return tmp_containers

    def __process_load_balancer_ports__(self, service_name):
        """

        :param service_name: str
        :return: List[str], str
        """
        ret = []
        res = metadatarequest.MetadataRequest.get_service_metadata(service_name)
        if not res:
            return ret
        default_http_port = None
        for p in res["ports"]:
            tmp = p.split("/")
            if len(tmp) == 2 and tmp[1].lower() == "tcp":
                ret.append(tmp[0])
            elif len(tmp) == 1 and not default_http_port:
                default_http_port = tmp[0].split(":")[0]
        return ret, default_http_port

    def __process_target_label__(self, target, default_http_port):
        location = []
        for t in target.split(","):
            routing_path = t.split("=")[0]
            if ":" in routing_path and "/" in routing_path:  # -- test.com:3000/v1=3001 -> 3000:3000:/v1
                tmp_loc = routing_path.split(":")[1]
                tmp_port = tmp_loc.split("/")[0]
                tmp_location = tmp_loc.lstrip(tmp_port)
                location.append(tmp_port+":"+tmp_port+":"+tmp_location)
            elif "/" in routing_path:  # -- 3000/v1=3001 -> 3000:3000:/v1
                tmp_port = routing_path.split("/")[0]
                if tmp_port.isdigit():
                    tmp_location = routing_path.lstrip(tmp_port)
                else:
                    if not default_http_port:
                        continue
                    tmp_port = default_http_port
                    tmp_location = routing_path
                location.append(tmp_port+":"+tmp_port+":"+tmp_location)
            elif ":" in routing_path:  # -- test.com:3000=3001 -> 3000:3000:/
                tmp_port = routing_path.split(":")[1]
                location.append(tmp_port+":"+tmp_port+":/")
            else:  # -- 3000=3001 -> 3000:3000:/
                location.append(routing_path+":"+routing_path + ":/")
        return location
