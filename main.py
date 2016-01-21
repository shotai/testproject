import configparser
import getopt
import json
import sys
import time
from threading import Thread
from dataprocess import metadataprocess, servicedataregister
from servicestructure import configuration


def initial_consul(config, data_process):
    """
    Initialization
    :type data_process: MetaDataProcess
    :type config: Configuration
    :rtype: str, str, Host
    """
    enable_acl = config.enable_acl
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

    register_host = data_process.get_host()
    if not register_host:
        print("Cannot get host information")
        return

    consul_url = config.consul_server if config.consul_server else register_host.agent_ip
    if not consul_url:
        print("Cannot get consul address")
        return
    if not str.startswith(consul_url, "http://"):
        consul_url = "http://"+consul_url + ":8500"

    return consul_url, consul_token, register_host


def start_host_container_agent_register(config):
    """
    :type config: Configuration
    :return: None
    """
    curr_registered_services = []
    config.print_config()

    data_process = metadataprocess.MetaDataProcess(enable_lb_target=config.enable_lb_target,
                                                   enable_lb_tcp_port=config.enable_lb_tcp_port)
    consul_url, consul_token, register_host = initial_consul(config, data_process)
    service_register = servicedataregister.ServiceDataRegister(host_ip=register_host.agent_ip,
                                                               consul_url=consul_url,
                                                               consul_token=consul_token,
                                                               enable_tcp=config.enable_tcp)

    consul_client = data_process.get_consul_client(config.consul_client)
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
        time.sleep(config.wait_time)


def load_config(argv):
    """
    :type argv: str
    :rtype: rtype: Configuration
    """
    config = configuration.Configuration()

    # load config file
    tmp_config = configparser.ConfigParser()
    tmp_config.read('/registersrc/config.ini')
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
                                   ["acl", "tcp", "lbtarget", "lbport", "wait=", "consulserver=", "consulclient="])
    except getopt.GetoptError:
        print('-a/--acl                                     enable acl \n'
              '-t/--tcp                                     enable tcp register with nginx-defined tag (tcpport) \n'
              '-l/--lbtarget                                enable register with loadbalancer target label \n'
              '-p/--lbport                                  enable register with loadbalancer ports which have /tcp)\n'
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
        elif opt in ("-p", "--lbport"):
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
