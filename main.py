import time
import json
from threading import Thread
import configparser
import getopt
import sys
import consulrequest
import metadatarequest
import configuration


def initial_consul(config):
    """
    :param config:  configuration
    :return: consul_server_url, acl_token, host
    """
    if config.enable_acl:
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
    if not register_host or not register_host.agent_ip:
        print("Cannot get host information or ip")
        return
    register_host.print_host()

    if not config.consul_server:
        config.consul_server = register_host.agent_ip

    if not str.startswith(config.consul_server, "http://"):
        config.consul_server = "http://"+config.consul_server + ":8500"

    return config.consul_server, consul_token, register_host


def start_host_container_agent_register(config):
    """
    :param config: configuration
    :return: None
    """
    curr_registered_services = []
    consul_url, consul_token, register_host = initial_consul(config)
    config.print_config()

    # register consul client
    consul_client = metadatarequest.MetadataRequest.get_consul_client(config.consul_client)
    if consul_client:
        consulrequest.ConsulRequest.register_consul_client(consul_client, register_host, consul_url, consul_token)

    # register loop
    while True:
        register_containers = []
        need_register_containers = metadatarequest.MetadataRequest.get_all_register_containers(config)
        for container in need_register_containers:
            if container.host_uuid == register_host.uuid:
                register_containers.extend(
                    consulrequest.ConsulRequest.agent_register_container(container, register_host, consul_url,
                                                                         curr_registered_services, config,
                                                                         consul_token))
        for current in curr_registered_services:
            if current not in register_containers:
                consulrequest.ConsulRequest.agent_deregister_service(current, consul_url, consul_token)
        curr_registered_services = register_containers
        time.sleep(config.wait_time)


def load_config(argv):
    """
    :param argv: system input arg
    :return: configuration
    """
    config = configuration.Configuration()

    # load config file
    tmp_config = configparser.ConfigParser()
    tmp_config.read('./config.ini')
    try:
        for key in tmp_config["Registrator"]:
            if key == "enableacl":
                config.enable_acl = tmp_config.getboolean("Registrator",key)
            elif key == "enabletcp":
                config.enable_tcp = tmp_config.getboolean("Registrator",key)
            elif key == "enablelbtarget":
                config.enable_lb_target = tmp_config.getboolean("Registrator", key)
            elif key == "enablelbport":
                config.enable_lb_tcp_port = tmp_config.getboolean("Registrator", key)
            elif key == "wait":
                config.wait_time = int(tmp_config["Registrator"][key])
            elif key == "consulclient":
                config.consul_client = tmp_config["Registrator"][key]
            elif key == "consulserver":
                config.consul_server = tmp_config["Registrator"][key]
    except KeyError:
        pass

    # read from commandline
    try:
        opts, args = getopt.getopt(argv, "atlpw:s:c:",
                                   ["acl", "tcp", "lbtarget", "wait=", "consulserver=", "consulclient="])
    except getopt.GetoptError:
        print('-a/--acl                                     enable acl \n'
              '-t/--tcp                                     enable tcp register with nginx-defined tag (tcpport) \n'
              '-l/--lbtarget                                enable register with loadbalancer target label \n'
              '-p/--lbport                                  enable register with loadbalancer ports(ports have /tcp)\n'
              '-w/--wait <wait_time>                        registrator loop sleep time \n'
              '-s/--consulserver <consul_server_address>    consul server address \n'
              '-c/--consulclient <consul_client_address>    consul client address \n')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-a", "--acl"):
            config.enable_acl = True
        elif opt in ("-t", "--tcp"):
            config.enable_tcp = True
        elif opt in ("-l", "--lbtarget"):
            config.enable_lb_target = True
        elif opt in ("-p", "lbport"):
            config.enable_lb_tcp_port = True
        elif opt in ("-w", "--wait"):
            config.wait_time = int(arg)
        elif opt in ("-s", "--consulserver"):
            config.consul_server = arg
        elif opt in ("-c", "--consulclient"):
            config.consul_client = arg
    return config


def main(argv):
    config = load_config(argv)
    thread = Thread(target=start_host_container_agent_register, args=(config,))
    thread.start()
    thread.join()

if __name__ == "__main__":
    main(sys.argv[1:])
