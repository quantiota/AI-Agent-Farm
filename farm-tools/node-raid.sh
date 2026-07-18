#!/usr/bin/env bash
# node-raid.sh — show each node's P410 array / RAID volumes.
#
# Reads the Smart Array from the host OS (iLO 4 won't report it). Per node it runs:
#   ssacli ctrl all show config   (controller + RAID level + disks)  [needs sudo]
#   lsblk                         (the volumes as the OS sees them)  [no sudo]
#
# Hosts: auto-discovered from farm-inventory.txt (HOST IP column of iLO rows), or pass
# host IPs as arguments.
#   ./node-raid.sh                              # hosts from farm-inventory.txt
#   ./node-raid.sh 192.168.1.114 192.168.1.15
#   SSH_USER=devbox ./node-raid.sh
set -u
SSH_USER="${SSH_USER:-devbox}"
INV="${INV:-farm-inventory.txt}"

# Optional hands-off auth: export SSH_PASS='...' (never hardcode it here).
# Uses sshpass for the login; the sudo password is piped via `sudo -S`.
SSH=(ssh -o ConnectTimeout=6 -o StrictHostKeyChecking=accept-new)
SUDO='sudo -n'
if [ -n "${SSH_PASS:-}" ]; then
    command -v sshpass >/dev/null || { echo "SSH_PASS set but sshpass missing — sudo apt install sshpass" >&2; exit 1; }
    SSH=(sshpass -e ssh -o ConnectTimeout=6 -o StrictHostKeyChecking=accept-new)
    export SSHPASS="$SSH_PASS"
    SUDO="echo \"$SSH_PASS\" | sudo -S"
fi

if [ "$#" -gt 0 ]; then
    hosts=("$@")
elif [ -f "$INV" ]; then
    mapfile -t hosts < <(awk '$3=="iLO" && $5 ~ /^192\.168\./ {print $5}' "$INV" | sort -u)
else
    echo "no $INV and no hosts given — pass host IPs, or run farm-discover --save first" >&2
    exit 1
fi
[ "${#hosts[@]}" -eq 0 ] && { echo "no hosts found" >&2; exit 1; }

for h in "${hosts[@]}"; do
    echo "==================== $h ===================="
    "${SSH[@]}" "${SSH_USER}@${h}" "
        echo '# controller:'; lspci | grep -i 'raid\|smart array' || echo '  (no Smart Array on lspci)'
        echo '# volumes (lsblk):'; lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | grep -v loop
        echo '# array config (ssacli):'
        if command -v ssacli >/dev/null; then
            $SUDO ssacli ctrl all show config 2>/dev/null || echo '  (ssacli needs sudo — run: sudo ssacli ctrl all show config)'
            echo '# OS SSD (model):'
            $SUDO ssacli ctrl all show config detail 2>/dev/null | grep -iE 'Model:.*SSD' | sed 's/^ *//' || echo '  (needs sudo)'
            echo '# physical disks (capacity / model / interface):'
            $SUDO ssacli ctrl all show config detail 2>/dev/null \
              | grep -E 'physicaldrive|Size:|Interface Type:|Drive Type:|Model:|Firmware' \
              || echo '  (needs sudo)'
        else echo '  (ssacli not installed — apt install ssacli, or read disks in BIOS/iLO ORCA)'; fi
    " 2>/dev/null || echo "  <unreachable>"
    echo
done
