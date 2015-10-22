import requests
import stack
import host
import service


class MetadataRequest:
    @staticmethod
    def get_host():
        res = requests.get(url="http://rancher-metadata/2015-07-25/self/host", headers={"Accept": "application/json"})
        res = res.json()
        tmp_host = host.Host()
        tmp_host.agent_ip = res['agent_ip']
        tmp_host.name = res['name']
        tmp_host.labels = res['labels']
        return tmp_host

    @staticmethod
    def get_stack():
        res = requests.get(url="http://rancher-metadata/2015-07-25/self/stack",
                           headers={"Accept": "application/json"})
        res = res.json()
        tmp_stack = stack.Stack()
        tmp_stack.name = res['name']
        tmp_stack.environment_name = res['environment_name']
        tmp_stack.services = res['services']
        return tmp_stack

    @staticmethod
    def get_other_service(name):
        res = requests.get(url="http://rancher-metadata/2015-07-25/services/"+name,
                           headers={"Accept": "application/json"})
        res = res.json()
        print(res)
        tmp_service = service.Service()
        tmp_service.name = res['name']
        tmp_service.hostname = res['hostname']
        tmp_service.metadata = res['metadata']
        tmp_service.kind = res['kind']
        tmp_service.stack_name = res['stack_name']
        tmp_service.ports = res['ports']
        tmp_service.labels = res['labels']
        tmp_service.links = res['links']
        # for k, v in res['links'].items():
        #     tmp_service.links.append(k.split("/")[1])

        return tmp_service

    @staticmethod
    def get_self_service():
        res = requests.get(url="http://rancher-metadata/2015-07-25/self/service",
                           headers={"Accept": "application/json"})
        res = res.json()
        print(res)
        tmp_service = service.Service()
        tmp_service.name = res['name']
        tmp_service.hostname = res['hostname']
        tmp_service.metadata = res['metadata']
        tmp_service.kind = res['kind']
        tmp_service.stack_name = res['stack_name']
        tmp_service.ports = res['ports']
        tmp_service.labels = res['labels']
        tmp_service.links = res['links']
        # for k, v in res['links'].items():
        #     tmp_service.links.append(k.split("/")[1])

        return tmp_service













