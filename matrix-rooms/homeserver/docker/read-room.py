#!/usr/bin/env python3
"""Print the messages of every room the admin account is in, oldest first.

Run on the homeserver box, from the docker folder of the homeserver:

    python3 read-room.py

It asks for the admin password (the password itself, not its hash), reaches
Synapse directly on the docker network (no nginx, no certificate), prints the
rooms, and logs out again. Nothing has to be copied or pasted.
"""
import getpass
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

USER = os.environ.get("MATRIX_ADMIN", "admin")


def synapse_url():
    if os.environ.get("SYNAPSE_URL"):
        return os.environ["SYNAPSE_URL"]
    try:
        cid = subprocess.check_output(
            ["docker", "compose", "ps", "-q", "synapse"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        cid = ""
    if not cid:
        sys.exit("Synapse container not found. Run this from the docker folder "
                 "of the homeserver, with the stack up.")
    ips = subprocess.check_output(
        ["docker", "inspect", "-f",
         "{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}", cid],
        text=True).split()
    return "http://%s:8008" % ips[0]


def call(base, path, data=None, token=None, method=None):
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(base + path, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return json.load(e)
        except ValueError:
            return {"errcode": str(e.code), "error": e.reason}
    except urllib.error.URLError as e:
        sys.exit("Synapse does not answer at %s: %s" % (base, e.reason))


def main():
    base = synapse_url()
    password = getpass.getpass("Password of %s: " % USER)
    login = call(base, "/_matrix/client/v3/login", {
        "type": "m.login.password",
        "identifier": {"type": "m.id.user", "user": USER},
        "password": password,
        "initial_device_display_name": "read-room.py"})
    token = login.get("access_token")
    if not token:
        sys.exit("Login refused: %s %s" % (login.get("errcode"), login.get("error")))
    try:
        rooms = call(base, "/_matrix/client/v3/joined_rooms", token=token).get("joined_rooms", [])
        if not rooms:
            print("%s is in no room." % USER)
        for room in rooms:
            rid = urllib.parse.quote(room, safe="")
            name = call(base, "/_matrix/client/v3/rooms/%s/state/m.room.name" % rid,
                        token=token).get("name", "(no name)")
            print("=" * 72)
            print("ROOM: %s   %s" % (name, room))
            print("=" * 72)
            n, start = 0, None
            while True:
                q = "/_matrix/client/v3/rooms/%s/messages?dir=f&limit=100" % rid
                if start:
                    q += "&from=" + urllib.parse.quote(start, safe="")
                page = call(base, q, token=token)
                for e in page.get("chunk", []):
                    if e.get("type") == "m.room.message":
                        n += 1
                        print("\n%d. %s\n%s" % (n, e["sender"], e["content"].get("body", "")))
                    elif e.get("type") == "m.room.encrypted":
                        n += 1
                        print("\n%d. %s\n[encrypted]" % (n, e["sender"]))
                start = page.get("end")
                if not page.get("chunk") or not start:
                    break
            print("\n-- %d messages --\n" % n)
    finally:
        call(base, "/_matrix/client/v3/logout", {}, token=token, method="POST")


if __name__ == "__main__":
    main()
