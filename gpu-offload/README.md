# GPU Offload

## Overview

Each agent runs on a modest CPU microserver, while the GPUs live on the central
JupyterHub server. **[`jupyterhub-exec`](https://github.com/quantiota/jupyterhub-exec)**
bridges the two: an agent terminal offloads heavy computation to a remote
JupyterHub kernel and streams the output back — leveraging the server's GPU
resources (CUDA, PyTorch, cuDF, …) without any local GPU.

```
┌─────────────────────────┐        WebSocket         ┌──────────────────────────┐
│   Agent Terminal (CPU)  │ ───────────────────────► │  JupyterHub Kernel (GPU) │
│   orchestration         │ ◄─────────────────────── │  execution               │
│   Claude Code / CLI     │        stdout stream      │  /srv/data access        │
└─────────────────────────┘                           └──────────────────────────┘
```

`jupyterhub-exec` is a standalone package (born from this farm) that speaks the
Jupyter kernel protocol over a raw WebSocket — no browser, no notebook UI, and
zero dependencies beyond the Python standard library.

## Install

```bash
pip install jupyterhub-exec
```

## Usage

```bash
# Run a script file on the remote GPU kernel
jh-exec run gpu_task.py

# Execute inline code
jh-exec exec "import torch; print(torch.cuda.is_available())"

# List running kernels
jh-exec kernels

# Start a new kernel
jh-exec new-kernel
```

## Configuration

Each agent gets its own JupyterHub user and API token, so its offloaded work is
isolated to its own workspace and GPU. In the AI Agent Lab, these credentials can
be entered through the **JupyterHub API Key** box in the AI Agent UI, which
delivers the credentials into the agent terminal automatically.

## Dedicating one GPU per agent

To pin a specific GPU to each JupyterHub user, add a spawn hook to
`jupyterhub_config.py` on the server:

```python
def assign_gpu(spawner):
    gpu_map = {
        "agent-01": "0",
        "agent-02": "1",
        "agent-03": "2",
        # add more agents as needed
    }
    spawner.environment["CUDA_VISIBLE_DEVICES"] = gpu_map.get(spawner.user.name, "")

c.Spawner.pre_spawn_hook = assign_gpu
```

Each agent kernel then only sees its assigned GPU — no client-side change is
needed, the kernel inherits `CUDA_VISIBLE_DEVICES` automatically.

## Server-side prerequisites

PyTorch (and any other GPU libraries) must be installed in the **JupyterHub**
Python environment, not the system Python:

```bash
sudo /opt/jupyterhub/bin/python3 -m pip install torch --index-url https://download.pytorch.org/whl/cu121
```

Validate GPU access from the agent terminal:

```bash
jh-exec exec "import torch; print(torch.cuda.is_available()); print(torch.cuda.device_count())"
```

Expected output:

```
True
4
```

## Notes

- The kernel is auto-discovered at runtime (reused if running, created if not)
  and persists across calls.
- The kernel has full access to the server filesystem (`/srv/data/...`).
- The agent terminal only receives text output — for binary results, write to a
  file on the server and fetch it via the JupyterHub Contents API.
- See the [`jupyterhub-exec`](https://github.com/quantiota/jupyterhub-exec)
  repository for the Python API (`execute`, `list_kernels`, `new_kernel`) and
  benchmarks.
