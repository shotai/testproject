import metadatarequest
import os
import service
import consulrequest
import threading
import time


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
        # register_services = []
        gateway_service = metadatarequest.MetadataRequest.get_other_service(gateway_services_name)
        register_services = register_to_consul(gateway_service.links, gateway_service.stack_name,
                                               curr_registered_services, register_host,
                                               consul_url, "location", register_method)
        # for link_service in gateway_service.links:
        #     tmp_service_name = gateway_service.stack_name + '/' + link_service
        #     if tmp_service_name not in curr_registered_services:
        #         tmp_service = metadatarequest.MetadataRequest.get_other_service(link_service)
        #         register_to_consul(tmp_service, register_host, consul_url, "location", register_method)
        #     register_services.append(tmp_service_name)

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
                    tmp_service.tags.append(label)
                    register_method(tmp_service, register_host, consul_url)
            except KeyError:
                print("No " + label_name + " label in " + tmp_service + ", skipped.")
                continue
        register_services.append(tmp_service_name)

    return register_services


def start_tcp_stack_agent_register(gateway_services_name, register_host, consul_url):
    start_tcp_agent_register(register_host, consul_url, False)
    # curr_registered_services = []
    # while True:
    #     register_services = []
    #     tmp_stack = metadatarequest.MetadataRequest.get_self_stack()
    #     for stack_service in tmp_stack.services:
    #         tmp_service = metadatarequest.MetadataRequest.get_other_service(stack_service)
    #         tmp_service_full_name = tmp_service.stack_name + "/" + stack_service
    #         if tmp_service_full_name not in curr_registered_services:
    #             try:
    #                 for port in tmp_service.labels['tcpport'].split(","):
    #                     tmp_service.tags.append(port)
    #                     consulrequest.ConsulRequest.agent_register_service(tmp_service, register_host, consul_url)
    #             except KeyError:
    #                 print("No tcpport label in " + stack_service)
    #                 continue
    #         register_services.append(tmp_service_full_name)
    #
    #     for i in curr_registered_services:
    #         if i not in register_services:
    #             consulrequest.ConsulRequest.agent_deregister_service(i, consul_url)
    #     curr_registered_services = register_services
    #
    #     time.sleep(5)


def start_tcp_link_agent_register(gateway_services_name, register_host, consul_url):
    start_tcp_agent_register(register_host, consul_url, True)
    # curr_registered_services = []
    # while True:
    #     register_services = []
    #     self_service = metadatarequest.MetadataRequest.get_self_service()
    #     for stack_service in self_service.links:
    #         tmp_service = metadatarequest.MetadataRequest.get_other_service(stack_service)
    #         tmp_service_full_name = tmp_service.stack_name + "/" + stack_service
    #         try:
    #             ports = tmp_service.labels['tcpport']
    #             register_services.append(tmp_service_full_name)
    #         except KeyError:
    #             print("No tcpport label in " + stack_service)
    #             continue
    #         if tmp_service_full_name not in curr_registered_services:
    #             for port in ports.split(","):
    #                 tmp_service.tags.append(port)
    #                 consulrequest.ConsulRequest.agent_register_service(tmp_service, register_host, consul_url)
    #
    #     for i in curr_registered_services:
    #         if i not in register_services:
    #             consulrequest.ConsulRequest.agent_deregister_service(i, consul_url)
    #     curr_registered_services = register_services
    #
    #     time.sleep(5)


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
        # self_service = metadatarequest.MetadataRequest.get_self_service()
        # for stack_service in self_service.links:
        #     tmp_service = metadatarequest.MetadataRequest.get_other_service(stack_service)
        #     tmp_service_full_name = tmp_service.stack_name + "/" + stack_service
        #     try:
        #         ports = tmp_service.labels['tcpport']
        #         register_services.append(tmp_service_full_name)
        #     except KeyError:
        #         print("No tcpport label in " + stack_service)
        #         continue
        #     if tmp_service_full_name not in curr_registered_services:
        #         for port in ports.split(","):
        #             tmp_service.tags.append(port)
        #             consulrequest.ConsulRequest.agent_register_service(tmp_service, register_host, consul_url)

        for i in curr_registered_services:
            if i not in register_services:
                consulrequest.ConsulRequest.agent_deregister_service(i, consul_url)
        curr_registered_services = register_services

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
        "agentLinkTcp": start_tcp_link_agent_register}
    # gateway_services_name = metadatarequest.MetadataRequest.get_self_service().links[0]
    gateway_service = metadatarequest.MetadataRequest.get_other_service(gateway_services_name)
    register_host = metadatarequest.MetadataRequest.get_host()
    register_host.port = gateway_service.ports[0].split(":")[0]
    register_host.dc = data_center

    for i in register_mode.split(","):
        mode = mode_switcher.get(i, start_agent_link_register)
        threading.Thread(name=register_mode,
                         target=mode(gateway_services_name, register_host, consul_url),
                         daemon=True).start()

    v = input("press any key to exit.")


if __name__ == "__main__":
    main()
