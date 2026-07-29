#!/usr/bin/env bash
# fleet-power.sh — power the farm nodes on/off via iLO Redfish (no SSH needed).
#
# Reads iLO credentials from a LOCAL file (default: ./ilo-creds.txt), one line per node:
#     <ilo-ip>   <user>   <password>
#
# SECURITY: keep that creds file OUT of git and chmod 600 — it holds iLO passwords.
#           This script itself contains no secrets and is safe to commit.
set -euo pipefail

CREDS="${ILO_CREDS:-$(dirname "$0")/ilo-creds.txt}"
CMD="${1:-}"

usage() {
  cat <<EOF
usage: $(basename "$0") {up|down|off|status} [--yes]
  up      power ON all nodes        (Redfish ResetType On)
  down    graceful ACPI shutdown    (ResetType PushPowerButton — momentary press, OS halts cleanly)
  off     force power OFF (hard)     (ResetType ForceOff — use only if 'down' is ignored)
  status  show each node's PowerState
  --yes   skip the confirmation prompt on down/off
creds file: $CREDS   (lines: "IP  USER  PASS")
EOF
  exit 1
}

case "$CMD" in
  up)     RESET=On ;;
  down)   RESET=PushPowerButton ;;
  off)    RESET=ForceOff ;;
  status) RESET=status ;;
  *)      usage ;;
esac

[[ -f "$CREDS" ]] || { echo "creds file not found: $CREDS" >&2; exit 1; }

# confirm before shutting the whole fleet down
if [[ "$RESET" == "PushPowerButton" || "$RESET" == "ForceOff" ]] && [[ "${2:-}" != "--yes" ]]; then
  read -rp "About to '$CMD' ALL nodes listed in $CREDS. Continue? [y/N] " ans
  [[ "$ans" == "y" || "$ans" == "Y" ]] || { echo "aborted"; exit 0; }
fi

while read -r ip user pass _; do
  [[ -z "${ip:-}" || "${ip:0:1}" == "#" ]] && continue
  if [[ "$RESET" == "status" ]]; then
    state=$(curl -sk -m 8 -u "$user:$pass" "https://$ip/redfish/v1/Systems/1/" \
            | grep -o '"PowerState"[^,]*' | cut -d'"' -f4)
    printf "%-15s %s\n" "$ip" "${state:-unreachable}"
  else
    code=$(curl -skL -m 8 -o /dev/null -w '%{http_code}' -u "$user:$pass" \
           -H 'Content-Type: application/json' \
           -X POST "https://$ip/redfish/v1/Systems/1/Actions/ComputerSystem.Reset/" \
           -d "{\"ResetType\":\"$RESET\"}")
    printf "%-15s %-16s -> HTTP %s\n" "$ip" "$RESET" "$code"
  fi
done < "$CREDS"
