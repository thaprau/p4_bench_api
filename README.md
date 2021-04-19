# Python API packet for creating network config file for p4 benchexec

## Installation
```
git clone https://github.com/thaprau/p4_bench_api.git
cd p4_bench_api
pip3 install .
```

## Usage

To use the api, start py importing the package. Then create and instace of the NetworSetup.
Then the wanted devices tp the setup with add_new_node and add_new_switch. Link the setup
together by creating links. Depending on what you are connecting, choose between
link_node_to_switch, link_switch_to_switch or link_node_to_node. Finally, run setup.check_for_errors()
to traverse the setup and look for error. Then save the setup to a json file.

## Example

```
#Create empty setup
setup = NetworkSetup()

#Add some nodes
add_new_node(setup, "Node1", "192.168.1.1")
add_new_node(setup, "Node2", "192.168.1.2")
add_new_node(setup, "Node3", "192.168.1.3")
add_new_node(setup, "Node4", "192.168.1.4")

#Add some switches
add_new_switch(setup, "Switch1")
add_new_switch(setup, "Switch2")

#Creates links between Nodes and Switches
link_node_to_switch(setup, "Node1", "Switch1")
link_node_to_switch(setup, "Node2", "Switch1")
link_node_to_switch(setup, "Node3", "Switch2")
link_node_to_switch(setup, "Node4", "Switch2")

link_switch_to_switch(setup, "Switch1", "Switch2", 100, 100)

setup.check_for_errors()

save_to_json("/path/to/file.json")
```

