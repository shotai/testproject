import requests


class ConsulRequest:
    @staticmethod
    def agent_register_container(payloads, registered_containers, consul_url, consul_token=None):
        """
        Register request to consul, return registered service ids
        :param payloads: List[dict]
        :param registered_containers: List[str]
        :param consul_url: str
        :param consul_token: str
        :return: List[str]
        """
        container_ids = []
        url = consul_url + "/v1/agent/service/register"
        if consul_token:
            url += "?token=" + consul_token
        for payload in payloads:
            try:
                if payload["ID"] not in registered_containers:
                    r = requests.post(url, json=payload, timeout=3)
                    print("Register Service ID:     " + payload["ID"] + "\n"
                          "Service Name:            " + payload["Name"] + "\n"
                          "Port:                    " + str(payload["Port"]) + "\n"
                          "Address:                 " + payload["Address"] + "\n"
                          "Tags:                    " + ",".join(payload["Tags"]) + "\n"
                          "Result:                  " + str(r.status_code) + "\n")
            except requests.HTTPError:
                print("HTTPError: register container " + payload["ID"])
                continue
            except requests.ConnectionError:
                print("ConnectionError: register container " + payload["ID"])
                continue
            except requests.Timeout:
                print("Timeout: register container " + payload["ID"])
                continue
            container_ids.append(payload["ID"])
        return container_ids

    @staticmethod
    def agent_deregister_contaienr(service_id, consul_url, consul_token):
        """
        Deregister service from consul
        :param service_id: str
        :param consul_url: str
        :param consul_token: str
        """
        url = consul_url + "/v1/agent/service/deregister/"+service_id
        if consul_token:
            url += "?token=" + consul_token
        try:
            r = requests.post(url, timeout=3)
            print("Deregister Service ID:   " + service_id + "\n"
                  "Result:                  " + str(r.status_code) + "\n")
        except requests.HTTPError:
            print("HTTPError: deregister service " + service_id)
            return
        except requests.ConnectionError:
            print("ConnectionError: deregister service " + service_id)
            return
        except requests.Timeout:
            print("Timeout: deregister service " + service_id)
            return







