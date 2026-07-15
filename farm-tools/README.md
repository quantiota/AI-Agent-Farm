# farm-tools

Operational tools for the physical farm (the HP MicroServer Gen8 fleet).

## `farm-discover.py` — find nodes on the LAN

Discovers farm nodes on the local network and prints **IP, hostname, and iLO name**
(plus MAC / serial / model / power / **paired host IP** when iLO credentials are given).

Built to run on the **GPU server** (or any box on the same LAN). **Stdlib only** —
needs just `python3`. No nmap / arp-scan / jq / root. Host liveness uses ICMP when
`ping` is present, otherwise a pure-Python TCP probe (ports 443 / 22 / 80).

### How it works

1. Ping-sweeps the subnet (auto-detected `/24`, or a CIDR you pass).
2. Reverse-DNS resolves each responder's hostname.
3. Probes each host's Redfish endpoint (`https://IP/redfish/v1/`) to detect an
   HP **iLO** (Gen8 = iLO 4), then reads the iLO name and server serial/model.
4. With iLO creds, pairs each iLO to its **HOST IP** on the same row — asks the iLO for its
   host NIC (Redfish `Systems`), then matches that MAC to the LAN ARP table (or uses the
   host's AMS-reported IP if the Agentless Management Service is running).

### Usage

```bash
# auto-detect the /24, no iLO login (IP + hostname + is-iLO only)
python3 farm-discover.py

# specify the subnet
python3 farm-discover.py 192.168.1.0/24

# with an iLO login -> also fills MAC / SERIAL / MODEL / POWER + the paired HOST IP
ILO_USER=Administrator ILO_PASS=secret python3 farm-discover.py 192.168.1.0/24
#   or: python3 farm-discover.py 192.168.1.0/24 --ilo-user Administrator --ilo-pass secret

# per-iLO passwords (refurb Gen8s each have a unique factory password) -> a creds file
python3 farm-discover.py 192.168.1.0/24 --creds-file ~/ilo-creds.txt
#   or:  ILO_CREDS=~/ilo-creds.txt python3 farm-discover.py 192.168.1.0/24
```

Creds-file format — one `ip user password` per line (`#` comments ok), then `chmod 600` it:
```
# ip            user           password
192.168.1.27    Administrator  <pass-from-sticker>
192.168.1.116   Administrator  <pass-from-sticker>
```

### Output

```
IP             HOSTNAME           TYPE  iLO NAME       HOST IP        MAC                SERIAL      MODEL   POWER
192.168.1.27   ILOCZ150901RE.lan  iLO   ILOCZ150901RE  192.168.1.15   xx:xx:xx:xx:xx:xx  CZ150901RE  Gen8    On
192.168.1.15   microserver02.lan  -     -              -              -                  -           -       -
...
```
Each Gen8 shows up twice: the **iLO** row (with its paired `HOST IP`) and the **host OS** row.

### Notes

- **What needs creds.** iLO **name / serial / model** come from the anonymous `xmldata`
  endpoint (no login). **MAC, POWER, and the paired HOST IP** need an iLO login.
- **Per-iLO passwords.** Refurb Gen8s each ship with a unique factory iLO password — use
  `--creds-file` (above). Long-term, standardizing all iLOs to one admin password lets you
  drop back to a single `ILO_USER`/`ILO_PASS`.
- **Bare nodes** (no OS yet) have no host IP → `HOST IP` stays `-` until installed.
- **HOST IP pairing** works when the host is on the **same subnet** (ARP) or runs **AMS**.
- **Subnet.** Pass the exact CIDR if the farm isn't a `/24`.
- Copy the repo (or just this file) to the box you run it from.

