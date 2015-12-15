import requests
import host
import container
import os
import service


class MetadataRequest:
    @staticmethod
    def get_all_register_containers():
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

            # normal location
            try:
                for loc in tmp_container.labels["location"].split(","):
                    tmp_container.locations.append(loc)
            except KeyError:
                pass

            # load balancer location
            try:
                for loc in tmp_container.labels["lblocation"].split(","):
                    tmp_container.lb_locations.append(loc)
            except KeyError:
                pass

            # target label
            enable_target = os.environ.get("ENABLETARGET", "False")
            if enable_target == "True":
                for k, v in tmp_container.labels.items():
                    if k.startswith("io.rancher.loadbalancer.target"):
                        tmp_location, tmp_tcp_port = MetadataRequest.process_target_label(
                            v, tmp_container.ports[0].split(":")[0])
                        tmp_container.lb_locations.extend(tmp_location)
                        tmp_container.tcp_ports.extend(tmp_tcp_port)

            if tmp_container.stack_name and tmp_container.service_name \
                    and (tmp_container.tcp_ports or tmp_container.locations or tmp_container.lb_locations):
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
        tmp_host.print_host()
        return tmp_host

    @staticmethod
    def process_target_label(target, port):
        location = []
        tcp_port = []
        for t in target.split(","):
            routing_path = t.split("=")[0]
            if ":" in routing_path and "/" in routing_path:
                tmp_loc = routing_path.split(":")[1]
                tmp_port = tmp_loc.split("/")[0]
                tmp_location = tmp_loc.lstrip(tmp_port)
                location.append(tmp_port+":"+tmp_port+":"+tmp_location)
            elif "/" in routing_path:
                tmp_port = routing_path.split("/")[0]
                if tmp_port.isdigit():
                    tmp_location = routing_path.lstrip(tmp_port)
                else:
                    tmp_port = port
                    tmp_location = routing_path
                location.append(tmp_port+":"+tmp_port+":"+tmp_location)
            elif ":" in routing_path:  # the rule without path will be treated as tcp port
                tmp_port = routing_path.split(":")[1]
                tcp_port.append(tmp_port+":"+tmp_port)
            else:
                tcp_port.append(routing_path+":"+routing_path)
        return location, tcp_port

    @staticmethod
    def get_consul_client(name):
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
                print("Metadata error, cannot find consul client")
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
































