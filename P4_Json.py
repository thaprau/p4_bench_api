import os
import json
from model import Node, Link, Switch

network_config = {}
table_config = {}

#Key definitions in the built up dict
SWITCHES_KEY = "switches"
USED_PORTS_KEY = "used_ports"

NODES_KEY = "nodes"

LINKS_KEY = "links"



def CreateJson(path, data):
    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)

def CreateNode(name, ipv4_addr):
    if not NODES_KEY in network_config:
        network_config[NODES_KEY] = {}
    
    node = {}
    node[USED_PORTS_KEY] = []
    node["ipv4_addr"] = ipv4_addr
    network_config[NODES_KEY][name] = node

def LinkNodeToNode(node1_name, node2_name):
    if not LINKS_KEY in network_config:
        network_config[LINKS_KEY] = []
    
    link = {}
    link["type"] = "Node_to_Node"
    link["device1"] = node1_name
    link["device2"] = node2_name

    network_config[LINKS_KEY].append(link)
    
def LinkNodeToSwitch(node_name, switch_name, switch_port=-1, node_port=-1):
    if not LINKS_KEY in network_config:
        network_config[LINKS_KEY] = []

    link = {}
    link["type"] = "Node_to_Switch"
    link["device1"] = node_name
    link["device2"] = switch_name

    used_ports_on_switch = network_config[SWITCHES_KEY][switch_name][USED_PORTS_KEY]

    if switch_port >= 0:
        if switch_port in used_ports_on_switch:
            raise Exception("Port is already in use. Define different port")
        link["switch_port"] = switch_port
        network_config[SWITCHES_KEY][switch_name][USED_PORTS_KEY].append(switch_port)
    else:
        port_nr = GenerateSwitchPort(switch_name)
        link["switch_port"] = port_nr
        network_config[SWITCHES_KEY][switch_name][USED_PORTS_KEY].append(GenerateSwitchPort(switch_name))

    if node_port >= 0:
        if node_port in network_config[NODES_KEY][node_name][USED_PORTS_KEY]:
            raise Exception("Port is already in use. Define different port")
        link["node_port"] = node_port
        network_config[NODES_KEY][node_name][USED_PORTS_KEY].append(node_port)
    else:
        port_nr = GenerateNodePort(node_name)
        link["node_port"] = port_nr
        network_config[NODES_KEY][node_name][USED_PORTS_KEY].append(port_nr)
    network_config[LINKS_KEY].append(link)

def GenerateNodePort(node_name):
    used_ports = network_config[NODES_KEY][node_name][USED_PORTS_KEY]
    port_nr = 0

    while port_nr in used_ports:
        port_nr += 1
    
    return port_nr
#Switch commands
def CreateSwitch(switch_name):
    if not SWITCHES_KEY in network_config:
        network_config[SWITCHES_KEY] = {}
    
    switch = {}
    switch[USED_PORTS_KEY] = []

    network_config[SWITCHES_KEY][switch_name] = switch
    
def GenerateSwitchPort(switch_name):
    used_ports = network_config[SWITCHES_KEY][switch_name][USED_PORTS_KEY]
    port_nr = 0

    while port_nr in used_ports:
        port_nr += 1
    
    return port_nr
     

def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))


    CreateSwitch("Switch1")
    CreateSwitch("Switch2")

    CreateNode("Node1", "192.168.1.1")
    CreateNode("Node2", "192.168.1.2")
    CreateNode("Node3", "192.168.1.3")
    CreateNode("Node4", "192.168.1.4")

    LinkNodeToSwitch("Node1", "Switch1")
    LinkNodeToSwitch("Node2", "Switch1")
    LinkNodeToSwitch("Node3", "Switch1")
    LinkNodeToSwitch("Node4", "Switch1")

    CreateNode("Node5", "192.168.1.5")
    CreateNode("Node6", "192.168.1.6")
    CreateNode("Node7", "192.168.1.7")
    CreateNode("Node8", "192.168.1.8")

    LinkNodeToSwitch("Node5", "Switch2")
    LinkNodeToSwitch("Node6", "Switch2")
    LinkNodeToSwitch("Node7", "Switch2")
    LinkNodeToSwitch("Node8", "Switch2")

    #CreateJson(dir_path + "/test.json", network_config)

    CreateJson("/home/sdn/benchexec/contrib/p4/test.json", network_config)

if __name__ == "__main__":
    main()

