import requests
class MetadataRequest:

    @staticmethod
    def get_host():
        res = requests.get("http://rancher-metadata/2015-07-25/self/host")




