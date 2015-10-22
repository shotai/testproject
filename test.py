import metadatarequest
import host
import service
import register
import threading
import time

# host = metadatarequest.MetadataRequest.get_host()
# # print(host.name)
# # print(host.labels)
# stack = metadatarequest.MetadataRequest.get_stack()
# for i in stack.services:
#     a = metadatarequest.MetadataRequest.get_other_service(i)
    # print(service.name)
    # print(service.ports)
    # print(service.labels)
    # print(service.stack_name)

#time.sleep(10)


def get_register_service_tag(name):
    service1 = metadatarequest.MetadataRequest.get_other_service(name)
    try:
        service1.tags.append(service1.labels["location"])
        service1.tags.append(service1.labels['color'])
    except KeyError:
        pass
    return service


def start_register(gateway_services_name, curr_registered_services, register_services, register_host):
    while True:
        gateway_service = metadatarequest.MetadataRequest.get_other_service(gateway_services_name)
        for label_key, label_value in gateway_service.links.items():
            if label_key.startswith("io.rancher.loadbalancer.target"):
                tmp_service_name = gateway_service.stack_name+'/'+label_key.split(".")[-1]
                if tmp_service_name not in curr_registered_services:
                    tmp_service = service.Service()
                    tmp_service.name = tmp_service_name
                    tmp_service.tags.append(label_value.split("=")[0])
                    tmp_service.stack_name = gateway_service.stack_name
                    register.Register.register_service(tmp_service, register_host, "http://192.168.88.129:8500")
                register_services.append(tmp_service_name)

        for i in curr_registered_services:
            if i not in register_services:
                register.Register.deregister_service(i, register_host, "http://192.168.88.129:8500")
        curr_registered_services = register_services

        for s in register_services:
            print(s)
        time.sleep(5)


def main():

    gateway_services_name = metadatarequest.MetadataRequest.get_self_service().links[0]
    gateway_service = metadatarequest.MetadataRequest.get_other_service(gateway_services_name)
    register_host = metadatarequest.MetadataRequest.get_host()
    register_host.port = gateway_service.ports[0].split(":")[0]
    register_host.dc = "dc1"

    # register_services = []
    # curr_registered_services = []

    d = threading.Thread(name='daemon', target=start_register(gateway_services_name, [], [], register_host))
    d.setDaemon(True)
    d.start()

        # for p in gateway_service.ports:
        #     register_host.port = p.split(":")[0]

    # for i in register_services:
    #     service2 = get_register_service_tag(i)

    register_host.print_host()

    v = input("press any key to exit.")


if __name__ == "__main__":
    main()













