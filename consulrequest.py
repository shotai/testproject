import requests


class ConsulRequest:

    @staticmethod
    def register_service(service, host, consul_url):
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
        print("register_service: " + service.stack_name+'/'+service.name + "result: " + r.text)

    @staticmethod
    def deregister_service(service_id, host, consul_url):
        payload = {"Datacenter": host.dc,
                   "Node": host.name,
                   "ServiceID": service_id}
        url = consul_url + "/v1/catalog/deregister"
        r = requests.post(url, json=payload)
        print("deregister_service: " + service_id + "result: " + r.text)

