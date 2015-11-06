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
                "Name": service.name,
                "Tags": [i],
                "Address": host.agent_ip,
                "Port": int(port),
            }
            payloads.append(tmp)
        if service.location:
            tmp = {
                "ID": service.stack_name+'/'+service.name,
                "Name": service.name,
                "Tags": [],
                "Address": host.agent_ip,
                "Port": int(host.port),
                "checks": []
            }
            for i in service.location:
                loc = i.replace("loc:","")
                tmp["Tags"].append(i)
                tmp["checks"].append({
                    "HTTP": "http://"+host.agent_ip+":"+host.port+loc,
                    "Interval": "10s"
                })
            payloads.append(tmp)
        return payloads






