import requests
import host
import container


class MetadataRequest:
    @staticmethod
    def get_host():
        try:
            res = requests.get(url="http://rancher-metadata/2015-07-25/self/host",
                               headers={"Accept": "application/json"},
                               timeout=3)
        except requests.HTTPError:
            print("HTTPError: get_host")
            return None
        except requests.ConnectionError:
            print("ConnectionError: get_host")
            return None
        except requests.Timeout:
            print("Timeout: get_host")
            return None

        res = res.json()
        try:
            if res["code"] == 404:
                return None
        except KeyError:
            pass
        except TypeError:
            pass

        tmp_host = host.Host()
        tmp_host.agent_ip = res['agent_ip']
        tmp_host.name = res['name']
        tmp_host.labels = res['labels']
        tmp_host.print_host()
        return tmp_host

    @staticmethod
    def get_all_containers():
        try:
            res = requests.get(url="http://rancher-metadata/2015-07-25/containers",
                               headers={"Accept": "application/json"},
                               timeout=3)
        except requests.HTTPError:
            print("HTTPError: get_all_containers")
            return []
        except requests.ConnectionError:
            print("ConnectionError: get_all_containers")
            return []
        except requests.Timeout:
            print("Timeout: get_all_containers")
            return []

        res = res.json()
        try:
            if res["code"] == 404:
                return []
        except KeyError:
            pass
        except TypeError:
            pass

        tmp_containers = []
        for i in res:
            tmp_container = container.Container()
            tmp_container.create_index = i['create_index']
            tmp_container.hostname = i['hostname']
            tmp_container.stack_name = i['stack_name']
            tmp_container.name=i['name']
            tmp_container.service_name = i["service_name"]
            tmp_container.ports = i['ports']
            tmp_container.labels = i['labels']
            tmp_container.primary_ip = i['primary_ip']
            try:
                for prt in tmp_container.labels["tcpports"].split(","):
                    tmp_container.tcp_ports.append(prt)
            except KeyError:
                pass

            try:
                for loc in tmp_container.labels["location"].split(","):
                    tmp_container.locations.append(loc)
            except KeyError:
                pass
            if tmp_container.stack_name and tmp_container.service_name:
                tmp_containers.append(tmp_container)
        return tmp_containers
















