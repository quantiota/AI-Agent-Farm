# node-deployment — bringing a bare MicroServer online

Provisioning a physical HP MicroServer Gen8 into a federation node: bare metal → installed OS,
mostly over **iLO** (the boxes have no monitor and, until installed, no host IP).

## 1. Find the node's iLO

Use [`../farm-tools/farm-discover.py`](../farm-tools/farm-discover.py) — sweeps the LAN and
reports each iLO's IP, serial, MAC, and name. That IP is your remote hand on the box.

## 2. Storage (Smart Array P410)

Ubuntu sees the P410's logical drives **natively** (in-kernel `hpsa` driver) as `/dev/sd*`.
Typical layout: a **small volume for the OS** (e.g. 250 GB) and a **RAID for data** (e.g.
4×1TB). Install the OS on the small volume; leave the RAID for data.

## 3. Install Ubuntu via iLO URL virtual media

The reliable remote path: mount the Ubuntu Server ISO from an HTTP URL as the virtual CD.

1. **Host the ISO on a LAN box** — plain **HTTP** (iLO 4's TLS is finicky), and it **must be a
   Range-capable server** — stock `python3 -m http.server` boot-loops (iLO seeks the ISO to boot it):
   ```bash
   sudo /opt/jupyterhub/bin/python3 -m pip install rangehttpserver
   cd /dir/with/iso && /opt/jupyterhub/bin/python3 -m RangeHTTPServer 5000
   # -> http://<lan-ip>:5000/ubuntu-22.04.5-live-server-amd64.iso
   ```
2. In iLO, set the **virtual CD/DVD to that URL**, set **one-time boot → CD**, power on.
3. Install onto the **small (OS) volume**; leave the RAID for data.
4. After install, set boot order to the OS volume.


## Ports note

Serve on an **unused high port** 