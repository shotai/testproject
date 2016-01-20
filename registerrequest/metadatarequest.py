import requests


class MetadataRequest:
    @staticmethod
    def get_all_containers_metadata():
        """
        Get containers metadata request, return response
        :return: dict
        """
        try:
            res = requests.get(url="http://rancher-metadata/latest/containers",
                               headers={"Accept": "application/json"},
                               timeout=3)
        except requests.HTTPError:
            print("HTTPError: get all containers metadata")
            return []
        except requests.ConnectionError:
            print("ConnectionError: get all containers metadata")
            return []
        except requests.Timeout:
            print("Timeout: get all containers metadata")
            return []

        res = res.json()
        try:
            if res["code"] == 404:
                print("Metadata error, cannot get all containers metadata")
                return []
        except KeyError:
            pass
        except TypeError:
            pass

        return res

    @staticmethod
    def get_self_host_metadata():
        """
        Get host metadata request, return response
        :return: dict
        """
        try:
            res = requests.get(url="http://rancher-metadata/latest/self/host",
                               headers={"Accept": "application/json"},
                               timeout=3)
        except requests.HTTPError:
            print("HTTPError: get_self_host")
            return None
        except requests.ConnectionError:
            print("ConnectionError: get_self_host")
            return None
        except requests.Timeout:
            print("Timeout: get_self_host")
            return None

        res = res.json()
        try:
            if res["code"] == 404:
                print("Metadata error, cannot get host")
                return None
        except KeyError:
            pass
        except TypeError:
            pass
        return res

    @staticmethod
    def get_service_metadata(name):
        """
        Get service metadata request, return response
        :param name: str
        :return: dict
        """
        try:
            res = requests.get(url="http://rancher-metadata/latest/services/"+name,
                               headers={"Accept": "application/json"},
                               timeout=3)
        except requests.HTTPError:
            print("HTTPError: get service "+name+" metadata")
            return []
        except requests.ConnectionError:
            print("ConnectionError: get service "+name+" metadata")
            return []
        except requests.Timeout:
            print("Timeout: get service "+name+" metadata")
            return []

        res = res.json()
        try:
            if res["code"] == 404:
                print("Metadata error, cannot get service "+name+" metadata.")
                return []
        except KeyError:
            pass
        except TypeError:
            pass
        return res










































