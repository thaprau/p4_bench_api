from re import L
from .model import Node, Switch, Link, NetworkSetup
import json
import os

ip_addresses = []
node_ids = []
STANDARD_IP_DOMAIN = "192.168"

# Holds information about setup
networkSetup = NetworkSetup()
table_entries = []  # Used if user wants to create a table entries file


def add_new_node(name, ipv4_addr="", mac_addr="", node_id=""):
    """Adds a new to the setup

    Args:
        setup (NetworkSetup): The setup to add the node to
        name (str): Name of the node. Should be unique.
        ipv4_addr (str, optional): [ipv4-address of the node.]. Defaults to "".
        mac_addr (str, optional): [mac address of the node]. Defaults to "".
    """
    if node_id == "":
        node_id = generate_node_id()

    node = Node(name, ipv4_addr=ipv4_addr, mac_addr=mac_addr)
    node.id = node_id

    node_ids.append(node_id)

    if not node in networkSetup.nodes:
        networkSetup.add_node(node)
    else:
        print("Node with same id or name already exits")


def add_new_switch(name, p4_file_name, p4_info_path="", server_port=-1):
    """Adds a new switch to the setup

    Args:
        setup ([NetworkSetup]): The setup to add the switch to
        name (str): Name of the switch. Should be unique
    """

    if server_port < 0:
        server_port = generate_switch_server_port()

    switch = Switch(name, p4_file_name, p4_info_path, server_port)

    if not switch in networkSetup.switches:
        networkSetup.add_switch(switch)


def add_switch_to_setup(switch):
    switch_is_unique = True
    for sw in networkSetup.switches:
        if switch.name == sw.name:
            print(f"Switch with name {switch.name} already exits")
            switch_is_unique = False
        if switch.server_port == sw.server_port:
            print(
                f"Swtich {switch.name} invalid server port. Port already used by Switch {sw.name}"
            )
            switch_is_unique = False

    if switch_is_unique:
        networkSetup.add_switch(switch)
    else:
        print(f"Not adding Switch {switch.name} to setup")


def add_node_to_setup(node):
    node_is_unique = True
    for n in networkSetup.nodes:
        if n == node:
            print(f"Node {node.name} already exits")
            node_is_unique = False

    if node_is_unique:
        networkSetup.add_node(node)
    else:
        print(f"Not adding Node {node.name} to setup")


def add_link_to_setup(link):
    add_new_link(link.device1, link.device2, link.device1_port1, link.device2_port)


def add_switch_table(switch_name, table_name):
    """Add a table definition to a switch

    Args:
        setup (NetworkSetup): Setup where the switch is defined
        switch_name (str): Name of the switch
        table_name (str): File name of the table json file. Ex table1.json
    """
    networkSetup.update_switch_table(switch_name, table_name)


# Links
def link_node_to_node(node1_name, node2_name, node1_port=-1, node2_port=-1):
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

    if not link in networkSetup.links:
        networkSetup.add_link(link)
        for node in networkSetup.nodes:
            if node.name == node1_name:
                node.used_ports.append(node1_port)
            elif node.name == node2_name:
                node.used_ports.append(node2_port)


def link_node_to_switch(node_name, switch_name, node_port=-1, switch_port=-1):
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
        for node in networkSetup.nodes:
            if node.name == node_name:
                node_port = node.generate_port()
    else:
        for node in networkSetup.nodes:
            if node.name == node_name:
                if not node_port in node.used_ports:
                    node.add_port(node_port)
                else:
                    print(f"Failed to add link between {node_name} and {switch_name}")

    # If no port is given, generate port for switch
    if switch_port < 0:
        for switch in networkSetup.switches:
            if switch_name == switch.name:
                switch_port = switch.generate_port()
    else:
        for switch in networkSetup.switches:
            if switch_name == switch.name:
                switch.add_port(switch_port)

    link = Link(
        node_name, switch_name, node_port, switch_port, conn_type="Node_to_Switch"
    )

    if not link in networkSetup.links:
        networkSetup.add_link(link)


def link_switch_to_switch(switch1_name, switch2_name, switch1_port=-1, switch2_port=-1):
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
        for switch in networkSetup.switches:
            if switch1_name == switch.name:
                switch1_port = switch.generate_port()
    else:
        for switch in networkSetup.switches:
            if switch1_name == switch.name:
                switch.add_port(switch1_port)
    if switch2_port < 0:
        for switch in networkSetup.switches:
            if switch2_name == switch.name:
                switch2_port = switch.generate_port()
    else:
        for switch in networkSetup.switches:
            if switch2_name == switch.name:
                switch.add_port(switch2_port)

    link = Link(
        switch1_name,
        switch2_name,
        switch1_port,
        switch2_port,
        conn_type="Switch_to_Switch",
    )

    if not link in networkSetup.links:
        networkSetup.links.append(link)


def add_new_link(device1_name, device2_name, device1_port=-1, device2_port=-1):
    dev1 = None
    dev2 = None

    for dev in networkSetup.nodes + networkSetup.switches:
        if dev.name == device1_name:
            dev1 = dev
        if dev.name == device2_name:
            dev2 = dev

    if not dev1:
        print(
            f"Failed to add link between {device1_name} and {device2_name} --> Device: {device1_name} could not be found in setup"
        )
        return
    if not dev2:
        print(
            f"Failed to add link between {device1_name} and {device2_name} --> Device: {device2_name} could not be found in setup"
        )
        return

    # Check if desired port is used
    if device1_port in dev1.used_ports:
        print(
            f"Failed to add link between {device1_name} and {device2_name} --> Port {device1_port} alread used in {device1_name}"
        )
        return
    if device2_port in dev2.used_ports:
        print(
            f"Failed to add link between {device1_name} and {device2_name} --> Port {device2_port} alread used in {device2_name}"
        )
        return

    if type(dev1) == Node:
        if type(dev2) == Node:
            link_node_to_node(device1_name, device2_name, device1_port, device2_port)
        elif type(dev2) == Switch:
            link_node_to_switch(device1_name, device2_name, device1_port, device2_port)
    elif type(dev1) == Switch:
        if type(dev2) == Node:
            link_node_to_switch(device2_name, device1_name, device2_port, device1_port)
        elif type(dev2) == Switch:
            link_switch_to_switch(
                device1_name, device2_name, device1_port, device2_port
            )


def save_setup_to_json(setup, path):
    """Save the setup to json file. This is the file to be added as input to benchexec

    Args:
        setup (NetworkSetup): The setup which are to be save
        path (str): Path to where to save the file. Ex. /home/setup.json
    """
    data = setup.to_dict()
    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)


def save_table_entries_to_json(path):
    with open(path, "w") as json_file:
        json.dump(table_entries, json_file, indent=4, sort_keys=True)


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


def generate_switch_server_port():
    server_port = 50051
    switch_ports = []

    for switches in networkSetup.switches:
        switch_ports.append(switches.server_port)

    while server_port in switch_ports:
        server_port += 1

    return server_port


def read_base_from_json(path: str):
    """
    Reads setup from a previous network configuration

    Args:
        path: Absolute path to network configuration file
    """

    if not os.path.exists(path):
        print(f"Failed to read {path}. Path not found")
        return

    with open(path) as f:
        data = json.load(f)

    # Add switches withoud table entries
    for switch_name in data["switches"]:
        switch_info = data["switches"][switch_name]
        add_new_switch(
            switch_name, switch_info["p4_prog_name"], switch_info["p4_info_path"]
        )

    # Add nodes
    for node_name in data["nodes"]:
        node_info = data["nodes"][node_name]
        add_new_node(
            node_name,
            node_info["ipv4_addr"],
            node_info["mac_addr"],
            node_info["id"],
        )

    # Add links
    for link in data["links"]:
        add_new_link(
            link["device1"], link["device2"], link["device1_port"], link["device2_port"]
        )

    return


def add_table_entry_to_switch(
    switch_name: str,
    table_name: str,
    action_name: str,
    match_fields: dict,
    action_params: dict,
):

    switch = None
    for sw in networkSetup.switches:
        if switch_name == sw.name:
            switch = sw

    if not switch:
        print(f"Could not find switch {switch_name}")
        return

    switch.add_table_entry(table_name, action_name, match_fields, action_params)


def update_switch_p4_info(switch_name: str, p4_prog_name: str, p4_info_path: str):
    switch = _get_switch(switch_name)

    switch.p4_info_path = p4_info_path
    switch.p4_prog_name = p4_prog_name


def add_table_entry_file_to_switch(switch_name: str, path: str):
    if not os.path.exists(path):
        print(f"Failedto add table entry file. File doest exist")
        return

    with open(path) as f:
        data = json.load(f)

        for table_entry in data:
            add_table_entry_to_switch(
                switch_name,
                table_entry["table_name"],
                table_entry["action_name"],
                table_entry["match_fields"],
                table_entry["action_params"],
            )


def print_setup():
    print(networkSetup)


def check_for_errors():
    return networkSetup.check_for_errors()


# Functions for creating table entry file
def add_table_entry_to_file(
    table_name: str,
    action_name: str,
    match_fields: dict,
    action_params: dict,
    p4_info_path="",
):

    # Create tmp switch if p4 info is given for error check
    if p4_info_path:
        sw_tmp = Switch("", "", p4_info_path)

        sw_tmp.add_table_entry(table_name, action_name, match_fields, action_params)
        table_isvalid = sw_tmp.validate_p4_entries()

        if table_isvalid:
            table_entries.append(
                {
                    "table_name": table_name,
                    "action_name": action_name,
                    "match_fields": match_fields,
                    "action_params": action_params,
                }
            )


# Local functions
def _get_switch(switch_name: str):
    switch = None
    for sw in networkSetup.switches:
        if switch_name == sw.name:
            switch = sw

    return switch


def main():

    # add_new_switch(
    #     "S1",
    #     "simple_switch2",
    #     "/home/p4/installations/bf-sde-9.5.0/build/p4-build/tofino/simple_switch2/tofino/p4info2.pb.txt",
    # )

    # add_table_entry_to_file(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.2.2", 32]},
    #     {"egress_port": 1},
    #     p4_info_path="/home/p4/installations/bf-sde-9.5.0/build/p4-build/tofino/simple_switch2/tofino/p4info2.pb.txt",
    # )

    # save_table_entries_to_json(
    #     "/home/p4/installations/p4_bench_api/src/p4_bench_api/table_entries.json"
    # )

    # read_base_from_json(
    #     "/home/p4/installations/p4_bench_api/src/p4_bench_api/netconf.json"
    # )

    # add_table_entry_file_to_switch(
    #     "S1", "/home/p4/installations/p4_bench_api/src/p4_bench_api/table_entries.json"
    # )

    # update_switch_p4_info(
    #     "S1",
    #     "simple_switch2",
    #     "/home/p4/installations/bf-sde-9.5.0/build/p4-build/tofino/simple_switch2/tofino/p4info2.pb.txt",
    # )

    # s1 = Switch(
    #     f"S1",
    #     p4_prog_name="simple_switch2",
    #     p4_info_path="/home/p4/installations/bf-sde-9.5.0/build/p4-build/tofino/simple_switch2/tofino/p4info2.pb.txt",
    #     server_port=50051,
    # )
    # # S1
    # s1.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.1.1", 32]},
    #     {"egress_port": 1},
    # )

    # s2 = Switch(
    #     f"S2",
    #     p4_prog_name="simple_switch2",
    #     p4_info_path="/home/p4/installations/bf-sde-9.5.0/build/p4-build/tofino/simple_switch2/tofino/p4info2.pb.txt",
    #     server_port=50052,
    # )
    # # S1
    # s2.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.1.1", 32]},
    #     {"egress_port": 1},
    # )

    # add_switch_to_setup(s1)
    # add_switch_to_setup(s2)

    s1 = Switch(
        f"S1",
        p4_prog_name="simple_switch2",
        p4_info_path="/home/p4/installations/bf-sde-9.5.0/build/p4-build/tofino/simple_switch2/tofino/p4info2.pb.txt",
        server_port=50051,
    )

    # s1.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.2.2", 16]},
    #     {"egress_port": 2},
    # )
    # s1.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.3.3", 16]},
    #     {"egress_port": 3},
    # )
    # s1.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.4.4", 16]},
    #     {"egress_port": 3},
    # )

    # S2
    s2 = Switch(
        f"S2",
        p4_prog_name="simple_switch2",
        p4_info_path="/home/p4/installations/bf-sde-9.5.0/build/p4-build/tofino/simple_switch2/tofino/p4info2.pb.txt",
        server_port=50054,
    )
    # s2.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.1.1", 32]},
    #     {"egress_port": 1},
    # )
    # s2.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.2.2", 32]},
    #     {"egress_port": 2},
    # )
    # s2.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.3.3", 32]},
    #     {"egress_port": 3},
    # )
    # s2.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.4.4", 32]},
    #     {"egress_port": 3},
    # )

    # S3
    s3 = Switch(
        f"S3",
        p4_prog_name="simple_switch2",
        p4_info_path="/home/p4/installations/bf-sde-9.5.0/build/p4-build/tofino/simple_switch2/tofino/p4info2.pb.txt",
        server_port=50055,
    )
    # s3.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.1.1", 32]},
    #     {"egress_port": 1},
    # )
    # s3.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.2.2", 32]},
    #     {"egress_port": 1},
    # )
    # s3.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.3.3", 32]},
    #     {"egress_port": 2},
    # )
    # s3.add_table_entry(
    #     "Ingress.ipv4_lpm",
    #     "Ingress.ipv4_forward",
    #     {"hdr.ipv4.dst_addr": ["10.0.4.4", 32]},
    #     {"egress_port": 2},
    # )

    add_switch_to_setup(s1)
    add_switch_to_setup(s2)
    add_switch_to_setup(s3)

    add_new_node("N1", "10.0.1.1")
    add_new_node("N2", "10.0.2.2")
    add_new_node("N3", "10.0.3.3")
    add_new_node("N4", "10.0.4.4")

    add_new_link("N1", "S1", 0, 1)
    add_new_link("N2", "S1", 0, 2)
    add_new_link("N3", "S2", 0, 1)
    add_new_link("N4", "S2", 0, 2)

    add_new_link("S1", "S3", 3, 1)
    add_new_link("S3", "S2", 2, 4)

    # # Nodes
    # nrOfNodes = 4
    # for i in range(nrOfNodes):
    #     add_new_node(f"h{i+1}", f"10.0.{i+1}.{i+1}")

    # add_new_link("h1", "S1", device2_port=1)
    # add_new_link("h2", "S1", device2_port=2)
    # add_new_link("h3", "S2", device2_port=1)
    # add_new_link("h4", "S2", device2_port=2)

    # add_new_link("S1", "S3", 3, 1)
    # add_new_link("S3", "S2", 2, 4)

    # # # Links Node <--> Switch
    # # l1 = Link(h1, s1, 0, 1)
    # # l2 = Link(h2, s1, 0, 2)
    # # l3 = Link(h3, s2, 0, 1)
    # # l4 = Link(h4, s2, 0, 2)

    # # # Links Switch <--> Switch
    # # l5 = Link(s1, s3, 3, 1)
    # # l6 = Link(s3, s2, 2, 4)

    # # setup.add_link(l1)
    # # setup.add_link(l2)
    # # setup.add_link(l3)
    # # setup.add_link(l4)
    # # setup.add_link(l5)
    # # setup.add_link(l6)

    setup_has_error = networkSetup.check_for_errors()
    from pathlib import Path

    path = Path(__file__)
    f_path = str(path.parent.absolute())

    if not setup_has_error:
        # save_setup_to_json(networkSetup, f"{f_path}/netconf.json")
        # save_setup_to_json(
        #     networkSetup,
        #     "/home/p4/bf_benchexec/benchexec/contrib/p4_files/docker_files/ptf_tester/tests/network_configs/2_nodes_1_switch.json",
        # )

        # # save_setup_to_json(setup, "/home/p4/p4_bench_api/testing/test2.json")
        # save_setup_to_json(
        #     networkSetup,
        #     "/home/p4/installations/p4_bench_api/src/p4_bench_api/netconf.json",
        # )
        print_setup()


if __name__ == "__main__":
    main()
