class Node(object):
    def __init__(self, name, ipv4_addr="", node_id=0):
        self.name = name
        self.iface = ""
        self.ipv4_addr = ipv4_addr
        self.used_ports = []
        self.id = node_id

    def __eq__(self, other):
        if isinstance(other, Node):
            if self.name == other.name or self.id == other.id:
                return True
        return False

    def add_ipv4_addres(self, addr):
        self.ipv4_addr = addr

    def add_port(self, port_nr):
        if not port_nr in self.used_ports:
            self.used_ports.append(port_nr)

    def generate_port(self):
        for i in range(len(self.used_ports) + 1):
            if not i in self.used_ports:
                self.used_ports.append(i)
                return i


class Switch(object):
    def __init__(self, name, p4_file_name):
        self.name = name
        self.iface = ""
        self.table_entries = []
        self.used_ports = []
        self.p4_file_name = p4_file_name

    def __eq__(self, other):
        if isinstance(other, Switch):
            if self.name == other.name:
                return True
        return False

    def update_table(self, table_name):
        if not table_name in self.table_entries:
            self.table_entries.append(table_name)

    def add_port(self, port_nr):
        if not port_nr in self.used_ports:
            self.used_ports.append(port_nr)

    def generate_port(self):
        for i in range(len(self.used_ports) + 1):
            if not i in self.used_ports:
                self.used_ports.append(i)
                return i


class Link(object):
    def __init__(self, device1, device2, device1_port, device2_port, conn_type=""):
        self.device1 = device1
        self.device2 = device2
        self.device1_port = device1_port
        self.device2_port = device2_port
        self.conn_type = conn_type

    def is_valid(self):
        return (
            isinstance(self.device1, str)
            and isinstance(self.device2, str)
            and isinstance(self.device1_port, int)
            and isinstance(self.device2_port, int)
            and self.conn_type in ["Node_to_Switch", "Node_to_Node", "Switch_to_Switch"]
        )


class NetworkSetup(object):
    def __init__(self):
        self.nodes = []
        self.switches = []
        self.links = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_link(self, link):
        self.links.append(link)

    def add_switch(self, switch):
        self.switches.append(switch)

    def update_switch_table(self, switch_name, table_name):
        for switch in self.switches:
            if switch_name == switch.name:
                switch.update_table(table_name)

    def to_dict(self):
        setup_dict = {}

        # Add nodes
        setup_dict["nodes"] = {}
        for node in self.nodes:
            setup_dict["nodes"][node.name] = {
                "ipv4_addr": node.ipv4_addr,
                "used_ports": node.used_ports,
                "id": node.id,
            }

        setup_dict["switches"] = {}
        for switch in self.switches:
            setup_dict["switches"][switch.name] = {
                "table_entries": switch.table_entries,
                "used_ports": switch.used_ports,
                "p4_file_name": switch.p4_file_name,
            }

        setup_dict["links"] = []

        for link in self.links:
            setup_dict["links"].append(
                {
                    "device1": link.device1,
                    "device2": link.device2,
                    "device1_port": link.device1_port,
                    "device2_port": link.device2_port,
                    "type": link.conn_type,
                }
            )

        return setup_dict

    def check_for_errors(self):
        for node in self.nodes:
            nr_of_occ = len([x for x in self.nodes if x == node])
            if nr_of_occ != 1:
                print(f"Node {node.name} is defined multiple times")

            if len(node.used_ports) == 0:
                print(f"Node {node.name} is not connected to the network")

        for switch in self.switches:
            nr_of_occ = len([x for x in self.switches if x == switch])
            if nr_of_occ != 1:
                print(f"Switch {switch.name} is defined multiple times")
            if len(switch.used_ports) == 0:
                print(f"Switch {switch.name} is not connected to the network")

        for link in self.links:
            if not link.is_valid():
                print(f"Link between {link.device1} and {link.device2} is not valid")

    print("Check completed")


# simple testing


def main():

    setup = NetworkSetup()

    nodes = []

    nodes.append(Node("Node1", node_id=0))
    nodes.append(Node("Node2", node_id=1))
    nodes.append(Node("Node3", node_id=2))

    switches = []

    switches.append(Switch("Switch1"))
    switches.append(Switch("Switch2"))
    switches.append(Switch("Switch3"))

    links = []
    links.append(Link("Node1", "Switch1", 0, 0, conn_type="Node_to_Switch"))
    links.append(Link("Node1", "Switch1", 0, 0))
    links.append(Link("Node1", "Switch1", 0, 0))

    for node in nodes:
        setup.add_node(node)

    for switch in switches:
        setup.add_switch(switch)

    for link in links:
        setup.add_link(link)

    setup.check_for_errors()


if __name__ == "__main__":
    main()