import concurrent.futures
import os
import time
import service
import consulrequest
import metadatarequest


def start_label_register(gateway_services_name, register_host, consul_url):
    curr_registered_services = []
    print("Start label register")
    while True:
        register_services = []
        gateway_service = metadatarequest.MetadataRequest.get_other_service(gateway_services_name)
        for label_key, label_value in gateway_service.labels.items():
            if label_key.startswith("io.rancher.loadbalancer.target"):
                tmp_service_name = gateway_service.stack_name + '/' + label_key.split(".")[-1]
                if tmp_service_name not in curr_registered_services:
                    tmp_service = service.Service()
                    tmp_service.name = label_key.split(".")[-1]
                    tmp_service.tags.append(label_value.split("=")[0])
                    tmp_service.stack_name = gateway_service.stack_name
                    consulrequest.ConsulRequest.remote_register_service(tmp_service, register_host, consul_url)
                register_services.append(tmp_service_name)

        for i in curr_registered_services:
            if i not in register_services:
                consulrequest.ConsulRequest.remote_deregister_service(i, register_host, consul_url)
        curr_registered_services = register_services

        time.sleep(5)


def start_remote_link_register(gateway_services_name, register_host, consul_url):
    print("Start remote link register")
    start_link_register(gateway_services_name, register_host, consul_url, True)


def start_agent_link_register(gateway_services_name, register_host, consul_url):
    print("Start agent link register")
    start_link_register(gateway_services_name, register_host, consul_url, False)


def start_link_register(gateway_services_name, register_host, consul_url, is_remote):
    curr_registered_services = []
    if is_remote:
        register_method = consulrequest.ConsulRequest.remote_register_service
        deregister_method = consulrequest.ConsulRequest.remote_deregister_service
    else:
        register_method = consulrequest.ConsulRequest.agent_register_service
        deregister_method = consulrequest.ConsulRequest.agent_deregister_service

    while True:
        gateway_service = metadatarequest.MetadataRequest.get_other_service(gateway_services_name)
        register_services = register_to_consul(gateway_service.links, gateway_service.stack_name,
                                               curr_registered_services, register_host,
                                               consul_url, "location", register_method)

        for i in curr_registered_services:
            if i not in register_services:
                deregister_method(i, register_host, consul_url)
        curr_registered_services = register_services

        time.sleep(5)


def register_to_consul(services_name, stack_name, curr_registered_services, register_host, consul_url, label_name,
                       register_method):

    register_services = []
    for link_service in services_name:
        tmp_service_name = stack_name + '/' + link_service
        if tmp_service_name not in curr_registered_services:
            tmp_service = metadatarequest.MetadataRequest.get_other_service(link_service)
            try:
                for label in tmp_service.labels[label_name].split(','):
                    if label_name == "tcpport":
                        tmp_service.tcp_port.append(label)
                    if label_name == "location":
                        tmp_service.location.append(label)
                    # tmp_service.tags.append(label)

            except KeyError:
                continue
            register_services.extend(register_method(tmp_service, register_host, consul_url))
        else:
            register_services.append(tmp_service_name)

    return register_services


def find_host_services(host):
    host_services = []
    all_services = metadatarequest.MetadataRequest.get_all_services()
    for svc in all_services:
        if host.name == svc.hostname:
            host_services.append(svc)
    return host_services


def start_tcp_stack_agent_register(gateway_services_name, register_host, consul_url):
    start_tcp_agent_register(register_host, consul_url, False)


def start_tcp_link_agent_register(gateway_services_name, register_host, consul_url):
    start_tcp_agent_register(register_host, consul_url, True)


def start_tcp_agent_register(register_host, consul_url, is_linked):
    curr_registered_services = []
    register_method = consulrequest.ConsulRequest.agent_register_service
    while True:
        if is_linked:
            self_service = metadatarequest.MetadataRequest.get_self_service()
            stack_name = self_service.stack_name
            services_name = self_service.links

        else:
            tmp_stack = metadatarequest.MetadataRequest.get_self_stack()
            stack_name = tmp_stack.name
            services_name = tmp_stack.services

        register_services = register_to_consul(services_name, stack_name,
                                               curr_registered_services,
                                               register_host, consul_url,
                                               "tcpport", register_method)

        for i in curr_registered_services:
            if i not in register_services:
                consulrequest.ConsulRequest.agent_deregister_service(i, consul_url)
        curr_registered_services = register_services

        time.sleep(5)


def start_host_agent_register(gateway_services_name, register_host, consul_url):
    curr_registered_services = []

    while True:
        host_services = find_host_services(register_host)
        for i in host_services:
            consulrequest.ConsulRequest.agent_register_service(i, register_host, consul_url)
        for i in curr_registered_services:
            if i not in host_services:
                consulrequest.ConsulRequest.agent_deregister_service(i, consul_url)
        curr_registered_services = host_services
        time.sleep(5)


def main():
    consul_url = os.environ.get("CONSUL", "http://localhost:8500")
    data_center = os.environ.get("DATACENTER", "dc1")
    register_mode = os.environ.get("MODE", "agentLink")
    gateway_services_name = os.environ.get("GATEWAY", "gateway")
    mode_switcher = {
        "agentLink": start_agent_link_register,
        "remoteLink": start_remote_link_register,
        "label": start_label_register,
        "agentStackTcp": start_tcp_stack_agent_register,
        "agentLinkTcp": start_tcp_link_agent_register,
        "hostAgent": start_host_agent_register}

    register_host = metadatarequest.MetadataRequest.get_host()
    if not register_host:
        print("Cannot get host info")
        return
    gateway_service = metadatarequest.MetadataRequest.get_other_service(gateway_services_name)
    if gateway_service:
        register_host.port = gateway_service.ports[0].split(":")[0]
    register_host.dc = data_center

    modes = register_mode.split(",")
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(modes))

    for i in register_mode.split(","):
        mode = mode_switcher.get(i, start_agent_link_register)
        print(i)
        executor.submit(mode, gateway_services_name, register_host, consul_url)

    v = input("press any key to exit.")


if __name__ == "__main__":
    main()
