#!/usr/bin/env python3
"""farm-discover.py — discover farm nodes on the LAN: IP, hostname, and iLO name.

Runs on the GPU server (or any box on the same LAN). Stdlib only — needs just
`python3` and the system `ping`. No nmap / arp-scan / jq required.

What it does:
  1. Ping-sweeps the subnet (auto-detected, or pass a CIDR).
  2. Reverse-DNS resolves each responder's hostname.
  3. Probes each host's Redfish endpoint (https://IP/redfish/v1/) to detect an
     HP iLO (Gen8 = iLO 4), then reads the iLO name + server serial/model.

Usage:
  python3 farm-discover.py                       # auto-detect /24, no iLO creds
  python3 farm-discover.py 192.168.1.0/24
  ILO_USER=admin ILO_PASS=secret python3 farm-discover.py 192.168.1.0/24
  python3 farm-discover.py 192.168.1.0/24 --ilo-user admin --ilo-pass secret

Without iLO credentials you still get IP + hostname + "is-iLO" (the Redfish root
is anonymous); the iLO's internal name/serial usually needs a (read-only) iLO login.
