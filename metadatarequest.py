import requests
import stack
import host
import service


class MetadataRequest:
    @staticmethod
    def get_host():
        res = requests.get("http://rancher-metadata/2015-07-25/self/host", header={"Accept":"application/json"})
        res.json()
        print(res)
        tmp_host = host.Host()
        tmp_host.agent_ip = res.agent_ip
        tmp_host.name = res.name
        tmp_host.uuid = res.uuid
        for k,v in res.labels:
            tmp_host.add_labels(k, v)
        return tmp_host

    @staticmethod
    def get_stack():
        res = requests.get("http://rancher-metadata/2015-07-25/self/stack", header={"Accept":"application/json"})
        res.json()
        print(res)
        tmp_stack = stack.stack()
        tmp_stack.name = res.name
        tmp_stack.environment_name = res.environment_name
        for i in res.services:
            tmp_stack.add_service(i)
        return tmp_stack

    @staticmethod
    def get_service(name):
        res = requests.get("http://rancher-metadata/2015-07-25/services/"+name, header={"Accept":"application/json"})
        res.json()
        print(res)
        tmp_service = service.Service()
        tmp_service.name = res.name
        tmp_service.hostname = res.hostname
        tmp_service.metadata = res.metadata
        for i in res.ports:
            tmp_service.add_port(i)
        










