import requests
import host
import service
import stack
import container

class MetadataRequest:
    @staticmethod
    def get_host():
        try:
            res = requests.get(url="http://rancher-metadata/2015-07-25/self/host",
                               headers={"Accept": "application/json"})
        except requests.HTTPError:
            print("HTTPError: get host")
            return None
        res = res.json()
        tmp_host = host.Host()
        tmp_host.agent_ip = res['agent_ip']
        tmp_host.name = res['name']
        tmp_host.labels = res['labels']
        tmp_host.print_host()
        return tmp_host



    @staticmethod
    def get_self_service():
        try:
            res = requests.get(url="http://rancher-metadata/2015-07-25/self/service",
                               headers={"Accept": "application/json"})
        except requests.HTTPError:
            print("HTTPError: get self service")
            return None
        res = res.json()
        tmp_service = service.Service()
        tmp_service.name = res['name']
        tmp_service.hostname = res['hostname']
        tmp_service.stack_name = res['stack_name']
        tmp_service.ports = res['ports']
        tmp_service.labels = res['labels']
        #tmp_service.links = res['links']
        for k, v in res['links'].items():
            tmp_service.links.append(k.split("/")[1])

        return tmp_service

    @staticmethod
    def get_self_stack():
        try:
            res = requests.get(url="http://rancher-metadata/2015-07-25/self/stack",
                               headers={"Accept": "application/json"})
        except requests.HTTPError:
            print("HTTPError: get self stack")
            return None
        res = res.json()
        tmp_stack = stack.Stack()
        tmp_stack.name = res['name']
        for i in res['services']:
            tmp_stack.services.append(i)

        return tmp_stack

    @staticmethod
    def get_other_service(name):
        try:
            res = requests.get(url="http://rancher-metadata/2015-07-25/services/"+name,
                               headers={"Accept": "application/json"})
        except requests.HTTPError:
            print("HTTPError: get other service")
            return None
        res = res.json()
        try:
            if res["code"] == 404:
                return None
        except KeyError:
            pass
        tmp_service = service.Service()
        tmp_service.name = res['name']
        tmp_service.hostname = res['hostname']
        tmp_service.stack_name = res['stack_name']
        tmp_service.ports = res['ports']
        tmp_service.labels = res['labels']
        #tmp_service.links = res['links']
        for k, v in res['links'].items():
            tmp_service.links.append(k.split("/")[1])

        return tmp_service

    @staticmethod
    def get_all_services():
        try:
            res = requests.get(url="http://rancher-metadata/2015-07-25/services",
                               headers={"Accept": "application/json"})
        except requests.HTTPError:
            print("HTTPError: get all services")
            return []

        res = res.json()
        print(res)
        try:
            if res["code"] == 404:
                return []
        except KeyError:
            pass
        tmp_services = []
        for i in res:
            tmp_service = service.Service()
            tmp_service.name = i['name']
            tmp_service.hostname = i['hostname']
            tmp_service.stack_name = i['stack_name']
            tmp_service.ports = i['ports']
            tmp_service.labels = i['labels']

            for prt in tmp_service.ports:
                p = prt.split("/")
                if len(p) > 1 and p[1] == 'tcp':
                    tmp_service.tcp_ports.append(p[0].split(":")[0])
                else:
                    tmp_service.public_ports.append(p[0].split(":")[0])

            try:
                for loc in tmp_service.labels["location"]:
                    tmp_service.location.append(loc)
            except KeyError:
                pass
            tmp_services.append(tmp_service)
        return tmp_services

    @staticmethod
    def get_all_containers():
        try:
            res = requests.get(url="http://rancher-metadata/2015-07-25/containers",
                               headers={"Accept": "application/json"})
        except requests.HTTPError:
            print("HTTPError: get all containers")
            return []

        res = res.json()
        print(res)
        try:
            if res["code"] == 404:
                return []
        except KeyError:
            pass
        tmp_containers = []
        for i in res:
            tmp_container = container.Container()
            tmp_container.create_index = i['create_index']
            tmp_container.hostname = i['hostname']
            tmp_container.stack_name = i['stack_name']
            tmp_container.ports = i['ports']
            tmp_container.labels = i['labels']

            for prt in tmp_container.ports:
                p = prt.split("/")
                if len(p) > 1 and p[1] == 'tcp':
                    tmp_container.tcp_ports.append(p[0].split(":")[1])

            try:
                for loc in tmp_container.labels["location"]:
                    tmp_container.locations.append(loc)
            except KeyError:
                pass
            tmp_containers.append(tmp_container)
        return tmp_containers
















