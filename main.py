import json
import os
import time
from threading import Thread
from dataprocess import metadataprocess, servicedataregister


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

    data_process = metadataprocess.MetaDataProcess()
    register_host = data_process.get_host()
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
    data_process = metadataprocess.MetaDataProcess()
    service_register = servicedataregister.ServiceDataRegister(host_ip=register_host.agent_ip,
                                                               consul_url=consul_url,
                                                               consul_token=consul_token)
    consul_client = data_process.get_consul_client(os.environ.get("CONSULCLIENT", ""))
    if consul_client:
        service_register.register_consul_client(consul_client, register_host)
    while True:
        register_containers = []
        need_register_containers = data_process.get_all_containers()

        for i in need_register_containers:
            if i.host_uuid == register_host.uuid:
                register_containers.extend(service_register.register_containers(i, curr_registered_services))
        for n in curr_registered_services:
            if n not in register_containers:
                service_register.deregister_container(n)

        curr_registered_services = register_containers
        time.sleep(int(sleep_time))


def main():

    thread = Thread(target=start_host_container_agent_register)
    thread.start()
    thread.join()

if __name__ == "__main__":
    main()
