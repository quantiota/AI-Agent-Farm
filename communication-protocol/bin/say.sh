#!/usr/bin/env bash
# say.sh — append one message to this agent's own log.
# Identity comes from JUPYTERHUB_USER, falling back to USER for local testing.
#
# Usage:
#   ./bin/say.sh "@reviewer #task-42 please check shared/agent-01/vol.csv"
#   JUPYTERHUB_USER=agent-09 ./bin/say.sh "@orchestrator #task-7 done"
set -euo pipefail

CHAT_DIR="${CHAT_DIR:-$(cd "$(dirname "$0")/.." && pwd)/chat}"
USER_NAME="${JUPYTERHUB_USER:-${USER:-anon}}"

mkdir -p "$CHAT_DIR"
printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$USER_NAME" "$*" >> "$CHAT_DIR/$USER_NAME.log"
