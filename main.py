import metadatarequest
import os
import service
import consulrequest
import threading
import time


def start_label_register(gateway_services_name, register_host, consul_url):
    curr_registered_services = []
    while True:
        register_services = []
        gateway_service = metadatarequest.MetadataRequest.get_other_service(gateway_services_name)
        for label_key, label_value in gateway_service.labels.items():
            if label_key.startswith("io.rancher.loadbalancer.target"):
                tmp_service_name = gateway_service.stack_name+'/'+label_key.split(".")[-1]
                if tmp_service_name not in curr_registered_services:
                    tmp_service = service.Service()
                    tmp_service.name = label_key.split(".")[-1]
                    tmp_service.tags.append(label_value.split("=")[0])
                    tmp_service.stack_name = gateway_service.stack_name
                    consulrequest.ConsulRequest.register_service(tmp_service, register_host, consul_url)
                register_services.append(tmp_service_name)

        for i in curr_registered_services:
            if i not in register_services:
                consulrequest.ConsulRequest.deregister_service(i, register_host, consul_url)
        curr_registered_services = register_services

        time.sleep(5)


def start_link_register(gateway_services_name, register_host, consul_url):
    curr_registered_services = []
    while True:
        register_services = []
        gateway_service = metadatarequest.MetadataRequest.get_other_service(gateway_services_name)
        for link_service in gateway_service.links:
            tmp_service_name = gateway_service.stack_name+'/'+link_service
            if tmp_service_name not in curr_registered_services:
                tmp_service = metadatarequest.MetadataRequest.get_other_service(link_service)
                for loc in tmp_service.labels['location'].split(","):		
                    tmp_service.tags.append(loc)
                    consulrequest.ConsulRequest.register_service(tmp_service, register_host, consul_url)
            register_services.append(tmp_service_name)

        for i in curr_registered_services:
            if i not in register_services:
                consulrequest.ConsulRequest.deregister_service(i, consul_url)
        curr_registered_services = register_services

        time.sleep(5)

def start_agent_register(gateway_services_name, register_host, consul_url):
    curr_registered_services = []
    while True:
        register_services = []
        gateway_service = metadatarequest.MetadataRequest.get_other_service(gateway_services_name)
        for link_service in gateway_service.links:
            tmp_service_name = gateway_service.stack_name+'/'+link_service
            if tmp_service_name not in curr_registered_services:
                tmp_service = metadatarequest.MetadataRequest.get_other_service(link_service)
                for loc in tmp_service.labels['location'].split(","):		
                    tmp_service.tags.append(loc)
                    consulrequest.ConsulRequest.register_agent_service(tmp_service, register_host, consul_url)
            register_services.append(tmp_service_name)

        for i in curr_registered_services:
            if i not in register_services:
                consulrequest.ConsulRequest.deregister_agent_service(i, consul_url)
        curr_registered_services = register_services

        time.sleep(5)


def main():
    consul_url = os.environ.get("CONSUL", "http://localhost:8500")
    data_center = os.environ.get("DATACENTER", "dc1")
    register_mode = os.environ.get("MODE", "agent")
    gateway_services_name = os.environ.get("GATEWAY", "gateway")
    mode_switcher = {
        "agent": start_agent_register,
        "link": start_link_register,
        "label": start_label_register}
    #gateway_services_name = metadatarequest.MetadataRequest.get_self_service().links[0]
    gateway_service = metadatarequest.MetadataRequest.get_other_service(gateway_services_name)
    register_host = metadatarequest.MetadataRequest.get_host()
    register_host.port = gateway_service.ports[0].split(":")[0]
    register_host.dc = data_center
    
    mode = mode_switcher.get(register_mode, start_agent_register) 
    d = threading.Thread(name='daemon', target=mode(gateway_services_name, register_host, consul_url))
    d.setDaemon(True)
    d.start()

    v = input("press any key to exit.")


if __name__ == "__main__":
    main()













