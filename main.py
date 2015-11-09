import os
import time
from threading import Thread
import consulrequest
import metadatarequest


def find_host_register_containers(host):
    host_register_containers = []
    all_containers = metadatarequest.MetadataRequest.get_all_containers()
    for cont in all_containers:
        if host.name == cont.hostname and (cont.tcp_ports or cont.locations):
            host_register_containers.append(cont)
    return host_register_containers


def start_host_container_agent_register(register_host, consul_url):
    curr_registered_services = []
    while True:
        register_containers = []
        host_register_containers = find_host_register_containers(register_host)
        for i in host_register_containers:
            if i.locations or i.tcp_ports:
                register_containers.extend(consulrequest.ConsulRequest.agent_register_container(i,
                                                                                                register_host,
                                                                                                consul_url))
        print(register_containers)
        print(curr_registered_services)
        for n in curr_registered_services:
            if n not in register_containers:
                consulrequest.ConsulRequest.agent_deregister_service(n, consul_url)
        curr_registered_services = register_containers
        time.sleep(5)


def main():
    consul_url = os.environ.get("CONSUL", "http://localhost:8500")
    data_center = os.environ.get("DATACENTER", "dc1")

    register_host = metadatarequest.MetadataRequest.get_host()
    if not register_host:
        print("Cannot get host info")
        return

    register_host.dc = data_center

    thread = Thread(start_host_container_agent_register, register_host, consul_url)
    thread.start()
    thread.join()

    #v = input("press any key to exit.")


if __name__ == "__main__":
    main()
