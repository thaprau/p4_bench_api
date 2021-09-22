from re import L
from .model import Node, Switch, Link, NetworkSetup
import json
import os
from inspect import getframeinfo, stack


STANDARD_IP_DOMAIN = "192.168"


class NetworkBuilder(object):
    """
    Class for creating network configuration for P4 benchexec. Holds all available functions.
    """

    def __init__(self):
        self.network_setup = NetworkSetup()
        self.table_entries = []
        self.ip_addresses = []
        self.node_ids = []

    def add_new_node(self, name: str, ipv4_addr="", mac_addr="", node_id=""):
        """
        Adds a new node to the setup with given parameters.

        Args:
            setup (NetworkSetup): The setup to add the node to
            name (str): Name of the node. Should be unique.
            ipv4_addr (str, optional): [ipv4-address of the node.]. Defaults to "".
            mac_addr (str, optional): [mac address of the node]. Defaults to "".
        """
        if node_id == "":
            node_id = self.__generate_node_id()

        node = Node(name, ipv4_addr=ipv4_addr, mac_addr=mac_addr)
        node.id = node_id

        self.node_ids.append(node_id)

        if not node in self.network_setup.nodes:
            self.network_setup.add_node(node)
        else:
            self.__debug_info("Node with same id or name already exits")

    def add_new_switch(
        self, name: str, p4_file_name: str, p4_info_path="", server_port=-1
    ):
        """
        Adds new switch to the setup

        Args:
            name (str): Name of the switch. Should be unique.
            p4_file_name (str): Name of the p4 program to be executed on the switch
            p4_info_path (str, optional): Path to p4 info file. Required for p4 entry error check. Defaults to "".
            server_port (int, optional): Grpc connection port of the switch. -1 generates a port automatically.
        """
        if server_port < 0:
            server_port = self.__generate_switch_server_port()

        if p4_info_path and not os.path.exists(p4_info_path):
            self.__debug_info(f"Could not find p4 info file: {p4_info_path}")
            return

        switch = Switch(name, p4_file_name, p4_info_path, server_port)

        if not switch in self.network_setup.switches:
            self.network_setup.add_switch(switch)
        else:
            self.__debug_info("Switch with same id or name already exits")

    def add_table_entry_from_file(self, switch_name: str, path: str):
        """Add a table definition to a switch

        Args:
            switch_name (str): Name of the switch
            path (str): Path to the table entry file
        """
        self.network_setup.update_switch_table(switch_name, path)

    def add_new_link(
        self, device1_name, device2_name, device1_port=-1, device2_port=-1
    ):
        """
        Add new link to the setup between given given devices. If no ports are given, they are
        set automatically to an available port.
        """
        dev1 = None
        dev2 = None

        dev1 = self.__get_device(device1_name)
        dev2 = self.__get_device(device2_name)

        if not dev1:
            self.__debug_info(
                f"Failed to add link between {device1_name} and {device2_name} --> Device: {device1_name} could not be found in setup"
            )
            return
        if not dev2:
            self.__debug_info(
                f"Failed to add link between {device1_name} and {device2_name} --> Device: {device2_name} could not be found in setup"
            )
            return

        # Check if desired port is used
        if device1_port in dev1.used_ports:
            self.__debug_info(
                f"Failed to add link between {device1_name} and {device2_name} --> Port {device1_port} alread used in {device1_name}"
            )
            return
        if device2_port in dev2.used_ports:
            self.__debug_info(
                f"Failed to add link between {device1_name} and {device2_name} --> Port {device2_port} alread used in {device2_name}"
            )
            return

        self.__add_link_to_setup(dev1, dev2, device1_port, device2_port)

    def add_switch_to_setup(self, switch: Switch):
        """
        Adds a switch object to the setup. For the majority of cases, use add_new_switch instead

        Args:
            switch (Switch): Switch to add
        """
        switch_is_unique = True
        for sw in self.network_setup.switches:
            if switch.name == sw.name:
                self.__debug_info(f"Switch with name {switch.name} already exits")
                switch_is_unique = False
            if switch.server_port == sw.server_port:
                self.__debug_info(
                    f"Swtich {switch.name} invalid server port. Port already used by Switch {sw.name}"
                )
                switch_is_unique = False

        if switch_is_unique:
            self.network_setup.add_switch(switch)
        else:
            self.__debug_info(f"Not adding Switch {switch.name} to setup")

    def add_node_to_setup(self, node: Node):
        """
        Add node to the seutp. In the majority of cases, use add_new_node instead.

        Args:
            node (Node): Node to add
        """
        node_is_unique = True
        for n in self.network_setup.nodes:
            if n == node:
                self.__debug_info(f"Node {node.name} already exits")
                node_is_unique = False

        if node_is_unique:
            self.network_setup.add_node(node)
        else:
            self.__debug_info(f"Not adding Node {node.name} to setup")

    def save_setup_to_json(self, path: str):
        """Save the setup to json file. This is the file to be added as input to benchexec

        Args:
            path (str): Path to where to save the file. Ex. /home/setup.json
        """
        data = self.network_setup.to_dict()
        with open(path, "w") as json_file:
            json.dump(data, json_file, indent=4, sort_keys=True)

    def save_table_entries_to_json(self, path: str):
        """
        Dumps all the table_entries to a file to be used later

        Args:
            path (str): Path to file
        """
        with open(path, "w") as json_file:
            json.dump(self.table_entries, json_file, indent=4, sort_keys=True)

    def read_base_from_json(self, path: str):
        """
        Reads base setup from configuration file. Includes Nodes, Switches and Links.

        Args:
            path: Absolute path to network configuration file
        """

        if not os.path.exists(path):
            self.__debug_info(f"Failed to read {path}. Path not found")
            return

        with open(path) as f:
            data = json.load(f)

        # Add switches withoud table entries
        for switch_name in data["switches"]:
            switch_info = data["switches"][switch_name]
            self.add_new_switch(
                switch_name, switch_info["p4_prog_name"], switch_info["p4_info_path"]
            )

        # Add nodes
        for node_name in data["nodes"]:
            node_info = data["nodes"][node_name]
            self.add_new_node(
                node_name,
                node_info["ipv4_addr"],
                node_info["mac_addr"],
                node_info["id"],
            )

        # Add links
        for link in data["links"]:
            self.add_new_link(
                link["device1"],
                link["device2"],
                link["device1_port"],
                link["device2_port"],
            )

        return

    def add_table_entry_to_switch(
        self,
        switch_name: str,
        table_name: str,
        action_name: str,
        match_fields: dict,
        action_params: dict,
    ):
        """
        Adds table entry to switch with the given name. Run check_for_errors to check if the
        given input is valid.
        """

        switch = None
        for sw in self.network_setup.switches:
            if switch_name == sw.name:
                switch = sw

        if not switch:
            self.__debug_info(f"Could not find switch {switch_name}")
            return

        switch.add_table_entry(table_name, action_name, match_fields, action_params)

    def update_switch_p4_info(
        self, switch_name: str, p4_prog_name: str, p4_info_path: str
    ):
        """
        Updates the p4 info file and/or the p4 program name of a switch.

        Args:
            switch_name (str): Name of the switch
            p4_prog_name (str): Name of the p4 program
            p4_info_path (str): Path to p4 info file
        """
        switch = self.__get_device(switch_name)

        switch.p4_info_path = p4_info_path
        switch.p4_prog_name = p4_prog_name

    def add_table_entry_file_to_switch(self, switch_name: str, path: str):
        """
        Adds a table entry defined in a file.
        """
        if not os.path.exists(path):
            print(f"Failed to add table entry file. File doest exist")
            return

        with open(path) as f:
            data = json.load(f)

            for table_entry in data:
                self.add_table_entry_to_switch(
                    switch_name,
                    table_entry["table_name"],
                    table_entry["action_name"],
                    table_entry["match_fields"],
                    table_entry["action_params"],
                )

    def print_setup(self):
        """
        Makes a human readable print to see what devices are defined in the setup and
        how they are connected
        """
        print(self.network_setup)

    def check_for_errors(self) -> bool:
        """
        Goes through all given input and check if its correct. Will give hints on how
        to fix any eventual errors

        Returns:
            [bool]: True if setup has errors
        """
        print("######## Checking for errors #######")
        return self.network_setup.check_for_errors()

    # Private functions
    def __get_device(self, device_name):
        for dev in self.network_setup.nodes + self.network_setup.switches:
            if dev.name == device_name:
                return dev
        return None

    def __add_link_to_setup(self, dev1, dev2, device1_port, device2_port):
        if type(dev1) == Node:
            if type(dev2) == Node:
                self.__link_node_to_node(
                    dev1.name, dev2.name, device1_port, device2_port
                )
            elif type(dev2) == Switch:
                self.__link_node_to_switch(
                    dev1.name, dev2.name, device1_port, device2_port
                )
        elif type(dev1) == Switch:
            if type(dev2) == Node:
                self.__link_node_to_switch(
                    dev2.name, dev1.name, device2_port, device1_port
                )
            elif type(dev2) == Switch:
                self.__link_switch_to_switch(
                    dev1.name, dev2.name, device1_port, device2_port
                )

    def __link_node_to_node(self, node1_name, node2_name, node1_port=-1, node2_port=-1):
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

        if not link in self.network_setup.links:
            self.network_setup.add_link(link)
            for node in self.network_setup.nodes:
                if node.name == node1_name:
                    node.used_ports.append(node1_port)
                elif node.name == node2_name:
                    node.used_ports.append(node2_port)

    def __link_node_to_switch(
        self, node_name, switch_name, node_port=-1, switch_port=-1
    ):
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
            for node in self.network_setup.nodes:
                if node.name == node_name:
                    node_port = node.generate_port()
        else:
            for node in self.network_setup.nodes:
                if node.name == node_name:
                    if not node_port in node.used_ports:
                        node.add_port(node_port)
                    else:
                        print(
                            f"Failed to add link between {node_name} and {switch_name}"
                        )

        # If no port is given, generate port for switch
        if switch_port < 0:
            for switch in self.network_setup.switches:
                if switch_name == switch.name:
                    switch_port = switch.generate_port()
        else:
            for switch in self.network_setup.switches:
                if switch_name == switch.name:
                    switch.add_port(switch_port)

        link = Link(
            node_name, switch_name, node_port, switch_port, conn_type="Node_to_Switch"
        )

        if not link in self.network_setup.links:
            self.network_setup.add_link(link)

    def __link_switch_to_switch(
        self, switch1_name, switch2_name, switch1_port=-1, switch2_port=-1
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
            for switch in self.network_setup.switches:
                if switch1_name == switch.name:
                    switch1_port = switch.generate_port()
        else:
            for switch in self.network_setup.switches:
                if switch1_name == switch.name:
                    switch.add_port(switch1_port)
        if switch2_port < 0:
            for switch in self.network_setup.switches:
                if switch2_name == switch.name:
                    switch2_port = switch.generate_port()
        else:
            for switch in self.network_setup.switches:
                if switch2_name == switch.name:
                    switch.add_port(switch2_port)

        link = Link(
            switch1_name,
            switch2_name,
            switch1_port,
            switch2_port,
            conn_type="Switch_to_Switch",
        )

        if not link in self.network_setup.links:
            self.network_setup.links.append(link)

    def __generate_fresh_ip(self, domain_name=""):
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
            if len(self.ip_addresses) == 0:
                addres_array_int.append(172)
                addres_array_int.append(168)
                addres_array_int.append(1)
                addres_array_int.append(1)
            else:
                for i in self.ip_addresses[-1]:
                    addres_array_int.append(i)
        else:
            while len(addres_array_int) < 4:
                addres_array_int.append(1)

        # Check if ip address exits
        while addres_array_int in self.ip_addresses:
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

        self.ip_addresses.append(addres_array_int)

        return addres_array_int

    def __generate_fresh_mac(self, setup):
        # TODO
        nr_of_devices = len(setup.nodes) + len(setup.switches)

        return

    def __generate_node_id(self):
        id = 0
        while id in self.node_ids:
            id += 1

        return id

    def __generate_switch_server_port(self):
        server_port = 50051
        switch_ports = []

        for switches in self.network_setup.switches:
            switch_ports.append(switches.server_port)

        while server_port in switch_ports:
            server_port += 1

        return server_port

    def __debug_info(self, message):
        caller = getframeinfo(stack()[2][0])
        print(
            "%s:%d - %s" % (caller.filename, caller.lineno, message)
        )  # python3 syntax print

    # Functions for creating table entry file
    def add_table_entry_to_file(
        self,
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
                self.table_entries.append(
                    {
                        "table_name": table_name,
                        "action_name": action_name,
                        "match_fields": match_fields,
                        "action_params": action_params,
                    }
                )


def main():

    builder = NetworkBuilder()

    builder.add_new_node("N1", "10.0.1.1")
    builder.add_new_node("N2", "10.0.2.2")
    builder.add_new_node("N3", "10.0.3.3")
    builder.add_new_node("N4", "10.0.4.4")

    builder.add_new_node("N5", "10.0.1.1")
    builder.add_new_node("N6", "10.0.2.2")
    builder.add_new_node("N7", "10.0.3.3")
    builder.add_new_node("N8", "10.0.4.4")

    builder.add_new_switch("S4", "test")
    builder.add_new_switch("S5", "test")
    builder.add_new_switch("S6", "test")

    builder.add_new_link("S4", "S5")
    builder.add_new_link("S5", "S6")
    builder.add_new_link("N5", "S6")
    builder.add_new_link("N6", "S6")
    builder.add_new_link("N7", "S6")
    builder.add_new_link("N8", "S6")

    builder.add_new_switch(
        "S1",
        "simple_switch2",
        "/home/p4/installations/bf-sde-9.5.0/build/p4-build/tofino/simple_switch2/tofino/p4info2.pb.txt",
    )
    builder.add_new_switch(
        "S2",
        "simple_switch2",
        "/home/p4/installations/bf-sde-9.5.0/build/p4-build/tofino/simple_switch2/tofino/p4info2.pb.txt",
    )
    builder.add_new_switch(
        "S3",
        "simple_switch2",
        "/home/p4/installations/bf-sde-9.5.0/build/p4-build/tofino/simple_switch2/tofino/p4info2.pb.txt",
    )

    builder.add_new_link("S3", "S4")
    builder.add_new_link("N1", "S1", 0, 1)
    builder.add_new_link("N2", "S1", 0, 2)
    builder.add_new_link("N3", "S2", 0, 1)
    builder.add_new_link("N4", "S2", 0, 2)
    builder.add_new_link("S1", "S3", 3, 1)
    builder.add_new_link("S3", "S2", 2, 3)

    builder.print_setup()

    builder.add_table_entry_to_switch(
        "S1",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.1.1", 32]},
        {"egress_port": 1},
    )

    builder.add_table_entry_to_switch(
        "S1",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.2.2", 32]},
        {"egress_port": 2},
    )

    builder.add_table_entry_to_switch(
        "S1",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.3.3", 32]},
        {"egress_port": 3},
    )

    builder.add_table_entry_to_switch(
        "S1",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.4.4", 32]},
        {"egress_port": 4},
    )

    builder.add_table_entry_to_switch(
        "S2",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.1.1", 32]},
        {"egress_port": 3},
    )

    builder.add_table_entry_to_switch(
        "S2",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.2.2", 32]},
        {"egress_port": 3},
    )

    builder.add_table_entry_to_switch(
        "S2",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.3.3", 32]},
        {"egress_port": 1},
    )

    builder.add_table_entry_to_switch(
        "S2",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.4.4", 32]},
        {"egress_port": 2},
    )

    builder.add_table_entry_to_switch(
        "S3",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.1.1", 32]},
        {"egress_port": 1},
    )

    builder.add_table_entry_to_switch(
        "S3",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.2.2", 32]},
        {"egress_port": 1},
    )

    builder.add_table_entry_to_switch(
        "S3",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.3.3", 32]},
        {"egress_port": 2},
    )

    builder.add_table_entry_to_switch(
        "S3",
        "Ingress.ipv4_lpm",
        "Ingress.ipv4_forward",
        {"hdr.ipv4.dst_addr": [f"10.0.4.4", 32]},
        {"egress_port": 2},
    )

    builder.check_for_errors()
    builder.save_setup_to_json("/home/p4/Drawing_Test/4_nodes_3_switch.json")


if __name__ == "__main__":
    main()
