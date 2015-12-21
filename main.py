import os
import time
import json
from threading import Thread
import consulrequest
import metadatarequest


def initial_consul():
    enable_acl = os.environ.get("ENABLEACL", "True")
    if enable_acl == "True":
        try:
            with open("/registersrc/client_acl_token.json") as acl:
                acl_token = json.load(acl)
                consul_token = acl_token["ID"]
        except IOError:
            print("Cannot find token json file. ")
            return
    else:
        consul_token = None

    register_host = metadatarequest.MetadataRequest.get_self_host()
    if not register_host:
        print("Cannot get host information")
        return
    consul_url = os.environ.get("CONSUL", register_host.agent_ip)
    if not consul_url:
        print("Cannot get consul address")
        return
    if not str.startswith(consul_url, "http://"):
        consul_url = "http://"+consul_url + ":8500"
    return consul_url, consul_token, register_host


def start_host_container_agent_register():
    curr_registered_services = []
    sleep_time = os.environ.get("TIME", "10")
    consul_url, consul_token, register_host = initial_consul()
    consul_client = metadatarequest.MetadataRequest.get_consul_client(os.environ.get("CONSULCLIENT", "consulclient"))
    if consul_client:
        consulrequest.ConsulRequest.register_consul_client(consul_client, register_host, consul_url, consul_token)

    while True:
        register_containers = []
        
        need_register_containers = metadatarequest.MetadataRequest.get_all_register_containers()
        
        for i in need_register_containers:
            if i.host_uuid == register_host.uuid:
                register_containers.extend(
                    consulrequest.ConsulRequest.agent_register_container(i, register_host, consul_url,
                                                                         curr_registered_services,
                                                                         consul_token))
        for n in curr_registered_services:
            if n not in register_containers:
                consulrequest.ConsulRequest.agent_deregister_service(n, consul_url, consul_token)

        curr_registered_services = register_containers
        time.sleep(int(sleep_time))


def main():

    thread = Thread(target=start_host_container_agent_register)
    thread.start()
    thread.join()

if __name__ == "__main__":
    main()
