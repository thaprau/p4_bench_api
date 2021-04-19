from model import Node, Switch, Link, NetworkSetup
import json

ip_addresses = []
node_ids = []
STANDARD_IP_DOMAIN = "192.168"

# Devices


def add_new_node(setup, name, ipv4_addr="", mac_addr="", node_id=""):
    """Adds a new to the setup

    Args:
        setup (NetworkSetup): The setup to add the node to
        name (str): Name of the node. Should be unique.
        ipv4_addr (str, optional): [ipv4-address of the node.]. Defaults to "".
        mac_addr (str, optional): [mac address of the node]. Defaults to "".
    """
    if node_id == "":
        node_id = generate_node_id()

    node = Node(name, ipv4_addr=ipv4_addr)
    node.id = node_id

    node_ids.append(node_id)

    if not node in setup.nodes:
        setup.add_node(node)
    else:
        print("Node with same id or name already exits")


def add_new_switch(setup, name):
    """Adds a new switch to the setup

    Args:
        setup ([NetworkSetup]): The setup to add the switch to
        name (str): Name of the switch. Should be unique
    """
    switch = Switch(name)

    if not switch in setup.switches:
        setup.add_switch(switch)


def add_switch_table(setup, switch_name, table_name):
    """Add a table definition to a switch

    Args:
        setup (NetworkSetup): Setup where the switch is defined
        switch_name (str): Name of the switch
        table_name (str): File name of the table json file. Ex table1.json
    """
    setup.update_switch_table(switch_name, table_name)


# Links
def link_node_to_node(setup, node1_name, node2_name, node1_port=-1, node2_port=-1):
    """Create a link between two nodes.

    Args:
        setup (NetworkSetup): The setup where the nodes are defined
        node1_name (str): Name of the first node
        node2_name (str): Name of the second node
        node1_port (int, optional): Define port of the connection. If -1, autogenerate port. Defaults to -1.
        node2_port (int, optional): Define port of the connection. If -1, autogenerate port. Defaults to -1.
    """
    link = Link(
        node1_name, node2_name, node1_port, node2_port, conn_type="Node_to_Node"
    )

    if not link in setup.links:
        setup.add_link(link)
        for node in setup.nodes:
            if node.name == node1_name:
                node.used_ports.append(node1_port)
            elif node.name == node2_name:
                node.used_ports.append(node2_port)


def link_node_to_switch(setup, node_name, switch_name, node_port=-1, switch_port=-1):
    """Create link between node and switch

    Args:
        setup (NetworkSetup): Setup where the switch and node are defined
        node_name (str): Name of the node
        switch_name (str): Name of the switch
        node_port (int, optional): Define port of the connection. If -1, autogenerate port. Defaults to -1.
        switch_port (int, optional): Define port of the connection. If -1, autogenerate port. Defaults to -1.
    """
    # If no port is given, generate port for node
    if node_port < 0:
        for node in setup.nodes:
            if node.name == node_name:
                node_port = node.generate_port()
    else:
        for node in setup.nodes:
            if node.name == node_name:
                node.add_port(node_port)

    # If no port is given, generate port for switch
    if switch_port < 0:
        for switch in setup.switches:
            if switch_name == switch.name:
                switch_port = switch.generate_port()
    else:
        for switch in setup.switches:
            if switch_name == switch.name:
                switch.add_port(switch_port)

    link = Link(
        node_name, switch_name, node_port, switch_port, conn_type="Node_to_Switch"
    )

    if not link in setup.links:
        setup.add_link(link)


def link_switch_to_switch(
    setup, switch1_name, switch2_name, switch1_port=-1, switch2_port=-1
):
    """Create link between two switches

    Args:
        setup (NetworkSetup): The setup where the switches are defined
        switch1_name (str): Name of the first switch
        switch2_name (str): Name of the secondc switch
        switch1_port (int, optional): Define port of the connection. If -1, autogenerate port. Defaults to -1.
        switch2_port (int, optional): Define port of the connection. If -1, autogenerate port. Defaults to -1.
    """
    # If no port is given, generate switch ports
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

    link = Link(
        switch1_name,
        switch2_name,
        switch1_port,
        switch2_port,
        conn_type="Switch_to_Switch",
    )

    if not link in setup.links:
        setup.links.append(link)


def save_to_json(setup, path):
    """Save the setup to json file. This is the file to be added as input to benchexec

    Args:
        setup (NetworkSetup): The setup which are to be save
        path (str): Path to where to save the file. Ex. /home/setup.json
    """
    data = setup.to_dict()
    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)


# Helper functions
def generate_fresh_ip(domain_name=""):
    """Generates a unused ipv4 address in a specific domain. Define a domain name to generate an ip address in a specific domain. Ex 192.168.

    Args:
        domain_name (str, optional): Define a domain name. Ex 172.1 will generate an ip address. Defaults to "".

    Returns:
        int[]: List if ints. Ex. [192, 168, 1, 1] for ip 192.168.1.1
    """
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

    # Check if ip address exits
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


def generate_node_id():
    id = 0
    while id in node_ids:
        id += 1

    return id


def main():
    setup = NetworkSetup()

    add_new_switch(setup, "Switch1")
    add_new_switch(setup, "Switch2")
    add_new_switch(setup, "Switch3")
    add_new_switch(setup, "Switch4")
    add_new_switch(setup, "Switch5")
    add_new_switch(setup, "Switch6")

    # Add table entries for the switches
    add_switch_table(setup, "Switch1", "ip_table1.json")
    add_switch_table(setup, "Switch2", "ip_table2.json")
    add_switch_table(setup, "Switch3", "ip_table3.json")
    add_switch_table(setup, "Switch4", "ip_table4.json")
    add_switch_table(setup, "Switch5", "ip_table5.json")
    add_switch_table(setup, "Switch6", "ip_table6.json")

    add_new_node(setup, "Node1", "192.168.1.1")
    add_new_node(setup, "Node2", "192.168.1.2")
    add_new_node(setup, "Node3", "192.168.1.3")
    add_new_node(setup, "Node4", "192.168.1.4")

    add_new_node(setup, "Node5", "192.168.1.5")
    add_new_node(setup, "Node6", "192.168.1.6")
    add_new_node(setup, "Node7", "192.168.1.7")
    add_new_node(setup, "Node8", "192.168.1.8")

    add_new_node(setup, "Node9", "192.168.1.9")
    add_new_node(setup, "Node10", "192.168.1.10")
    add_new_node(setup, "Node11", "192.168.1.11")
    add_new_node(setup, "Node12", "192.168.1.12")

    add_new_node(setup, "Node13", "192.168.1.13")
    add_new_node(setup, "Node14", "192.168.1.14")
    add_new_node(setup, "Node15", "192.168.1.15")
    add_new_node(setup, "Node16", "192.168.1.16")

    add_new_node(setup, "Node13", "192.168.1.13")
    add_new_node(setup, "Node14", "192.168.1.14")
    add_new_node(setup, "Node15", "192.168.1.15")
    add_new_node(setup, "Node16", "192.168.1.16")

    add_new_node(setup, "Node17")

    link_node_to_switch(setup, "Node1", "Switch1")
    link_node_to_switch(setup, "Node2", "Switch1")
    link_node_to_switch(setup, "Node3", "Switch2")
    link_node_to_switch(setup, "Node4", "Switch2")

    # Long chain of switches test
    link_switch_to_switch(setup, "Switch2", "Switch3", 51, 50)
    link_switch_to_switch(setup, "Switch3", "Switch4", 51, 50)
    link_switch_to_switch(setup, "Switch4", "Switch5", 51, 50)
    link_switch_to_switch(setup, "Switch5", "Switch6", 51, 50)
    link_node_to_switch(setup, "Node16", "Switch6", 0, 0)

    # link_node_to_switch(setup, "Node5", "Switch1")
    # link_node_to_switch(setup, "Node6", "Switch1")
    # link_node_to_switch(setup, "Node7", "Switch2")
    # link_node_to_switch(setup, "Node8", "Switch2")

    # link_node_to_switch(setup, "Node9", "Switch1")
    # link_node_to_switch(setup, "Node10", "Switch1")
    # link_node_to_switch(setup, "Node11", "Switch2")
    # link_node_to_switch(setup, "Node12", "Switch2")

    link_node_to_switch(setup, "Node1", "Switch2")
    link_node_to_switch(setup, "Node2", "Switch2")

    link_switch_to_switch(setup, "Switch1", "Switch2", 100, 100)

    setup.check_for_errors()
    save_to_json(setup, "/home/p4/p4_bench_api/testing/test2.json")
    save_to_json(setup, "/home/p4/benchexec/contrib/p4/network_config.json")


if __name__ == "__main__":
    main()