# AI Agent Farm — GPU Validation Setup

This document describes a **GPU validation configuration** for testing the AI Agent Farm.

The goal is to confirm that the farm can detect NVIDIA GPUs, run CUDA workloads, expose GPUs inside the JupyterHub environment, and assign GPU devices to AI agents.

## Tested Configuration

This setup was validated with:

```text
OS: Ubuntu 22.04.1 LTS
GPU: NVIDIA Tesla K80
Driver: NVIDIA 470.256.02
CUDA runtime shown by nvidia-smi: 11.4
Python environment: /opt/jupyterhub
PyTorch: 1.13.1+cu116
CUDA used by PyTorch: 11.6
GPU architecture: sm_37
```

## GPU Recommendation

The Tesla K80 is used here as a **validation GPU**. It is useful for testing the AI Agent Farm infrastructure, but users should upgrade to a recent NVIDIA GPU for production AI workloads.

Recommended production GPUs include:

```text
Tesla V100
RTX 3090
RTX 4090
A100
L40S
H100
or any modern CUDA-supported NVIDIA GPU
```

## Install NVIDIA Driver for Tesla K80

The Tesla K80 requires the legacy NVIDIA 470 driver branch.

First clean any existing NVIDIA or CUDA installation:

```bash
sudo apt update
sudo apt purge '^nvidia-.*' '^cuda.*' '^libnvidia-.*'
sudo apt autoremove --purge -y
sudo apt autoclean
```

Install required build tools:

```bash
sudo apt install -y build-essential dkms linux-headers-$(uname -r)
```

Install the NVIDIA 470 server driver:

```bash
sudo apt install -y nvidia-driver-470-server
```

If the server package is not available, use:

```bash
sudo apt install -y nvidia-driver-470
```

Reboot:

```bash
sudo reboot
```

After reboot, verify the driver:

```bash
nvidia-smi
```

Expected result:

```text
NVIDIA-SMI 470.256.02
Driver Version: 470.256.02
CUDA Version: 11.4
GPU: Tesla K80
```

## Install PyTorch in the JupyterHub Environment

The AI Agent Farm uses the JupyterHub Python environment located at:

```text
/opt/jupyterhub
```

Install PyTorch with CUDA 11.6 support:

```bash
sudo /opt/jupyterhub/bin/python3 -m pip uninstall -y torch torchvision torchaudio

sudo /opt/jupyterhub/bin/python3 -m pip install \
  torch==1.13.1+cu116 \
  torchvision==0.14.1+cu116 \
  torchaudio==0.13.1 \
  --extra-index-url https://download.pytorch.org/whl/cu116
```

## Validate PyTorch GPU Access

Run the validation as the normal JupyterHub user when possible. Use `sudo` only for installation.

```bash
/opt/jupyterhub/bin/python3 - <<'PY'
import torch

print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("torch cuda:", torch.version.cuda)
print("arch list:", torch.cuda.get_arch_list())
print("gpu:", torch.cuda.get_device_name(0))
PY
```

Expected result:

```text
torch: 1.13.1+cu116
cuda available: True
torch cuda: 11.6
arch list: ['sm_37', ...]
gpu: Tesla K80
```

The important checks are:

```text
cuda available: True
gpu: Tesla K80
sm_37
```

`sm_37` confirms that the installed PyTorch build supports the Tesla K80 architecture.

## Test a Real GPU Computation

Run:

```bash
/opt/jupyterhub/bin/python3 - <<'PY'
import torch

print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
print("gpu:", torch.cuda.get_device_name(0))

x = torch.randn(5000, 5000, device="cuda")
y = torch.randn(5000, 5000, device="cuda")
z = x @ y

torch.cuda.synchronize()

print("GPU computation OK")
print("Result shape:", z.shape)
print("Allocated memory MB:", torch.cuda.memory_allocated() / 1024**2)
PY
```

Expected result:

```text
GPU computation OK
Result shape: torch.Size([5000, 5000])
GPU: Tesla K80
```

For a faster test, use `2000 x 2000` instead of `5000 x 5000`.

## Check All Visible GPUs

Run:

```bash
nvidia-smi -L
```

Example with multiple K80 cards:

```text
GPU 0: Tesla K80
GPU 1: Tesla K80
GPU 2: Tesla K80
GPU 3: Tesla K80
...
```

A Tesla K80 card exposes two GPU devices:

```text
1 Tesla K80 card = 2 visible NVIDIA GPUs
8 Tesla K80 cards = 16 visible NVIDIA GPUs
```

## Assign One Agent per GPU

Each visible GPU can be assigned to a separate agent with `CUDA_VISIBLE_DEVICES`.

Example:

```bash
CUDA_VISIBLE_DEVICES=0 /opt/jupyterhub/bin/python3 agent.py
CUDA_VISIBLE_DEVICES=1 /opt/jupyterhub/bin/python3 agent.py
CUDA_VISIBLE_DEVICES=2 /opt/jupyterhub/bin/python3 agent.py
CUDA_VISIBLE_DEVICES=3 /opt/jupyterhub/bin/python3 agent.py
```

## Validation Checklist

A node is considered valid when all checks pass:

```text
[ ] nvidia-smi works
[ ] nvidia-smi -L lists all GPUs
[ ] PyTorch imports correctly
[ ] torch.cuda.is_available() returns True
[ ] torch.cuda.get_device_name(0) returns the GPU name
[ ] GPU computation test runs successfully
[ ] JupyterHub Python environment sees the GPU
[ ] One agent can be assigned to one GPU with CUDA_VISIBLE_DEVICES
[ ] Grafana / monitoring can observe GPU activity
```

Once these checks pass, the node is ready for AI Agent Farm testing.
