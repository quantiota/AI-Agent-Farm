## Readme


The provided network configuration is defining three Ethernet interfaces (eth1, eth2, eth3) with static IP addresses and disabled DHCP. Each interface is marked as optional, indicating that they are not required for the network to function.

The addresses field for each interface specifies the IP address and subnet mask. The gateway4 field denotes the IP address of the gateway associated with each interface.

The nameservers field under each interface specifies the IP address of the DNS server to be used.

Additionally, there are three VLANs (vlan10, vlan20, vlan30) defined. Each VLAN is associated with a specific Ethernet interface (eth1, eth2, eth3) using the link field and identified by its VLAN ID (10, 20, 30).

Overall, this configuration allows for the setup of multiple interfaces with static IP addresses, each associated with a specific VLAN and gateway, and with DNS server settings specified.