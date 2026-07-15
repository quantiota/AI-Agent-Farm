#!/usr/bin/env python3
"""farm-discover.py — discover farm nodes on the LAN: IP, hostname, and iLO name.

Runs on the GPU server (or any box on the same LAN). Stdlib only — needs just
`python3` and the system `ping`. No nmap / arp-scan / jq required.

What it does:
  1. Ping-sweeps the subnet (auto-detected, or pass a CIDR).
  2. Reverse-DNS resolves each responder's hostname.
  3. Probes each host's Redfish endpoint (https://IP/redfish/v1/) to detect an
     HP iLO (Gen8 = iLO 4), then reads the iLO name + server serial/model.
  4. With iLO creds, pairs each iLO to its HOST IP on the same row — asks the iLO for
     its host NIC (Redfish Systems), then matches that MAC to the LAN ARP table (or uses
     the AMS-reported IP if the host runs the Agentless Management Service).

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

def arp_map():
    """{ip: MAC} from the local ARP/neighbour table (the sweep populates it)."""
    m = {}
    try:
        out = subprocess.run(["ip", "neigh"], capture_output=True, text=True).stdout
        for ln in out.splitlines():
            p = ln.split()
            if "lladdr" in p:
                m[p[0]] = p[p.index("lladdr") + 1].upper()
    except Exception:
        pass
    return m

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

def ilo_xmldata(ip):
    """HP iLO's ANONYMOUS info endpoint — serial (SBSN), model (SPN), iLO name (SN).
       Returns dict or None. No credentials needed."""
    import xml.etree.ElementTree as ET
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(f"https://{ip}/xmldata?item=all", timeout=4, context=ctx) as r:
            root = ET.fromstring(r.read())
    except Exception:
        return None
    def txt(tag):
        e = root.find(f".//{tag}"); return (e.text or "").strip() if e is not None else ""
    if root.tag != "RIMP" and root.find(".//HSI") is None:
        return None
    return {"serial": txt("SBSN") or "-", "model": txt("SPN") or "-",
            "ilo_sn": txt("SN") or "-", "ilo_pn": txt("PN") or "-"}

def probe(ip, auth):
    """Return dict of iLO/server facts if this host is an HP iLO, else None."""
    facts = {"ilo_name": "-", "ilo_fqdn": "-", "mac": "-", "serial": "-", "model": "-", "power": "-"}
    # 1) anonymous iLO identification (works with no creds)
    xd = ilo_xmldata(ip)
    if xd:
        facts["serial"] = xd["serial"]; facts["model"] = xd["model"]
        # default iLO name is ILO<serial> unless renamed
        if xd["serial"] != "-": facts["ilo_name"] = "ILO" + xd["serial"]
    # 2) Redfish for the real iLO name + power (root is anonymous; detail needs auth)
    try:
        root = redfish_get(ip, "/redfish/v1/", None, timeout=4)
    except Exception:
        return facts if xd else None
    if not (isinstance(root, dict) and (root.get("RedfishVersion") or "@odata.id" in root)):
        return facts if xd else None
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
    # iLO NIC MAC — from Redfish (auth), else derive from an ILO<12-hex> default name
    try:
        eth = redfish_get(ip, "/redfish/v1/Managers/1/EthernetInterfaces/1/", auth)
        facts["mac"] = eth.get("MACAddress") or eth.get("PermanentMACAddress") or facts["mac"]
    except Exception:
        pass
    if facts["mac"] == "-":
        import re
        m = re.fullmatch(r"ILO([0-9A-Fa-f]{12})", facts["ilo_name"])
        if m:
            h = m.group(1); facts["mac"] = ":".join(h[i:i+2] for i in range(0, 12, 2)).upper()
    try:
        sysd = redfish_get(ip, "/redfish/v1/Systems/1/", auth)
        if sysd.get("SerialNumber"): facts["serial"] = sysd["SerialNumber"]
        if sysd.get("Model"):        facts["model"]  = sysd["Model"]
        facts["power"] = sysd.get("PowerState", "-") or "-"
        if facts["ilo_name"] == "-" and sysd.get("HostName"):
            facts["ilo_name"] = sysd["HostName"]
    except Exception:
        pass
    # host NICs: MACs (+ AMS-reported IPs) from Redfish Systems (needs auth)
    facts["host_macs"], facts["host_ip"] = [], "-"
    try:
        coll = redfish_get(ip, "/redfish/v1/Systems/1/EthernetInterfaces/", auth)
        for mem in coll.get("Members", []):
            d = redfish_get(ip, mem["@odata.id"], auth)
            mac = (d.get("MACAddress") or d.get("PermanentMACAddress") or "").upper()
            if mac: facts["host_macs"].append(mac)
            for a4 in (d.get("IPv4Addresses") or []):
                addr = a4.get("Address")
                if addr and addr != "0.0.0.0" and facts["host_ip"] == "-":
                    facts["host_ip"] = addr
    except Exception:
        pass
    return facts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cidr", nargs="?", help="subnet CIDR, e.g. 192.168.1.0/24 (auto if omitted)")
    ap.add_argument("--ilo-user", default=os.environ.get("ILO_USER"))
    ap.add_argument("--ilo-pass", default=os.environ.get("ILO_PASS"))
    ap.add_argument("--creds-file", default=os.environ.get("ILO_CREDS"),
                    help="per-iLO creds: one 'ip user password' per line (# comments ok)")
    a = ap.parse_args()
    cidr = a.cidr or local_cidr()
    if not cidr:
        sys.exit("could not auto-detect subnet — pass one, e.g. 192.168.1.0/24")
    global_auth = (a.ilo_user, a.ilo_pass) if a.ilo_user and a.ilo_pass else None
    cred_map = {}   # ip -> (user, pass), for iLOs with their own passwords
    if a.creds_file:
        with open(a.creds_file) as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln or ln.startswith("#"):
                    continue
                p = ln.split()
                if len(p) >= 3:
                    cred_map[p[0]] = (p[1], " ".join(p[2:]))
    def auth_for(ip):
        return cred_map.get(ip, global_auth)
    hosts = [str(h) for h in ipaddress.ip_network(cidr, strict=False).hosts()]
    have_creds = bool(global_auth or cred_map)
    print(f"# sweeping {cidr} ({len(hosts)} hosts){' with iLO creds' if have_creds else ' (no iLO creds)'} ...",
          file=sys.stderr)

    with ThreadPoolExecutor(max_workers=128) as ex:
        live = [ip for ip in ex.map(alive, hosts) if ip]
    print(f"# {len(live)} responded; probing Redfish/iLO ...", file=sys.stderr)

    rows = []
    arp = arp_map()   # ip -> MAC, populated by the sweep (same-subnet hosts)
    with ThreadPoolExecutor(max_workers=64) as ex:
        names = dict(zip(live, ex.map(rdns, live)))
        facts = dict(zip(live, ex.map(lambda ip: probe(ip, auth_for(ip)), live)))
    for ip in sorted(live, key=lambda x: tuple(int(o) for o in x.split("."))):
        f = facts[ip] or {}
        # host IP: prefer AMS-reported, else match the host NIC MAC to the ARP table
        host_ip = f.get("host_ip", "-")
        if host_ip == "-" and f.get("host_macs"):
            for mac in f["host_macs"]:
                hit = next((hip for hip, hmac in arp.items() if hmac == mac), None)
                if hit: host_ip = hit; break
        rows.append((ip, names[ip],
                     "iLO" if facts[ip] else "-",
                     f.get("ilo_name", "-"),
                     host_ip,
                     f.get("mac", "-"),
                     f.get("serial", "-"),
                     f.get("model", "-"),
                     f.get("power", "-")))

    hdr = ("IP", "HOSTNAME", "TYPE", "iLO NAME", "HOST IP", "MAC", "SERIAL", "MODEL", "POWER")
    w = [max(len(str(r[i])) for r in rows + [hdr]) for i in range(len(hdr))]
    line = lambda r: "  ".join(str(r[i]).ljust(w[i]) for i in range(len(hdr)))
    print(line(hdr)); print("  ".join("-" * w[i] for i in range(len(hdr))))
    for r in rows: print(line(r))
    ilos = sum(1 for r in rows if r[2] == "iLO")
    print(f"\n# {len(rows)} live hosts, {ilos} iLO(s) found", file=sys.stderr)

if __name__ == "__main__":
    main()
