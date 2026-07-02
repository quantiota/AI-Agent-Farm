#!/usr/bin/env python3
"""
jh_exec.py — GPU offload interface for JupyterHub kernels.

Runs Python code on a remote JupyterHub kernel from this terminal,
streaming stdout/stderr back locally.

Usage:
  python3 jh_exec.py <script.py>        # execute a script file
  python3 jh_exec.py -c "print(1+1)"   # execute inline code
  python3 jh_exec.py --list-kernels     # list all running kernels
  python3 jh_exec.py --new-kernel       # force-start a new kernel, print its ID
"""

import socket, base64, struct, json, uuid, time, os, sys, pathlib
import urllib.request

# ── Load .env (same dir as this script, or home dir) ─────────────────────────
def _load_env():
    for candidate in [pathlib.Path(__file__).parent / ".env",
                      pathlib.Path.home() / ".env"]:
        if candidate.exists():
            with open(candidate) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            break

_load_env()

# ── CONFIG ────────────────────────────────────────────────────────────────────
HOST      = os.getenv("JH_HOST",    "192.168.1.xxx")
PORT      = int(os.getenv("JH_PORT", "8000"))
USER      = os.getenv("JH_USER",    "agent-01")
TOKEN     = os.getenv("JH_TOKEN",   "")
KERNEL_ID = os.getenv("JH_KERNEL",  "")  # auto-discovered at runtime if empty
TIMEOUT   = int(os.getenv("JH_TIMEOUT", "600"))
# ─────────────────────────────────────────────────────────────────────────────


def ws_handshake(sock):
    path = f"/user/{USER}/api/kernels/{KERNEL_ID}/channels?token={TOKEN}"
    key  = base64.b64encode(os.urandom(16)).decode()
    req  = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {HOST}:{PORT}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    )
    sock.sendall(req.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        resp += sock.recv(4096)
    if b"101" not in resp:
        print("Handshake failed:", resp[:300].decode(errors="replace"), file=sys.stderr)
        sys.exit(1)


def ws_send(sock, data):
    if isinstance(data, str):
        data = data.encode()
    mask   = os.urandom(4)
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
    length = len(data)
    if length < 126:
        header = bytes([0x81, 0x80 | length]) + mask
    elif length < 65536:
        header = bytes([0x81, 0xFE]) + struct.pack(">H", length) + mask
    else:
        header = bytes([0x81, 0xFF]) + struct.pack(">Q", length) + mask
    sock.sendall(header + masked)


def ws_recv_frame(sock):
    def recv_exact(n):
        buf = b""
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("Socket closed")
            buf += chunk
        return buf

    b1, b2  = recv_exact(2)
    opcode  = b1 & 0x0F
    masked  = (b2 & 0x80) != 0
    length  = b2 & 0x7F
    if length == 126:
        length = struct.unpack(">H", recv_exact(2))[0]
    elif length == 127:
        length = struct.unpack(">Q", recv_exact(8))[0]
    mask_key = recv_exact(4) if masked else b""
    payload  = recv_exact(length)
    if masked:
        payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    if opcode == 8:
        return None       # close frame
    if opcode == 9:
        ws_send(sock, b"")  # pong
        return ""
    return payload.decode("utf-8", errors="replace")


def execute(code: str):
    global KERNEL_ID
    if not KERNEL_ID:
        KERNEL_ID = get_or_create_kernel()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.settimeout(TIMEOUT)

    ws_handshake(sock)
    print(f"[jh_exec] connected  kernel={KERNEL_ID}", file=sys.stderr)

    msg_id = str(uuid.uuid4())
    execute_msg = {
        "header": {
            "msg_id": msg_id,
            "username": USER,
            "session": str(uuid.uuid4()),
            "msg_type": "execute_request",
            "version": "5.3",
            "date": ""
        },
        "parent_header": {},
        "metadata": {},
        "content": {
            "code": code,
            "silent": False,
            "store_history": False,
            "user_expressions": {},
            "allow_stdin": False
        },
        "channel": "shell",
        "buffers": []
    }
    ws_send(sock, json.dumps(execute_msg))
    print("[jh_exec] execute_request sent", file=sys.stderr)

    deadline = time.time() + TIMEOUT
    while time.time() < deadline:
        try:
            frame = ws_recv_frame(sock)
        except socket.timeout:
            print(".", end="", flush=True, file=sys.stderr)
            continue
        if frame is None:
            break
        if not frame:
            continue
        try:
            msg = json.loads(frame)
        except json.JSONDecodeError:
            continue

        mt = msg.get("msg_type", "")
        if mt == "stream":
            print(msg["content"]["text"], end="", flush=True)
        elif mt in ("execute_result", "display_data"):
            print(msg["content"]["data"].get("text/plain", ""), flush=True)
        elif mt == "error":
            print("KERNEL ERROR: " + msg["content"]["evalue"], file=sys.stderr)
            for line in msg["content"]["traceback"]:
                print(line, file=sys.stderr)
            break
        elif mt == "execute_reply":
            print(f"\n[jh_exec] done  status={msg['content']['status']}", file=sys.stderr)
            break

    sock.close()


def list_kernels():
    url = f"http://{HOST}:{PORT}/user/{USER}/api/kernels?token={TOKEN}"
    with urllib.request.urlopen(url) as resp:
        kernels = json.loads(resp.read())
    return kernels


def get_or_create_kernel():
    """Return an existing python3 kernel ID, or start a new one."""
    kernels = list_kernels()
    for k in kernels:
        if k["name"] == "python3":
            print(f"[jh_exec] reusing kernel: {k['id']}  state={k['execution_state']}", file=sys.stderr)
            return k["id"]
    return new_kernel()


def new_kernel():
    url = f"http://{HOST}:{PORT}/user/{USER}/api/kernels?token={TOKEN}"
    req = urllib.request.Request(
        url, data=b'{"name":"python3"}',
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    print(f"[jh_exec] new kernel: {data['id']}", file=sys.stderr)
    return data["id"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] == "--list-kernels":
        kernels = list_kernels()
        if not kernels:
            print("No running kernels.")
        for k in kernels:
            print(f"{k['id']}  name={k['name']}  state={k['execution_state']}  last_activity={k['last_activity']}")
        sys.exit(0)

    if sys.argv[1] == "--new-kernel":
        print(new_kernel())
    elif sys.argv[1] == "--kernel":
        # Find or create a kernel and write it to .env
        kid = get_or_create_kernel()
        env_path = pathlib.Path.home() / ".env"
        lines = env_path.read_text().splitlines() if env_path.exists() else []
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("JH_KERNEL="):
                lines[i] = f"JH_KERNEL={kid}"
                updated = True
                break
        if not updated:
            lines.append(f"JH_KERNEL={kid}")
        env_path.write_text("\n".join(lines) + "\n")
        print(f"[jh_exec] JH_KERNEL={kid} written to {env_path}", file=sys.stderr)
        print(kid)
    elif sys.argv[1] == "-c":
        if len(sys.argv) < 3:
            print("Error: -c requires a code argument", file=sys.stderr)
            sys.exit(1)
        execute(sys.argv[2])
    else:
        with open(sys.argv[1]) as f:
            code = f.read()
        execute(code)