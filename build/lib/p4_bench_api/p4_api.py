from p4_bench_api.model import Node, Switch, Link, NetworkSetup
import json

ip_addresses = []
STANDARD_IP_DOMAIN = "192.168"

#Devices
def add_new_node(setup, name, ipv4_addr="", mac_addr=""):
    node = Node(name, ipv4_addr=ipv4_addr)

    if not node in setup.nodes:
        setup.add_node(node)

def add_new_switch(setup, name):
    switch = Switch(name)

    if not switch in setup.switches:
        setup.add_switch(switch)

def add_switch_table(setup, switch_name, table_name):
    setup.update_switch_table(switch_name, table_name)

#Links
def link_node_to_node(setup, node1_name, node2_name, node1_port=-1, node2_port=-1):
    link = Link(node1_name, node2_name, node1_port, node2_port, conn_type="Node_to_Node")

    if not link in setup.links:
        setup.add_link(link)
        for node in setup.nodes:
            if node.name == node1_name:
                node.used_ports.append(node1_port)
            elif node.name == node2_name:
                node.used_ports.append(node2_port)

def link_node_to_switch(setup, node_name, switch_name, node_port=-1, switch_port=-1):
    #If no port is given, generate port for node
    if node_port < 0:
        for node in setup.nodes:
            if node.name == node_name:
                node_port = node.generate_port()
    else:
        for node in setup.nodes:
            if node.name == node_name:
                node.add_port(node_port)

    #If no port is given, generate port for switch
    if switch_port < 0:
        for switch in setup.switches:
            if switch_name == switch.name:
                switch_port = switch.generate_port()
    else:
        for switch in setup.switches:
            if switch_name == switch.name:
                switch.add_port(switch_port)

    link = Link(node_name, switch_name, node_port, switch_port,conn_type="Node_to_Switch")
    
    if not link in setup.links:
        setup.add_link(link)

def link_switch_to_switch(setup, switch1_name, switch2_name, switch1_port=-1, switch2_port=-1):
    #If no port is given, generate switch ports
    if switch1_port < 0:
        for switch in setup.switches:
            if switch1_name == switch.name:
                switch1_port = switch.generate_port()
    else:
        for switch in setup.switches:
            if switch1_name == switch.name:
                switch.add_port(switch1_port)
    if switch2_port < 0:
        for switch in setup.switches:
            if switch2_name == switch.name:
                switch2_port = switch.generate_port()
    else:
        for switch in setup.switches:
            if switch2_name == switch.name:
                switch.add_port(switch2_port)
    
    link = Link(switch1_name, switch2_name, switch1_port, switch2_port, conn_type="Switch_to_Switch")

    if not link in setup.links:
        setup.links.append(link)

def save_to_json(setup, path):
    data = setup.to_dict()
    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)

#Helper functions
def generate_fresh_ip(domain_name=""):
    
    addres_array = domain_name.split(".")
    addres_array_int = []

    if domain_name != "":
        for ele in addres_array:
            addres_array_int.append(int(ele))


    CIDR = len(addres_array_int)

    if CIDR == 0:
        if len(ip_addresses) == 0:
            addres_array_int.append(172)
            addres_array_int.append(168)
            addres_array_int.append(1)
            addres_array_int.append(1)
        else:
            for i in ip_addresses[-1]:
                addres_array_int.append(i)
    else:
        while len(addres_array_int) < 4:
            addres_array_int.append(1)

    #Check if ip address exits
    while addres_array_int in ip_addresses:
        if addres_array_int[3] < 255:
            addres_array_int[3] += 1
        else:
            if addres_array_int[2] < 255:
                addres_array_int[2] += 1
                addres_array_int[3] = 1
            else:
                if addres_array_int[1] < 255:
                    addres_array_int[1] += 1
                    addres_array_int[2] = 1
                    addres_array_int[3] = 1
                else:
                    if addres_array_int[0] < 255:
                        addres_array_int[0] += 1
                        addres_array_int[1] = 1
                        addres_array_int[2] = 1
                        addres_array_int[3] = 1
        
    ip_addresses.append(addres_array_int)

    return addres_array_int
    
def generate_fresh_mac(setup):
    nr_of_devices = len(setup.nodes) + len(setup.switches)
    
    return

def main():

    #Generate ip addresses
    nrOfAddresses = 500

    for i in range(nrOfAddresses):
        print(generate_fresh_ip(domain_name="172.168.1"))
    # setup = NetworkSetup()

    # add_new_switch(setup,"Switch1")
    # add_new_switch(setup, "Switch2")

    # #Add table entries for the switches
    # add_switch_table(setup, "Switch1", "ip_table1.json")
    # add_switch_table(setup, "Switch2", "ip_table2.json")

    # add_new_node(setup, "Node1", "192.168.1.1")
    # add_new_node(setup, "Node2", "192.168.1.2")
    # add_new_node(setup, "Node3", "192.168.1.3")
    # add_new_node(setup, "Node4", "192.168.1.4")

    # # CreateNode("Node5", "192.168.1.5")
    # # CreateNode("Node6", "192.168.1.6")
    # # CreateNode("Node7", "192.168.1.7")
    # # CreateNode("Node8", "192.168.1.8")

    # link_node_to_switch(setup, "Node1", "Switch1")
    # link_node_to_switch(setup, "Node2", "Switch1")
    # link_node_to_switch(setup, "Node3", "Switch2")
    # link_node_to_switch(setup, "Node4", "Switch2")

    # link_switch_to_switch(setup, "Switch1", "Switch2", 100, 100)

    # save_to_json(setup, "/home/sdn/p4_bench_api/testing/test2.json")
    # save_to_json(setup, "/home/sdn/benchexec/contrib/p4/network_config.json")
    # LinkNodeToSwitch("Node5", "Switch2")
    # LinkNodeToSwitch("Node6", "Switch2")
    # LinkNodeToSwitch("Node7", "Switch2")
    # LinkNodeToSwitch("Node8", "Switch2")

    #link("Switch1", "Switch2", 100, 100)

    #CreateJson(dir_path + "/testing/test.json", network_config)

    #CreateJson("/home/sdn/benchexec/contrib/p4/test.json", network_config)

if __name__=="__main__":
    main()