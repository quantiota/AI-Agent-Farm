# JupyterHub GPU Offload Interface

## Overview

`jh_exec.py` is a lightweight Python script that lets an AI agent terminal
offload heavy computation to a remote JupyterHub kernel — in particular to
leverage the server's GPU resources (CUDA, cuDF, PyTorch, etc.).

```
┌─────────────────────────┐        WebSocket         ┌──────────────────────────┐
│   Agent Terminal (CPU)  │ ───────────────────────► │  JupyterHub Kernel (GPU) │
│   orchestration         │ ◄─────────────────────── │  execution               │
│   Claude Code / CLI     │        stdout stream      │  /srv/data access        │
└─────────────────────────┘                           └──────────────────────────┘
```

The script uses only Python built-ins (`socket`, `json`, `struct`) — no
external dependencies required.

---

## Usage

```bash
# Execute a script file on the remote kernel
python3 jh_exec.py my_script.py

# Execute inline code
python3 jh_exec.py -c "import torch; print(torch.cuda.is_available())"

# Start a new kernel and get its ID
python3 jh_exec.py --new-kernel
```

---

## Configuration

Set via environment variables or edit the `CONFIG` block at the top of the script:

| Variable      | Default                                | Description                  |
|---------------|----------------------------------------|------------------------------|
| `JH_HOST`     | `192.168.1.xxx`                        | JupyterHub server IP         |
| `JH_PORT`     | `8000`                                 | JupyterHub port              |
| `JH_USER`     | `agent-01`                             | JupyterHub username          |
| `JH_TOKEN`    | *(see script)*                         | API token                    |
| `JH_KERNEL`   | *(see script)*                         | Kernel ID to connect to      |
| `JH_TIMEOUT`  | `600`                                  | Max seconds to wait (s)      |

```bash
export JH_HOST=192.168.1.xxx
export JH_TOKEN=xxxxxxxxxxxxxxxxxxx
export JH_KERNEL=xxxxxxxxxxxxxxxxxxxxxxxxx
python3 jh_exec.py gpu_task.py
```

---

## How it works

1. Opens a raw TCP socket to the JupyterHub server
2. Performs the WebSocket HTTP upgrade handshake manually
3. Sends a Jupyter `execute_request` message to the kernel channel
4. Streams `stream`, `execute_result`, and `error` messages back to stdout/stderr
5. Exits cleanly on `execute_reply`

---

## Notes

- The kernel must already be running (use `--new-kernel` to start one)
- The kernel has full access to the server filesystem (`/srv/data/...`)
- GPU libraries available on the server (PyTorch, cuDF, etc.) are accessible normally
- The agent terminal only receives text output — for binary results, write to a file
  on the server and fetch via the JupyterHub Contents API