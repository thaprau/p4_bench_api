# Python API packet for creating network config file for p4 benchexec

## Installation
```
git clone https://github.com/thaprau/p4_bench_api.git
cd p4_bench_api
pip3 install .
```

## Usage/Workflow

The best way to use the api is by creating a setup script. The script should include the 
creation of a networkbuilder, which handles all the setup.

### Basic configuration
Using the builder, there are 2 options for creating a setup.
1. Using an old setup file(see example file "")
2. Manually creating your own setup(see example file "")

1. When using an old setup, load the base setup with ```read_base_from_json(path_to_old_config)```. The 
builder will load the setup and you will be able to reference all devices by name.

2. When creating a new base setup, take advantage of 3 basic commands, ```add_new_node(), add_new_switch() and add_new_link()```.
  * add_new_node() - Creates a new node in the setup
  * add_new_switch() - Creates a new switch in the setup
  * add_new_link() - Creates a link/ethernet connection between 2 created devices

To display current devices and links in the setup, NetworkBuilder as a print_setup command, which 
will display all current links, nodes and switches. This is especially useful when loading a previous config file.

### Advance configuration - table entries
P4 switches all require table entries to define package flow of the device. To add table entries for the configartion file 
there are 2 alternatives:
1. add_table_entry_to_switch() - Enter table entry information directly
2. add_table_entry_file_to_switch() - Load table entry from file

If, for a switch, a p4 info file is defined, p4_bench_api can help with the creation of table_entries. To do so, run the command
with empty parameters(e.g. add_table_entry_to_switch("Switch_name", "", "", "", "")). When running the check_command, the api will print hints
on how to fix your table entry.

### Check for errors/save the file

The final step is to run check_for_errors() and save_setu_to_json(). The first one will check for any errors in the setup and give hints on how to 
fix them. The last one saves the configuration to a file to be fed into benchexec.

## Example

This is a example program showcasing how to create a simple 2 nodes 1 switch setup.

```
from p4_bench_api.builder import NetworkBuilder

# Create builder
net_builder = NetworkBuilder()

# Add 2 nodes
net_builder.add_new_node("Node1", "10.0.1.1")
net_builder.add_new_node("Node2", "10.0.2.2")

# Add switch
net_builder.add_new_switch("Switch1", "name_of_p4_program", "path_to_p4info")

# Link them together
net_builder.add_new_link("Node1", "Switch1", 0, 1)  # Node1's port0 to Switch1's port1
net_builder.add_new_link("Node2", "Switch1", 0, 1)  # Node2's port0 to Switch1's port2

net_builder.check_for_errors()
net_builder.save_setup_to_json("config.json")
```

