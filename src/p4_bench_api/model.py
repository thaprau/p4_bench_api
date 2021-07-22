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
    def __init__(self, name, p4_prog_name="", p4_info_path="", server_port=-1):
        self.name = name
        self.iface = ""
        self.p4_prog_name = p4_prog_name
        self.p4_info_path = p4_info_path
        self.server_port = server_port
        self.table_entries = []
        self.used_ports = []

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

    def add_table_entry(self, table_name, action_name, match_fields, action_params):
        self.table_entries.append(
            {
                "table_name": table_name,
                "action_name": action_name,
                "match_fields": match_fields,
                "action_params": action_params,
            }
        )


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
                "p4_prog_name": switch.p4_prog_name,
                "server_port": switch.server_port,
                "p4_info_path": switch.p4_info_path,
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
        setup_invalid = False

        for node in self.nodes:
            nr_of_occ = len([x for x in self.nodes if x == node])
            if nr_of_occ != 1:
                print(f"Node {node.name} is defined multiple times")
                setup_invalid = True

            if len(node.used_ports) == 0:
                print(f"Node {node.name} is not connected to the network")
                setup_invalid = True

        p4_isvalid = self.validate_p4_entries()

        if not p4_isvalid:
            setup_invalid = True

        for switch in self.switches:
            nr_of_occ = len([x for x in self.switches if x == switch])
            if nr_of_occ != 1:
                print(f"Switch {switch.name} is defined multiple times")
                setup_invalid = True
            if len(switch.used_ports) == 0:
                print(f"Switch {switch.name} is not connected to the network")
                setup_invalid = True

        for link in self.links:
            if not link.is_valid():
                print(f"Link between {link.device1} and {link.device2} is not valid")
                setup_invalid = True

        return setup_invalid

    def validate_p4_entries(self):
        from p4_helper import P4InfoHelper
        import logging

        # Go through table entries and provide feedback
        for switch in self.switches:
            if switch.p4_info_path:
                helper = P4InfoHelper(switch.p4_info_path)

                for table_entry in switch.table_entries:

                    table_entry_isvalid = True

                    table_name = table_entry["table_name"]
                    action_name = table_entry["action_name"]
                    match_fields = table_entry["match_fields"]
                    action_params = table_entry["action_params"]

                    # Get values in simple form
                    tables = helper.getAllTables()
                    actions = helper.getAllActions()

                    if type(table_name) != str:
                        print(f"Table name should be a string")
                        print_table_entry_info(switch.name, table_entry)
                        return False

                    # Check if table exist with same name/alias
                    table_for_check = None
                    for table in tables:
                        if table.name == table_name or table.alias == table.name:
                            table_for_check = table
                            break

                    if not table_for_check:
                        if not table_name:
                            table_name = "None"

                        print(
                            f"Error in table entry. Table with name {table_name} could not be found in p4 info file"
                        )
                        print_table_names(tables)
                        print_table_entry_info(switch.name, table_entry)
                        return False

                    # Check match_field
                    mf_to_check = table_for_check.match_fields

                    if not isinstance(match_fields, dict):
                        print(
                            f"Error switch: {switch.name}. Match_fields should be a dict."
                        )
                        table_entry_isvalid = False

                    else:
                        key_list = list(match_fields.keys())
                        if len(key_list) == 0:
                            logging.error(f"Match_field has no keys")
                            print_match_field_keys(mf_to_check)
                            table_entry_isvalid = False
                        else:
                            key = key_list[0]

                            if key != mf_to_check.name:
                                print(f"Incorrect match name: {key} in p4 file")
                                table_entry_isvalid = False

                            # Check match type
                            match_type = mf_to_check.match_type
                            match_fields_correct = True

                            # Exact match
                            if match_type == 2:
                                logging.info("Not implemented")
                            # LPM match
                            elif match_type == 3:
                                value = match_fields[key]
                                if not type(value) == list:
                                    print(
                                        f"Error match fields. Expected type list as input for match field value. Got {type(value)}"
                                    )
                                    match_fields_correct = False
                                else:
                                    if not isinstance(value[1], int):
                                        print(
                                            f"Error match fields. Second value should be an integer for LPM match"
                                        )
                                        match_fields_correct = False
                                if len(value) != 2:
                                    print(
                                        f"Error match fields. Expected list of length 2 as input. Got {value}"
                                    )
                                    match_fields_correct = False

                            # Ternary match
                            elif match_type == 4:
                                pass
                            if not match_fields_correct:
                                table_entry_isvalid = False

                    # Check action
                    if type(action_name) != str:
                        print("Action name should be a string")
                        print_table_entry_info(switch.name, table_entry)
                        print_avaialble_actions(table.action_refs, actions)
                        table_entry_isvalid = False

                    action_for_check = None
                    for act in actions:
                        if act.name == action_name or act.alias == action_name:
                            action_for_check = act
                            break

                    if not action_for_check:
                        logging.error(
                            f"Action with name {action_name} could not be found in p4 file"
                        )

                        print_avaialble_actions(table.action_refs, actions)

                        table_entry_isvalid = False
                    else:
                        # Check if required parameters are given
                        if action_for_check.params:
                            if type(action_params) != dict:
                                print(
                                    'Error action params. Should be a dict on format "parametername":"parameter value" '
                                )
                                print_action_params_info(action_for_check.params)
                                table_entry_isvalid = False

                            else:
                                key = list(action_params.keys())[0]
                                val = list(action_params.values())[0]

                                if not action_params:
                                    print(f"Action parameter was not given")
                                    print_action_params_info(action_for_check.params)
                                    table_entry_isvalid = False
                                if not key == action_for_check.params.name:
                                    print(f"Action key did not match key in P4 file")
                                    print_action_params_info(action_for_check.params)

                                if action_for_check.params.bitwidth:
                                    max_val = 2 ^ action_for_check.params.bitwidth
                                    if val >= max_val:
                                        print(f"Action param is to big")
                                        table_entry_isvalid = False

                        else:
                            if action_params:
                                print(
                                    f"{action_name} does not take input parameters. {action_params} was given"
                                )
                                table_entry_isvalid = False

                    if not table_entry_isvalid:
                        print("Error in table entry. Check above on how to fix them")
                        print_table_entry_info(switch.name, table_entry)
                        return False

        return True


def print_table_entry_info(switch_name, table_entry):
    print("########## Table entry information #########")
    table_name = table_entry["table_name"]
    action_name = table_entry["action_name"]
    match_fields = table_entry["match_fields"]
    action_params = table_entry["action_params"]

    print("Table entry information")
    print(f"Switch: {switch_name}")

    print(
        f"Table name: {table_name} \n"
        + f"Action Name: {action_name} \n"
        + f"Match_fields: {match_fields} \n"
        + f"Action Params: {action_params}"
    )

    print("########## End of table entry ##########")


# Helper functions
def print_table_names(tables):
    ret_string = "Avaialble table names:"

    for tab in tables:
        ret_string += f"\n* {tab.name}"

    print(ret_string)


def print_match_field_keys(match_field):
    print(f"Avaialable match keys \n {match_field.name}")


def print_avaialble_actions(action_refs, actions):
    print("Avaialble actions for table")
    for act in actions:
        if act.id in action_refs:
            print(act.name)


def print_action_params_info(action_params):
    print("##### Action params info #####")

    print(f"Name: {action_params.name}")
    print(f"Id: {action_params.id}")
    try:
        print(f"Bitwidth: {action_params.bitwidth}")
    except:
        pass
    print("##### Action params info #####")


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
