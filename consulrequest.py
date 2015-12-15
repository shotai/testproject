import requests


class ConsulRequest:
    @staticmethod
    def agent_register_container(container, host, consul_url, registered_container, consul_token=None):
        container_ids = []
        payloads = ConsulRequest.generate_container_payload(container, host)
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
    def agent_deregister_service(service_id, consul_url, consul_token):
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
    def generate_container_payload(container, host):
        payloads = []

        # tcp payload
        for i in container.tcp_ports:
            ports = i.replace("tcpport:", "")
            p = ports.split(":")
            if len(p) != 2:
                print("Bad tcpport format: " + i)
                continue
            tmp = {
                "ID": container.name + "-" + i,
                "Name": container.stack_name+'-'+container.service_name,
                "Tags": ["tcpport:"+p[0]],
                "Address": host.agent_ip,
                "Port": int(p[0])
            }
            payloads.append(tmp)

        # container payload
        payloads.extend(ConsulRequest.generate_location_payload(False, True, container.locations,
                                                                container.stack_name, container.service_name,
                                                                container.name, host, container.ips[0]))

        # load balancer payload
        payloads.extend(ConsulRequest.generate_location_payload(True, True, container.lb_locations,
                                                                container.stack_name, container.service_name,
                                                                container.name, host, container.ips[0]))
        return payloads

    @staticmethod
    def generate_location_payload(use_lb, health_check, locations, stack_name, service_name, name, host, primary_ip):
        payloads = []
        for i in locations:
            tmp = {
                "Name": stack_name+'-'+service_name,
                "Address": host.agent_ip
            }
            loc = i.replace("loc:", "")
            provide_location = loc.split(":")
            if len(provide_location) != 3 and len(provide_location) != 4:
                print("Bad location format: " + i)
                continue
            public_port = provide_location[0]
            private_port = provide_location[1]
            loc = provide_location[2]
            try:
                path = provide_location[3]
            except IndexError:
                path = None
                pass
            tmp["Port"] = int(public_port)
            tmp["ID"] = (name + '-' + public_port + '-' + loc).replace("/", "-")
            tmp["Tags"] = ["loc:"+loc] if not path else ["loc:"+loc, "path:" + path]
            if use_lb and health_check:
                tmp["Check"] = {
                    "HTTP": "http://"+primary_ip+":"+public_port+loc,
                    "Interval": "10s"
                }
            elif health_check:
                tmp["Check"] = {
                    "HTTP": "http://"+primary_ip+":"+private_port+loc,
                    "Interval": "10s"
                }
            payloads.append(tmp)
        return payloads







