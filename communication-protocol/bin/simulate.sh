#!/usr/bin/env bash
# simulate.sh — fake a few agents chatting so you can watch lnav update live.
# Run this in one terminal, then run `lnav chat/` in another.
set -euo pipefail

CHAT_DIR="${CHAT_DIR:-$(cd "$(dirname "$0")/.." && pwd)/chat}"
mkdir -p "$CHAT_DIR"

agents=(orchestrator agent-01 agent-02 agent-03)
templates=(
  "@researcher #task-%d new task: analyze regime"
  "@orchestrator #task-%d CLAIM"
  "@orchestrator #task-%d WORKING"
  "@orchestrator #task-%d DONE -> shared/out.csv"
  "@reviewer #task-%d please review"
  "@orchestrator #task-%d REVIEW LGTM"
  "@broadcast alive, idle"
)

while true; do
  agent="${agents[$RANDOM % ${#agents[@]}]}"
  template="${templates[$RANDOM % ${#templates[@]}]}"
  message="$(printf "$template" $((RANDOM % 90 + 10)))"
  printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$agent" "$message" >> "$CHAT_DIR/$agent.log"
  sleep "$(( (RANDOM % 3) + 1 ))"
done
