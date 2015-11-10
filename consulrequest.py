import requests


class ConsulRequest:

    @staticmethod
    def agent_register_container(container, host, consul_url):
        container_ids = []
        payloads = ConsulRequest.generate_container_payload(container, host)
        url = consul_url + "/v1/agent/service/register"
        for payload in payloads:
            try:
                r = requests.post(url, json=payload, timeout=3)
            except requests.HTTPError:
                print("HTTPError: agent_register_container")
                continue
            except requests.ConnectionError:
                print("ConnectionError: agent_register_container")
                continue
            except requests.Timeout:
                print("Timeout: agent_register_container")
                continue
            container.print_container()
            container_ids.append(payload["ID"])
            print("Agent Register Service: " + payload["ID"] + ", Result: " + r.text)
        return container_ids

    @staticmethod
    def agent_deregister_service(service_id, consul_url):
        url = consul_url + "/v1/agent/service/deregister/"+service_id
        r = requests.post(url)
        print("Agent Deregister Service: " + service_id + ", Result: " + r.text)

    @staticmethod
    def generate_container_payload(container, host):
        payloads = []
        for i in container.tcp_ports:
            tmp = {
                "ID": container.stack_name+'-'+container.service_name+"-" + container.name + "_" + i,
                "Name": container.stack_name+'-'+container.service_name+"-" + i,
                "Tags": [i],
                "Address": host.agent_ip,
                "Port": int(i)
            }
            tmp["ID"] = tmp["ID"].replace("/","-")
            tmp["Name"] = tmp["Name"].replace("/","-")
            payloads.append(tmp)
        for i in container.locations:
            tmp = {
                "ID": container.stack_name+'-'+container.service_name+"-" + container.name + "-" + i,
                "Name": container.stack_name+'-'+container.service_name,
                "Tags": [],
                "Address": host.agent_ip,
                "Port": int(host.port),
                "Check":{}
            }
            loc = i.replace("loc:","")
            provide_location = loc.split(":")
            if len(provide_location) != 3:
                print("Bad location format: " + i)
                continue

            private_port = provide_location[1]
            public_port = provide_location[0]
            path = provide_location[2]

            tmp["Port"] = int(public_port)
            tmp["ID"] = tmp["ID"] + "-" + public_port + path
            tmp["Name"] = tmp["Name"] + "-" + public_port + path
            tmp["ID"] = tmp["ID"].replace("/","-").replace(":","-")
            tmp["Name"] = tmp["Name"].replace("/","-").replace(":","-")
            tmp["Tags"] = ["loc:"+path]
            tmp["Check"] = {
                "HTTP": "http://"+container.primary_ip+":"+private_port+path,
                "Interval": "10s"
            }
            payloads.append(tmp)
        return payloads






