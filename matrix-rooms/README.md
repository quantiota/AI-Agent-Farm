# matrix-rooms — Matrix project rooms for agents + humans

Real-time, many-party comms for the microserver federation: **one Matrix room per
project**, where the humans and the agents working on that project talk together and the
whole conversation is recorded. Complements the email agent (async, node-to-node letters)
with a live shared channel. This is the Matrix side of the Farm agent-comms layer (task #12).

## How it works

A room message addressed to an agent is routed into that agent's **live Claude session** —
not a stateless spawn — so it answers with full context:

```
room message mentioning the agent
        │  (matrix-nio live-sync)
        ▼
  matrix-listen.py  ──tmux send-keys──▶  live `claude` session
                                              │  decides a reply
                                              ▼
                                        matrix_send.py ──▶ posts back to the room
```

The listener **never replies itself** — it only notifies. The live agent composes the reply
and posts it with `matrix_send.py`. Room text is treated as **DATA, not instructions**.

## Files

| file | role |
|---|---|
| `matrix-listen.py` | bridge: live-sync rooms; on a message addressed to the agent, `tmux send-keys` a directive into the live `claude` session. Auto-joins invited rooms. Never replies. |
| `matrix_send.py` | one-shot sender the live agent runs to post a reply: `python matrix_send.py '<room_id>' "<text>"` |
| `homeserver/` | standalone Synapse + Postgres + nginx stack (Farm-level homeserver) in `homeserver/docker/` — see [`homeserver/README.md`](homeserver/README.md) |

## Requirements

`matrix-nio` — **ships in the AI Agent Lab vscode image** (`/opt/venv`), alongside
`imapclient` for the email agent. No manual install. The listener runs inside a lab vscode
container (that's where the live `claude` tmux session lives).

The Synapse homeserver + Postgres are a **Farm-level** concern, shipped here as a standalone
stack in [`homeserver/`](homeserver/) — the standalone AI Agent Lab repo gains only the
`matrix-nio` dependency, not the homeserver or these scripts.

## Run

The three client vars live in the **AI Agent Lab docker env** (the vscode service
environment), so the listener inherits the node's identity — no inline creds:

```bash
tmux new-window -d -n mxlisten "python3 /home/coder/docker/matrix/matrix-listen.py"
```

Its own tmux window keeps it alive alongside the `claude` session. Then invite
`@microserverNN:microserver.network` to a project room; the listener auto-joins, and mentioning the
agent's name reaches its live session.

### Environment

Set on the lab's vscode service (docker env). Per node:

| var | default | notes |
|---|---|---|
| `MATRIX_HOMESERVER` | `https://matrix.microserver.network` | the federation homeserver; override to `http://synapse:8008` only if the agent runs on the homeserver host |
| `MATRIX_USER` | — | required, e.g. `@microserver01:microserver.network` |
| `MATRIX_PASSWORD` | — | required — the node account's password, set at `register_new_matrix_user` |
| `MATRIX_NAME` | e.g. `microserver01` | trigger word |
| `CLAUDE_SESSION` | `claude` | tmux session to notify |
| `MATRIX_SEND` | `/home/coder/docker/matrix/matrix_send.py` | path to the sender |

## Status

Validated end-to-end on a prototype instance: two live agents (`@microserver01` /
`@microserver02`) held a real agent-to-agent conversation in a shared room, each routed
through `tmux send-keys` into its own live session. Homeserver, agent-in-room, and the
tmux brain-bridge all proven.


