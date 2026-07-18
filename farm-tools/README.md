# farm-tools

Operational tools for the physical farm (the HP MicroServer Gen8 fleet).

## `farm-discover.py` — find nodes on the LAN

Discovers farm nodes on the local network and prints **IP, hostname, and iLO name**
(plus MAC / serial / CPU / RAM / health / power / temp / **paired host IP** when iLO
credentials are given).

Built to run on the **GPU server** (or any box on the same LAN). **Stdlib only** —
needs just `python3`. 
### Usage

```bash
# auto-detect the /24, no iLO login (IP + hostname + is-iLO only)
python3 farm-discover.py

# specify the subnet
python3 farm-discover.py 192.168.1.0/24

# with an iLO login -> also fills MAC / SERIAL / CPU / RAM / HEALTH / POWER / TEMP + the paired HOST IP
ILO_USER=Administrator ILO_PASS=secret python3 farm-discover.py 192.168.1.0/24
#   or: python3 farm-discover.py 192.168.1.0/24 --ilo-user Administrator --ilo-pass secret

# per-iLO passwords (refurb Gen8s each have a unique factory password) -> a creds file
python3 farm-discover.py 192.168.1.0/24 --creds-file ~/ilo-creds.txt
#   or:  ILO_CREDS=~/ilo-creds.txt python3 farm-discover.py 192.168.1.0/24

# everyday command: auto-detect the subnet, use the creds file, and save a dated inventory
python3 farm-discover.py --creds-file ilo-creds.txt --save farm-inventory.txt
```

Creds-file format — one `ip user password` per line (`#` comments ok), then `chmod 600` it:
```
# ip            user           password
192.168.1.27    Administrator  <pass-from-sticker>
192.168.1.116   Administrator  <pass-from-sticker>
```

### Output

With iLO creds, each iLO row fills in CPU / RAM / HEALTH / POWER / TEMP and its paired HOST IP:

```
IP             HOSTNAME           TYPE  iLO NAME       HOST IP        MAC                SERIAL      CPU                       RAM  HEALTH  POWER  TEMP
192.168.1.116  ILOCZxxxxxxxx.lan  iLO   ILOCZxxxxxxxx  192.168.1.113  xx:xx:xx:xx:xx:xx  CZxxxxxxxx  1x E3-1265L V2 @ 2.50GHz  16G  OK      On     35C
192.168.1.113  microserver01.lan  -     -              -              -                  -           -                         -    -       -      -
...
```
Each Gen8 shows up twice: the **iLO** row (with its paired `HOST IP`, CPU/RAM/health/temp) and the
**host OS** row. `TEMP` = inlet/ambient °C; `HEALTH` = iLO overall status. Storage/RAID isn't shown
(iLO 4 can't report the P410 without AMS) — use `node-raid.sh` for that.

### HOST IP pairing needs AMS on the host

On Gen8 / iLO 4 the iLO only knows its host's IP when **AMS (Agentless Management Service)**
runs on that host — without it, `HOST IP` stays `-`. Install `hp-ams` per host:

```bash
wget https://downloads.linux.hpe.com/SDR/repo/mcp/ubuntu/pool/non-free/hp-ams_2.6.2-2551.13_amd64.deb
sudo dpkg -i hp-ams_2.6.2-2551.13_amd64.deb
sudo systemctl status hp-ams          # -> active (running), "amsHelper Started"
```

Give it a minute, then re-run `farm-discover` — the host's IP now fills on its iLO row.

## Host-side scripts (over SSH)

Run these from the **GPU server** (same box as `farm-discover`, which can SSH the nodes). Both
auto-discover hosts from the `HOST IP` column of `farm-inventory.txt` (run `farm-discover --save`
first), or take host IPs as arguments. Optional hands-off auth: `SSH_PASS='...'` (needs
`sshpass`; never hardcoded).

- **`node-install-date.sh`** — each node's Ubuntu install date (root-fs / installer timestamp).
- **`node-raid.sh`** — each node's P410 array: controller, volumes (`lsblk`), RAID level,
  OS SSD model, and every physical disk's capacity / model / interface.

```bash
SSH_PASS='...' ./node-raid.sh
SSH_PASS='...' ./node-install-date.sh
```

### ssacli — read the P410 RAID from the host

iLO 4 doesn't expose the P410 array; `node-raid.sh` reads it with HPE's `ssacli` on each host
(RAID level + physical-disk detail need it). Install per host (direct `.deb`, no repo/GPG):

```bash
wget https://downloads.linux.hpe.com/SDR/repo/mcp/ubuntu/pool/non-free/ssacli-6.60-8.0_amd64.deb
sudo dpkg -i ssacli-6.60-8.0_amd64.deb
```

Then `sudo ssacli ctrl all show config` shows the controller, logical drives (RAID level), and
physical disks. Without `ssacli`, `node-raid.sh` still shows the controller (`lspci`) and volume
sizes (`lsblk`).



