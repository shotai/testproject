import requests


class ConsulRequest:

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
            path = provide_location[1] if len(provide_location) == 2 else provide_location[0]
            tmp["Port"] = int(provide_location[0]) if len(provide_location) == 2 else tmp["Port"]
            whole_path = str(tmp["Port"]) + path
            tmp["ID"] = tmp["ID"] + "-" + whole_path
            tmp["Name"] = tmp["Name"] + "-" + whole_path
            tmp["ID"] = tmp["ID"].replace("/","-").replace(":","-")
            tmp["Name"] = tmp["Name"].replace("/","-").replace(":","-")
            tmp["Tags"] = ["loc:"+path]
            tmp["Check"] = {
                "HTTP": "http://"+host.agent_ip+":"+whole_path,
                "Interval": "10s"
            }
            payloads.append(tmp)
        return payloads






