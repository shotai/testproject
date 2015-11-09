import requests


class ConsulRequest:

    @staticmethod
    def remote_register_service(service, host, consul_url):
        payload = {
                    "Datacenter": host.dc,
                    "Node": host.name,
                    "Address": host.agent_ip,
                    "Service": {
                        "ID": service.stack_name+'/'+service.name,
                        "Service": service.name,
                        "Tags": service.tags,
                        "Address": host.agent_ip,
                        "Port": int(host.port)
                    }
                }
        url = consul_url + "/v1/catalog/register"
        r = requests.post(url, json=payload)
        service.print_service()
        print("Remote Register Service: " + service.stack_name+'/'+service.name + ", Result: " + r.text)

    @staticmethod
    def agent_register_service(service, host, consul_url):
        # payload = {
        #             "ID": service.stack_name+'/'+service.name,
        #             "Name": service.name,
        #             "Tags": service.tags,
        #             "Address": host.agent_ip,
        #             "Port": int(host.port),
        #             "Check": {
        #                 "HTTP": "http://" + host.agent_ip + ":" + host.port + ""
        #             }
        #            }
        services_id = []
        payloads = ConsulRequest.generate_service_payload(service, host)
        url = consul_url + "/v1/agent/service/register"
        for payload in payloads:
            r = requests.post(url, json=payload)
            service.print_service()
            services_id.append(payload["ID"])
            print("Agent Register Service: " + service.stack_name+'/'+service.name + ", Result: " + r.text)
        return services_id

    @staticmethod
    def agent_register_container(container, host, consul_url):
        container_ids = []
        payloads = ConsulRequest.generate_container_payload(container, host)
        url = consul_url + "/v1/agent/service/register"
        for payload in payloads:
            r = requests.post(url, json=payload)
            container.print_container()
            container_ids.append(payload["ID"])
            print("Agent Register Service: " + payload["ID"] + ", Result: " + r.text)
        print("agent_register_container")
        print(container_ids)
        return container_ids


    @staticmethod
    def remote_deregister_service(service_id, host, consul_url):
        payload = {"Datacenter": host.dc,
                   "Node": host.name,
                   "ServiceID": service_id}
        url = consul_url + "/v1/catalog/deregister"
        r = requests.post(url, json=payload)
        print("Remote Deregister Service: " + service_id + ", Result: " + r.text)

    @staticmethod
    def agent_deregister_service(service_id, consul_url):
        url = consul_url + "/v1/agent/service/deregister/"+service_id
        r = requests.post(url)
        print("Agent Deregister Service: " + service_id + ", Result: " + r.text)

    @staticmethod
    def generate_service_payload(service, host):
        payloads = []
        for i in service.tcp_port:
            port = i.replace("prt:", "")
            tmp = {
                "ID": service.stack_name+'/'+service.name+"_" + port,
                "Name": service.name+"_"+port,
                "Tags": [i],
                "Address": host.agent_ip,
                "Port": int(port),
            }
            payloads.append(tmp)
        if service.location:
            for i in service.location:
                tmp = {
                    "ID": service.stack_name+'/'+service.name,
                    "Name": service.name,
                    "Tags": [],
                    "Address": host.agent_ip,
                    "Port": int(host.port),
                    "Check": {}
                }
                loc = i.replace("loc:", "")
                provide_location = loc.split(":")
                tmp["Port"] = int(provide_location[0]) if len(provide_location) == 2 else tmp["Port"]
                path = "".join(provide_location) if len(provide_location) == 2 else tmp["Port"]+loc
                tmp["ID"] = tmp["ID"] + "_" + path
                tmp["Name"] = tmp["Name"] + "_" + path
                tmp["Tags"] = [i]
                tmp["Check"] = {
                    "HTTP": "http://"+host.agent_ip+":"+path,
                    "Interval": "10s"
                }
                payloads.append(tmp)
        return payloads

    @staticmethod
    def generate_container_payload(container, host):
        payloads = []
        for i in container.tcp_ports:
            print("generate_container_payload1")
            tmp = {
                "ID": container.stack_name+'/'+container.service_name+"/" + container.name + "_" + i,
                "Name": container.stack_name+'/'+container.service_name+"_" + i,
                "Tags": [i],
                "Address": host.agent_ip,
                "Port": int(i)
            }
            print("generate_container_payload2")
            payloads.append(tmp)
        for i in container.locations:
            print("generate_container_payload3")
            tmp = {
                "ID": container.stack_name+'/'+container.service_name+"/" + container.name + "_" + i,
                "Name": container.stack_name+'/'+container.service_name,
                "Tags": [],
                "Address": host.agent_ip,
                "Port": int(host.port),
                "Check":{}
            }
            print("generate_container_payload4")
            loc = i.replace("loc:","")
            print(loc)
            provide_location = loc.split(":")
            print(provide_location)
            tmp["Port"] = int(provide_location[0]) if len(provide_location) == 2 else tmp["Port"]
            path = "".join(provide_location) if len(provide_location) == 2 else str(tmp["Port"])+loc
            print(path)
            tmp["ID"] = tmp["ID"] + "_" + path
            print("generate_container_payload5")
            tmp["Name"] = tmp["Name"] + "_" + path
            print("generate_container_payload6")
            tmp["Tags"] = [i]
            tmp["Check"] = {
                "HTTP": "http://"+host.agent_ip+":"+path,
                "Interval": "10s"
            }
            payloads.append(tmp)
        return payloads






