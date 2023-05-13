## Readme

This is a configuration file written in YAML format for the netplan network configuration tool. It defines the network interfaces and VLANs on a system. Here's a breakdown of the configuration:

The version of the network configuration format is set to 2.

Under the "ethernets" section, three Ethernet interfaces are defined: eth1, eth2, and eth3.
     For each interface, DHCPv4 is enabled (dhcp4: true) and DHCPv6 is disabled (dhcp6: false).
     The "optional" flag is set to true, indicating that these interfaces are optional.
    The "nameservers" section specifies the DNS server IP address for each interface. Replace "<DNS_server_IP>" with the actual IP address.

Under the "vlans" section, three VLANs are defined: vlan10, vlan20, and vlan30.
    For each VLAN, an ID is assigned (10, 20, and 30 respectively) and associated with an Ethernet interface (eth1, eth2, and eth3 respectively).

    
To use this configuration, replace "<DNS_server_IP>" with the actual IP address of your DNS server. Adjust the VLAN IDs and links (ethernet interfaces) according to your network configuration. Then, save the file and apply the changes by running the appropriate netplan command, such as "sudo netplan apply".