import requests


class ConsulRequest:

    @staticmethod
    def remote_register_service(service, host, consul_url):
        payload = {"Datacenter": host.dc,
                   "Node": host.name,
                   "Address": host.agent_ip,
                   "Service": {
                       "ID": service.stack_name+'/'+service.name,
                       "Service": service.name,
                       "Tags": service.tags,
                       "Address": host.agent_ip,
                       "Port": int(host.port)
                   }}
        url = consul_url + "/v1/catalog/register"
        r = requests.post(url, json=payload)
        service.print_service()
        print("Remote Register Service: " + service.stack_name+'/'+service.name + ", Result: " + r.text)

    @staticmethod
    def agent_register_service(service, host, consul_url):
        payload = {
                   "ID": service.stack_name+'/'+service.name,
                   "Name": service.name,
                   "Tags": service.tags,
                   "Address": host.agent_ip,
                   "Port": int(host.port)
                   }
        url = consul_url + "/v1/agent/service/register"
        r = requests.post(url, json=payload)
        service.print_service()
        print("Agent Register Service: " + service.stack_name+'/'+service.name + ", Result: " + r.text)

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

