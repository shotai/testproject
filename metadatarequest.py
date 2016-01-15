import requests
import host
import container
import service


class MetadataRequest:
    @staticmethod
    def get_all_register_containers(config):
        try:
            res = requests.get(url="http://rancher-metadata/latest/containers",
                               headers={"Accept": "application/json"},
                               timeout=3)
        except requests.HTTPError:
            print("HTTPError: get_all_register_containers")
            return []
        except requests.ConnectionError:
            print("ConnectionError: get_all_register_containers")
            return []
        except requests.Timeout:
            print("Timeout: get_all_register_containers")
            return []

        res = res.json()
        try:
            if res["code"] == 404:
                print("Metadata error, cannot get all containers")
                return []
        except KeyError:
            pass
        except TypeError:
            pass

        tmp_containers = []
        for i in res:
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
                for prt in tmp_container.labels["tcpport"].split(","):
                    tmp_container.tcp_ports.append(prt)
            except KeyError:
                pass

            # location
            try:
                for loc in tmp_container.labels["location"].split(","):
                    tmp_container.locations.append(loc)
            except KeyError:
                pass

            # load balancer labels
            default_http_port = None
            for k, v in tmp_container.labels.items():
                if k == "io.rancher.container.agent.role" and v == "LoadBalancerAgent":
                    tmp_container.is_lb = True
                    if config.enable_lb_tcp_port:
                        # process lb's tcp ports
                        tmp_tcp_port, default_http_port = MetadataRequest.process_load_balancer_port(
                            tmp_container.service_name)
                        tmp_container.tcp_ports.extend(tmp_tcp_port)
                elif k.startswith("io.rancher.loadbalancer.target") and config.enable_lb_target:
                    tmp_location = MetadataRequest.process_target_label(v, default_http_port)
                    tmp_container.locations.extend(tmp_location)

            if tmp_container.stack_name and tmp_container.service_name \
                    and (tmp_container.tcp_ports or tmp_container.locations):
                tmp_containers.append(tmp_container)
        return tmp_containers

    @staticmethod
    def get_self_host():
        try:
            res = requests.get(url="http://rancher-metadata/latest/self/host",
                               headers={"Accept": "application/json"},
                               timeout=3)
        except requests.HTTPError:
            print("HTTPError: get_self_host")
            return None
        except requests.ConnectionError:
            print("ConnectionError: get_self_host")
            return None
        except requests.Timeout:
            print("Timeout: get_self_host")
            return None

        res = res.json()
        try:
            if res["code"] == 404:
                print("Metadata error, cannot get host")
                return None
        except KeyError:
            pass
        except TypeError:
            pass

        tmp_host = host.Host()
        tmp_host.agent_ip = res["agent_ip"]
        tmp_host.name = res['name']
        tmp_host.uuid = res["uuid"]
        return tmp_host

    @staticmethod
    def process_target_label(target, default_http_port):
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

    @staticmethod
    def process_load_balancer_port(name):
        try:
            res = requests.get(url="http://rancher-metadata/latest/services/"+name,
                               headers={"Accept": "application/json"},
                               timeout=3)
        except requests.HTTPError:
            print("HTTPError: get_load_balancer")
            return []
        except requests.ConnectionError:
            print("ConnectionError: get_load_balancer")
            return []
        except requests.Timeout:
            print("Timeout: get_load_balancer")
            return []

        res = res.json()
        try:
            if res["code"] == 404:
                print("Metadata error, cannot find load balancer")
                return []
        except KeyError:
            pass
        except TypeError:
            pass

        ret = []
        default_http_port = None
        for p in res["ports"]:
            tmp = p.split("/")
            if len(tmp) == 2 and tmp[1].lower() == "tcp":
                ret.append(tmp[0])
            elif len(tmp) == 1 and not default_http_port:
                default_http_port = tmp[0].split(":")[0]

        return ret, default_http_port

    @staticmethod
    def get_consul_client(name):
        if not name:
            return None
        try:
            res = requests.get(url="http://rancher-metadata/latest/services/"+name,
                               headers={"Accept": "application/json"},
                               timeout=3)
        except requests.HTTPError:
            print("HTTPError: get_consul_client")
            return None
        except requests.ConnectionError:
            print("ConnectionError: get_consul_client")
            return None
        except requests.Timeout:
            print("Timeout: get_consul_client")
            return None

        res = res.json()
        try:
            if res["code"] == 404:
                print("Cannot find " + name + ", Ignored.")
                return None
        except KeyError:
            pass
        except TypeError:
            pass

        consul_client = service.Service()
        consul_client.name = res['name']
        consul_client.stack_name = res['stack_name']
        consul_client.labels = res['labels']
        try:
            for loc in consul_client.labels["location"].split(","):
                consul_client.locations.append(loc)
        except KeyError:
            pass

        if consul_client.stack_name and consul_client.name:
            if consul_client.locations:
                return consul_client
            else:
                print("no location label, ignored")
                return None
        else:
            print("cannot find valid consul client")
            return None










































