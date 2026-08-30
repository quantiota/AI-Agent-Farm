  GNU nano 6.2                                           fleet-power.sh
#!/usr/bin/env bash
# fleet-power.sh — power the farm nodes on/off via iLO Redfish (no SSH needed).
#
# Reads iLO credentials from a LOCAL file (default: ./ilo-creds.txt), one line per node:
#     <ilo-ip>   <user>   <password>
#
# State-aware: reads each node's PowerState first, then acts ONLY where needed —
#   up   -> only nodes currently Off   (On)
#   down -> only nodes currently On    (PushPowerButton — momentary press, clean OS halt)
#   off  -> only nodes currently On    (ForceOff — hard)
# so a mix of on/off nodes converges correctly, and 'down' never toggles an off node back on.
#
# SECURITY: keep the creds file OUT of git and chmod 600 — it holds iLO passwords.
#           This script itself contains no secrets and is safe to commit.
set -euo pipefail

CREDS="${ILO_CREDS:-$(dirname "$0")/ilo-creds.txt}"
CMD="${1:-}"
SYS="/redfish/v1/Systems/1/"

usage() {
  cat <<EOF
usage: $(basename "$0") {up|down|off|status} [--yes]
  up      power ON nodes that are Off     (Redfish ResetType On)
  down    graceful shutdown of ON nodes   (PushPowerButton — momentary press, OS halts cleanly)
  off     force OFF of ON nodes (hard)     (ForceOff — use only if 'down' is ignored)
  status  show each node's PowerState
  --yes   skip the confirmation prompt on down/off
Each command reads PowerState first and skips nodes already in the target state.
creds file: $CREDS   (lines: "IP  USER  PASS")
EOF
  exit 1
}

case "$CMD" in
  up|down|off|status) ;;
  *) usage ;;
esac

[[ -f "$CREDS" ]] || { echo "creds file not found: $CREDS" >&2; exit 1; }

# confirm before shutting the whole fleet down
if [[ "$CMD" == "down" || "$CMD" == "off" ]] && [[ "${2:-}" != "--yes" ]]; then
  read -rp "About to '$CMD' ALL eligible nodes in $CREDS. Continue? [y/N] " ans
  [[ "$ans" == "y" || "$ans" == "Y" ]] || { echo "aborted"; exit 0; }
fi

while read -r ip user pass _; do
  [[ -z "${ip:-}" || "${ip:0:1}" == "#" ]] && continue

  state=$(curl -sk -m 8 -u "$user:$pass" "https://$ip$SYS" \
          | grep -o '"PowerState"[^,]*' | cut -d'"' -f4)
  state="${state:-unreachable}"

  if [[ "$CMD" == "status" ]]; then
    printf "%-15s %s\n" "$ip" "$state"; continue
  fi
  if [[ "$state" == "unreachable" ]]; then
    printf "%-15s unreachable — skip\n" "$ip"; continue
  fi

  # filter: only act on nodes not already in the target state
  case "$CMD" in
    up)   [[ "$state" == "Off" ]] && act=On             || { printf "%-15s already On  — skip\n" "$ip"; continue; } ;;
    down) [[ "$state" == "On"  ]] && act=PushPowerButton || { printf "%-15s already Off — skip\n" "$ip"; continue; } ;;
    off)  [[ "$state" == "On"  ]] && act=ForceOff        || { printf "%-15s already Off — skip\n" "$ip"; continue; } ;;
  esac

  code=$(curl -skL -m 8 -o /dev/null -w '%{http_code}' -u "$user:$pass" \
         -H 'Content-Type: application/json' \
         -X POST "https://$ip${SYS}Actions/ComputerSystem.Reset/" \
         -d "{\"ResetType\":\"$act\"}")
  printf "%-15s %-16s -> HTTP %s\n" "$ip" "$act" "$code"
done < "$CREDS"
