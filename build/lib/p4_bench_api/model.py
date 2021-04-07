class Node(object):
    def __init__(self, name, ipv4_addr=""):
        self.name = name
        self.iface = ""
        self.ipv4_addr = ipv4_addr
        self.used_ports = []

    def __eq__(self, other):
        if isinstance(other, Node):
            if self.name == other.name:
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
    def __init__(self, name):
        self.name = name
        self.iface = ""
        self.table_entries = []
        self.used_ports = []

    def __eq__(self, other):
        if isinstance(other, Node):
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

        #Add nodes
        setup_dict["nodes"] = {}
        for node in self.nodes:
            setup_dict["nodes"][node.name] = {"ipv4_addr": node.ipv4_addr, "used_ports": node.used_ports}

        setup_dict["switches"] = {}
        for switch in self.switches:
            setup_dict["switches"][switch.name] = {"table_entries": switch.table_entries, "used_ports": switch.used_ports}
        
        setup_dict["links"] = []

        for link in self.links:
            setup_dict["links"].append({
                "device1": link.device1,
                "device2": link.device2,
                "device1_port": link.device1_port,
                "device2_port": link.device2_port,
                "type": link.conn_type})

        return setup_dict


#simple testing

def main():
    node1 = Node("node1")
    node2 = Node("node2")
    node1_cp = Node("node1")

    node_list = []

    node_list.append(node1)
    node_list.append(node2)

    if node1_cp in node_list:
        print("good")

    switch1 = Switch("switch1")

    print(node1 == node2)
    print(node1 == node1_cp)
    print(node1 == switch1)


if __name__=="__main__":
    main()