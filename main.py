import os
import time
from threading import Thread
import consulrequest
import metadatarequest


def start_host_container_agent_register():
    curr_registered_services = []
    sleep_time = os.environ.get("TIME", "10")
    consul_url = os.environ.get("CONSUL", "http://localhost:8500")
    if not str.startswith(consul_url, "http://"):
        consul_url = "http://"+consul_url
    register_host = metadatarequest.MetadataRequest.get_self_host()
    if not register_host:
        print("Cannot get host information")
        return
    while True:
        register_containers = []
        need_register_containers = metadatarequest.MetadataRequest.get_all_register_containers()

        for i in need_register_containers:
            if i.host_uuid == register_host.uuid:
                register_containers.extend(consulrequest.ConsulRequest.agent_register_container(i,
                                                                                                register_host,
                                                                                                consul_url,
                                                                                                curr_registered_services
                                                                                                ))
        for n in curr_registered_services:
            if n not in register_containers:
                consulrequest.ConsulRequest.agent_deregister_service(n, consul_url)

        curr_registered_services = register_containers
        time.sleep(int(sleep_time))


def main():
    thread = Thread(target=start_host_container_agent_register)
    thread.start()
    thread.join()

if __name__ == "__main__":
    main()
