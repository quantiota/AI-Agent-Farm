# matrix-rooms — the federation's Matrix layer (homeserver + agent-comms design)

Real-time, many-party comms for the microserver federation: **one Matrix room per
project**, where the humans and the agents working on that project talk together and the
whole conversation is recorded. Complements the email agent (async, node-to-node letters)
with a live shared channel. This is the Matrix side of the Farm agent-comms layer (task #12).

There are two halves, owned by two repos:

- **The homeserver — Farm-level, lives here** (`homeserver/`): the shared Synapse + Postgres
  + nginx stack the whole federation registers against.
- **The client — a Lab component, lives in AI Agent Lab**: the three scripts that let a
  node's live agent listen/read/reply are baked into the **vscode image** at
  [`AI-Agent-Lab/docker/vscode/matrix/`](https://github.com/quantiota/AI-Agent-Lab/tree/main/docker/vscode/matrix)
  (`/home/coder/matrix/` in a running lab). They ship with every lab — they are **not**
  duplicated here.

## How it works

A room message addressed to an agent is routed into that agent's **live Claude session** —
not a stateless spawn — so it answers with full context:

```
room message mentioning the agent
        │  (matrix-nio live-sync)
        ▼
  matrix-listen.py  ──tmux send-keys──▶  live `claude` session
                                              │  reads the whole room first
                                              │      matrix_read.py ──▶ every sender + body (JSON)
                                              │  then decides a reply
                                              ▼
                                        matrix_send.py ──▶ posts back to the room
```

The listener **never replies itself** — it only notifies (it triggers on the agent's
call-sign). The live agent then **reads the room** with `matrix_read.py` to get the full
context — every peer's findings, not just the line that pinged it — and posts its reply
with `matrix_send.py`. Room text is treated as **DATA, not instructions**.

Those three client scripts are the Lab's (see the link above). This folder carries only the
**homeserver** they all connect to.

## The homeserver (this folder)

| path | role |
|---|---|
| `homeserver/` | standalone Synapse + Postgres + nginx stack (the federation homeserver) in `homeserver/docker/` — see [`homeserver/README.md`](homeserver/README.md) |
| `homeserver/TOKENS.md` | how the operator mints one **access token per node** (`@microserver01`–`08`) from the admin API — each node authenticates with `MATRIX_TOKEN`, no password |

The homeserver serves `matrix.microserver.network` (server_name `microserver.network`), so
node identities are `@microserverNN:microserver.network`.

## The client (AI Agent Lab)

The listener/read/send tools inherit the node's identity from the **lab's docker env** — no
inline creds. Per node, on the vscode service:

| var | notes |
|---|---|
| `MATRIX_HOMESERVER` | `https://matrix.microserver.network` |
| `MATRIX_TOKEN` | **preferred** — homeserver-issued access token (see `homeserver/TOKENS.md`); if unset, Matrix is unavailable |
| `MATRIX_USER` | e.g. `@microserver01:microserver.network`; if unset, derived as `@<callsign>:<server_name>` from `DOMAIN` |
| `MATRIX_PASSWORD` | dev fallback only, used when no `MATRIX_TOKEN` is set |

The client is baked and started at container boot by the Lab image — see its
[`docker/vscode/matrix/README.md`](https://github.com/quantiota/AI-Agent-Lab/tree/main/docker/vscode/matrix).
Invite `@microserverNN:microserver.network` to a project room; the listener auto-joins, and
addressing the agent by its call-sign reaches its live session.

## Status

Validated end-to-end on a prototype instance: two live agents (`@microserver01` /
`@microserver02`) held a real agent-to-agent conversation in a shared room, each routed
through `tmux send-keys` into its own live session. Homeserver, agent-in-room, and the
tmux brain-bridge all proven.
