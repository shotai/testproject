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
                "ID": container.stack_name+'-'+container.service_name+"-" + container.name + "-" + i,
                "Name": container.stack_name+'-'+container.service_name+"-" + i,
                "Tags": ["tcpport:"+p[0]],
                "Address": host.agent_ip,
                "Port": int(p[0])
            }
            tmp["ID"] = tmp["ID"].replace("/", "-")
            tmp["Name"] = tmp["Name"].replace("/", "-")
            payloads.append(tmp)

        # container payload
        payloads.extend(ConsulRequest.generate_location_payload(False, container.locations,
                                                                container.stack_name, container.service_name,
                                                                container.name, host, container.ips[0]))

        # load balancer payload
        payloads.extend(ConsulRequest.generate_location_payload(True, container.lb_locations,
                                                                container.stack_name, container.service_name,
                                                                container.name, host, container.ips[0]))
        return payloads

    @staticmethod
    def generate_location_payload(use_lb, locations, stack_name, service_name, name, host, primary_ip):
        payloads = []
        for i in locations:
            tmp = {
                "ID": stack_name+'-'+service_name+"-"+name,
                "Name": stack_name+'-'+service_name,
                "Tags": [],
                "Address": host.agent_ip,
                "Check": {}
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
            tmp["ID"] = (tmp["ID"] + "-" + public_port + loc).replace("/", "-").replace(":", "-")
            tmp["Name"] = (tmp["Name"] + "-" + public_port + loc).replace("/", "-").replace(":", "-")
            tmp["Tags"] = ["loc:"+loc] if not path else ["loc:"+loc, "path:" + path]
            if use_lb:
                tmp["Check"] = {
                    "HTTP": "http://"+primary_ip+":"+public_port+loc,
                    "Interval": "10s"
                }
            else:
                tmp["Check"] = {
                    "HTTP": "http://"+primary_ip+":"+private_port+loc,
                    "Interval": "10s"
                }
            payloads.append(tmp)
        return payloads







