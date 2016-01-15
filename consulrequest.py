import requests


class ConsulRequest:
    @staticmethod
    def agent_register_container(container, host, consul_url, registered_container, config, consul_token=None):
        """
        :param container: Container
        :param host: Host
        :param consul_url: str
        :param registered_container: List[str]
        :param config: Configuration
        :param consul_token: str
        :return: List[str]
        """
        container_ids = []
        payloads = ConsulRequest.generate_container_payload(container, host, config)
        url = consul_url + "/v1/agent/service/register"
        if consul_token:
            url += "?token=" + consul_token
        for payload in payloads:
            try:
                if payload["ID"] not in registered_container:
                    r = requests.post(url, json=payload, timeout=3)
                    print("Agent Register Container: " + payload["ID"] + ", Result: " + str(r.status_code))
            except requests.HTTPError:
                print("HTTPError: register container " + payload["ID"])
                continue
            except requests.ConnectionError:
                print("ConnectionError: register container " + payload["ID"])
                continue
            except requests.Timeout:
                print("Timeout: register container " + payload["ID"])
                continue
            container_ids.append(payload["ID"])

        return container_ids

    @staticmethod
    def agent_deregister_service(service_id, consul_url, consul_token=None):
        """
        :param service_id: str
        :param consul_url: str
        :param consul_token: str
        :return: None
        """
        url = consul_url + "/v1/agent/service/deregister/"+service_id
        if consul_token:
            url += "?token=" + consul_token
        try:
            r = requests.post(url, timeout=3)
            print("Agent Deregister Service: " + service_id + ", Result: " + str(r.status_code))
        except requests.HTTPError:
            print("HTTPError: deregister service " + service_id)
            return
        except requests.ConnectionError:
            print("ConnectionError: deregister service " + service_id)
            return
        except requests.Timeout:
            print("Timeout: deregister service " + service_id)
            return

    @staticmethod
    def register_consul_client(service, host, consul_url, consul_token=None):
        """
        :param service: Service
        :param host: Host
        :param consul_url: str
        :param consul_token: str
        :return: None
        """
        payloads = ConsulRequest.generate_location_payload(False, False, service.locations, service.stack_name,
                                                           service.name, host.name, host, host.agent_ip)
        url = consul_url + "/v1/agent/service/register"
        if consul_token:
            url += "?token=" + consul_token
        for payload in payloads:
            try:
                r = requests.post(url, json=payload, timeout=3)
                print("Agent Register consul client: " + payload["ID"] + ", Result: " + str(r.status_code))
            except requests.HTTPError:
                print("HTTPError: register consul client " + payload["ID"])
                continue
            except requests.ConnectionError:
                print("ConnectionError: register consul client " + payload["ID"])
                continue
            except requests.Timeout:
                print("Timeout: register consul client " + payload["ID"])
                continue

    @staticmethod
    def generate_container_payload(container, host, config):
        """
        :param container: Container
        :param host: Host
        :param config: Configuration
        :return: List[dict]
        """
        payloads = []

        # tcp payload
        for i in container.tcp_ports:
            p = i.split(":")
            if len(p) < 2:
                print("Bad tcpport format: " + i + ", ignored.")
                continue
            tmp = {
                "ID": (container.name + "-" + i).replace(":", "-"),
                "Name": container.stack_name+'-'+container.service_name,
                "Tags": [],
                "Address": host.agent_ip,
                "Port": int(p[0])
            }
            if not config.enable_tcp:
                tmp["Tags"].append("tcp:"+p[0]+":"+p[1])
            else:
                tmp["Tags"].append("tcpport:"+p[0])
            try:
                for sp in p[2:]:
                    tmp["Tags"].append(sp)
            except IndexError:
                pass
            payloads.append(tmp)

        # container payload
        payloads.extend(ConsulRequest.generate_location_payload(container.is_lb, True, container.locations,
                                                                container.stack_name, container.service_name,
                                                                container.name, host, container.ips[0],
                                                                ))

        return payloads

    @staticmethod
    def generate_location_payload(is_lb, health_check, location, stack_name, service_name, name, host,
                                  rancher_ip):
        """
        :param is_lb: Boolean
        :param health_check: Boolean
        :param location: str
        :param stack_name: str
        :param service_name: str
        :param name: str
        :param host: Host
        :param rancher_ip: str
        :return: rtype: List[dict]
        """
        payloads = []
        for i in location:
            tmp = {
                "Name": stack_name+'-' + service_name,
                "Address": host.agent_ip,
                "Tags": []
            }

            provide_location = i.split(":")
            if len(provide_location) < 3:
                print("Bad location format: " + i)
                continue
            public_port = provide_location[0]
            private_port = provide_location[1]
            loc = provide_location[2]
            try:
                path = provide_location[3]
                if path:
                    tmp["Tags"].append("path:"+path)
                for sp in provide_location[4:]:
                    tmp["Tags"].append(sp)
            except IndexError:
                pass

            tmp["Port"] = int(public_port)
            tmp["ID"] = (name + '-' + public_port + '-' + loc).replace("/", "-")
            tmp["Tags"].append("loc:"+loc)

            if is_lb and health_check:
                tmp["Check"] = {
                    "HTTP": "http://"+rancher_ip+":"+public_port+loc,
                    "Interval": "10s"
                }
            elif health_check:
                tmp["Check"] = {
                    "HTTP": "http://"+rancher_ip+":"+private_port+loc,
                    "Interval": "10s"
                }
            payloads.append(tmp)
        return payloads







