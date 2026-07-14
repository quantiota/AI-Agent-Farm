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
"""
import argparse, ipaddress, json, os, shutil, socket, ssl, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

HAVE_PING = shutil.which("ping") is not None
PROBE_PORTS = (443, 22, 80)   # iLO https, host ssh, http

def local_cidr():
    """Best-effort auto-detect the primary IPv4 /24."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]; s.close()
        return f"{ip.rsplit('.',1)[0]}.0/24"
    except Exception:
        return None

def tcp_alive(ip):
    for port in PROBE_PORTS:
        try:
            with socket.create_connection((ip, port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            # refused == host is up (port closed but responding)
            if isinstance(sys.exc_info()[1], ConnectionRefusedError):
                return True
    return False

def alive(ip):
    """Host liveness: ICMP if ping exists, else a pure-Python TCP probe."""
    ip = str(ip)
    if HAVE_PING:
        try:
            r = subprocess.run(["ping", "-c", "1", "-W", "1", ip],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if r.returncode == 0:
                return ip
        except FileNotFoundError:
            pass
    return ip if tcp_alive(ip) else None

def rdns(ip):
    try: return socket.gethostbyaddr(ip)[0]
    except Exception: return "-"

def redfish_get(ip, path, auth=None, timeout=4):
    url = f"https://{ip}{path}"
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    if auth:
        import base64
        tok = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        req.add_header("Authorization", "Basic " + tok)
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return json.load(r)

def probe(ip, auth):
    """Return dict of iLO/server facts if this host is a Redfish BMC (iLO), else None."""
    try:
        root = redfish_get(ip, "/redfish/v1/", None, timeout=4)
    except Exception:
        return None
    if not isinstance(root, dict) or not (root.get("RedfishVersion") or "@odata.id" in root):
        return None
    facts = {"redfish": root.get("RedfishVersion", "?"), "ilo_name": "-",
             "ilo_fqdn": "-", "serial": "-", "model": "-", "power": "-"}
    for path, keys, dst in [
        ("/redfish/v1/Managers/1/", ("HostName",), "ilo_name"),
        ("/redfish/v1/Managers/1/EthernetInterfaces/1/", ("HostName", "FQDN"), "ilo_fqdn"),
    ]:
        try:
            d = redfish_get(ip, path, auth)
            for k in keys:
                if d.get(k): facts[dst] = d[k]; break
        except Exception:
            pass
    try:
        sysd = redfish_get(ip, "/redfish/v1/Systems/1/", auth)
        facts["serial"] = sysd.get("SerialNumber", "-") or "-"
        facts["model"]  = sysd.get("Model", "-") or "-"
        facts["power"]  = sysd.get("PowerState", "-") or "-"
        if facts["ilo_name"] == "-" and sysd.get("HostName"):
            facts["ilo_name"] = sysd["HostName"]
    except Exception:
        pass
    return facts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cidr", nargs="?", help="subnet CIDR, e.g. 192.168.1.0/24 (auto if omitted)")
    ap.add_argument("--ilo-user", default=os.environ.get("ILO_USER"))
    ap.add_argument("--ilo-pass", default=os.environ.get("ILO_PASS"))
    a = ap.parse_args()
    cidr = a.cidr or local_cidr()
    if not cidr:
        sys.exit("could not auto-detect subnet — pass one, e.g. 192.168.1.0/24")
    auth = (a.ilo_user, a.ilo_pass) if a.ilo_user and a.ilo_pass else None
    hosts = [str(h) for h in ipaddress.ip_network(cidr, strict=False).hosts()]
    print(f"# sweeping {cidr} ({len(hosts)} hosts){' with iLO creds' if auth else ' (no iLO creds)'} ...",
          file=sys.stderr)

    with ThreadPoolExecutor(max_workers=128) as ex:
        live = [ip for ip in ex.map(alive, hosts) if ip]
    print(f"# {len(live)} responded; probing Redfish/iLO ...", file=sys.stderr)

    rows = []
    with ThreadPoolExecutor(max_workers=64) as ex:
        names = dict(zip(live, ex.map(rdns, live)))
        facts = dict(zip(live, ex.map(lambda ip: probe(ip, auth), live)))
    for ip in sorted(live, key=lambda x: tuple(int(o) for o in x.split("."))):
        f = facts[ip]
        rows.append((ip, names[ip],
                     "iLO" if f else "-",
                     (f or {}).get("ilo_name", "-"),
                     (f or {}).get("serial", "-"),
                     (f or {}).get("model", "-"),
                     (f or {}).get("power", "-")))

    hdr = ("IP", "HOSTNAME", "TYPE", "iLO NAME", "SERIAL", "MODEL", "POWER")
    w = [max(len(str(r[i])) for r in rows + [hdr]) for i in range(len(hdr))]
    line = lambda r: "  ".join(str(r[i]).ljust(w[i]) for i in range(len(hdr)))
    print(line(hdr)); print("  ".join("-" * w[i] for i in range(len(hdr))))
    for r in rows: print(line(r))
    ilos = sum(1 for r in rows if r[2] == "iLO")
    print(f"\n# {len(rows)} live hosts, {ilos} iLO(s) found", file=sys.stderr)

if __name__ == "__main__":
    main()
