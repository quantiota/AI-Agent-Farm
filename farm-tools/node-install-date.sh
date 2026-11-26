#!/usr/bin/env bash
# node-install-date.sh — report each node's Ubuntu install date (root-fs creation time).
#
# The install date == when the installer formatted the root filesystem, read via
# `tune2fs -l <root-dev> | Filesystem created`. SSHes each host and prints one line.
#
# Hosts: auto-discovered from farm-inventory.txt (HOST IP column of iLO rows), or pass
# host IPs/names as arguments.
#
#   ./node-install-date.sh                              # read hosts from farm-inventory.txt
#   ./node-install-date.sh 192.168.1.114 192.168.1.15   # explicit hosts
#   SSH_USER=devbox ./node-install-date.sh
#   SSH_PASS='...' ./node-install-date.sh               # password once, for every node
set -u
SSH_USER="${SSH_USER:-devbox}"
INV="${INV:-farm-inventory.txt}"

# Optional hands-off auth: export SSH_PASS='...' (never hardcode it here).
SSH=(ssh -o ConnectTimeout=6 -o StrictHostKeyChecking=accept-new)
if [ -n "${SSH_PASS:-}" ]; then
    command -v sshpass >/dev/null || { echo "SSH_PASS set but sshpass missing — sudo apt install sshpass" >&2; exit 1; }
    SSH=(sshpass -e ssh -o ConnectTimeout=6 -o StrictHostKeyChecking=accept-new)
    export SSHPASS="$SSH_PASS"
fi

# collect hosts
if [ "$#" -gt 0 ]; then
    hosts=("$@")
else
    if [ ! -f "$INV" ]; then
        echo "no $INV and no hosts given — pass host IPs, or run farm-discover with --save first" >&2
        exit 1
    fi
    mapfile -t hosts < <(awk '$3=="iLO" && $5 ~ /^192\.168\./ {print $5}' "$INV" | sort -u)
fi

[ "${#hosts[@]}" -eq 0 ] && { echo "no microserver hosts found" >&2; exit 1; }

printf "%-16s  %-22s  %s\n" "HOST" "INSTALLED (root fs)" "HOSTNAME"
printf "%-16s  %-22s  %s\n" "----------------" "----------------------" "--------"
for h in "${hosts[@]}"; do
    out=$("${SSH[@]}" "${SSH_USER}@${h}" \
        'stat -c %y /var/log/installer 2>/dev/null | cut -d. -f1; hostname' 2>/dev/null)
    date=$(printf '%s\n' "$out" | sed -n '1p')
    name=$(printf '%s\n' "$out" | sed -n '2p')
    printf "%-16s  %-22s  %s\n" "$h" "${date:-<unreachable>}" "${name:--}"
done
