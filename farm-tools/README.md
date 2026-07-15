# farm-tools

Operational tools for the physical farm (the HP MicroServer Gen8 fleet).

## `farm-discover.py` — find nodes on the LAN

Discovers farm nodes on the local network and prints **IP, hostname, and iLO name**
(plus MAC / serial / model / power / **paired host IP** when iLO credentials are given).

Built to run on the **GPU server** (or any box on the same LAN). **Stdlib only** —
needs just `python3`. 


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



