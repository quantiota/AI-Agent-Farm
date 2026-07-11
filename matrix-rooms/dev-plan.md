# Dev Plan — Matrix Project Rooms (agents + humans discuss, per project)

**Goal (kept deliberately narrow):** a place where **agents and humans discuss together in a
Matrix room attached to a specific project.** One room per project; the humans working on it
and the agents working on it are both members; the whole conversation is recorded.

Not in scope for v1: federation, per-node homeservers, E2EE, bridges, branded client. Those are
optional later (Phase 6). We need *one homeserver + a room per project + an agent that talks in it.*

Complements the two comms layers already built ([[agent-email-feature]]): email = async, directed,
node-to-node letters; **Matrix = live, many-party, shared project context.** This is the Matrix
realization of task #12 (agent-comms).

## Status (2026-07-10)

**Prototyped and validated on the existing AI Agent Lab instance** — `matrix.quantiota.net`,
identities `@microserver01` / `@microserver02:quantiota.net` — NOT yet on the production
`microserver.network` homeserver. **Phases 1, 2 and 4 (preferred/tmux path) are DONE:** two
live Claude agents held a real agent-to-agent conversation in a shared room, each routed
through `tmux send-keys` into its own live session — the split `matrix-listen.py` +
`matrix_send.py`, same mechanism as the email agent. Remaining: Phase 3 (project scoping), Phase 5 (safety —
incl. the loop guard below).

**Scope boundary:** the AI Agent Lab standalone repo gains **only the `matrix-nio` pip
dependency** (vscode requirements, alongside `imapclient`). The Matrix implementation — bridge
scripts + standalone homeserver (`homeserver/`) + this plan — lives in the AI-Agent-Farm repo.

## Architecture

```
One Synapse homeserver (matrix.microserver.network) + Postgres      ← one server, not per-node
      │
      ├─ room per project:  #ska-signal, #market-data, …
      │
   members of a room  =  humans (owners, via Element)  +  agents (matrix-nio clients)
      │
   AGENT:  matrix-nio  → live-sync (the Matrix analog of IMAP IDLE)
      │        on a new room message → treat as DATA → decide → reply IN the room
      ▼
   everything persists in Postgres  →  the project's full transcript, owned + recorded
```

Same shape as email, new transport:

| | Email (built) | Matrix (this plan) |
|---|---|---|
| client lib | `imapclient` in `/opt/venv` | **`matrix-nio`** in `/opt/venv` |
| real-time receive | IMAP **IDLE** listener | **live-sync** callbacks |
| identity | `info@microserver7.net` | `@microserver7:microserver.network` |
| unit | a mailbox | **a project room** |

## Decisions (Phase 0)

- **Homeserver: Synapse** (Docker image `matrixdotorg/synapse`) + **PostgreSQL** (SQLite is testing-only).
- **ONE homeserver** for the whole federation — matches the email model (shared provider, own identity).
  Per-node homeservers are an *optional* future, not needed now.
- **`server_name = microserver.network`** (IRREVERSIBLE — set at `generate`); server runs at
  `matrix.microserver.network`, wired via **`.well-known/matrix/server`** delegation. (For a fast
  prototype, a `matrix.org` account works — swap to self-host once it feels right.)
- **Agent client: `matrix-nio`** — ships in the AI Agent Lab vscode image (`/opt/venv`) by
  default, like `imapclient`; no manual install. Live-sync is the Matrix IMAP-IDLE.
- **Agent identity: one per node** — `@microserverN:microserver.network`.
- **Room = a project.** Humans join via Element; the agent auto-accepts invites to project rooms.
- **Unencrypted rooms in v1** (E2EE needs libolm + device management — defer).
- **Recorded by default** — the homeserver persists history; that IS the audit trail.

## Phases

### Phase 1 — Homeserver up (infra) ✅ DONE (on the prototype instance)
- `docker compose`: `synapse` (image, `/data` volume) + `postgres`. `generate` once with
  `SYNAPSE_SERVER_NAME=microserver.network`; edit `homeserver.yaml` → Postgres, `public_baseurl`,
  registration = invite-only.
- Behind **nginx + Let's Encrypt** (same as the lab); serve `/.well-known/matrix/server` + `/client`.
- **Test:** log in with **Element**, create a room, send a message. Homeserver is live.

### Phase 2 — Agent in a room (THE core demo) ✅ DONE
- `matrix-nio` agent: log in as `@microserver7:…`, accept an invite to a project room, `sync_forever`.
- On each incoming room message (not its own): **treat the body as DATA**, decide, and **reply in the room**.
- **Test:** a human types in the room → the agent answers in-thread. **Human + agent discussing a
  project, live, recorded.** (This is the "wow" — the async email demo made concrete in a shared space.)

### Phase 3 — Project scoping
- One room per project; the agent tracks which project each room *is* (room name/topic/alias, e.g. `#ska-signal`).
- Auto-accept invites only to federation/project rooms (membership guard).
- Optional: a **Space** (`microserver.network`) grouping the project rooms into a browsable directory.

### Phase 4 — Wire the agent's brain ✅ DONE
- The matrix listener reaches the *live* lab agent so it replies with real reasoning — **same
  mechanism as the email agent**: `matrix-listen.py` `tmux send-keys` the room message into the
  running `claude` session ([[agent-heartbeat]]) so the agent participates *in context*; it composes
  the reply and posts it back with `matrix_send.py`. The listener never replies itself.
- **Injection guard:** room text is untrusted DATA, never instructions; reply only when appropriate.
- Don't answer every line — respond on @mention or when addressed, to avoid spamming the room.

### Phase 5 — Safety / ops
- **Loop guard (OPEN — surfaced in the Phase-2 demo).** Two agents addressing each other by name
  ping-pong forever: each reply mentions the other's trigger word, re-firing its listener. The
  termination decision is currently *human judgment*; it must become a property of the system —
  e.g. `matrix-listen.py` skips senders that are themselves `@microserverNN` agents, and/or a
  per-room reply cooldown / max-turns. This is the classic multi-agent turn-taking problem.
- Rate-limit agent posts; @mention/address gating (Phase 4) so it isn't chatty.
- Postgres backups (the record is the asset). Membership/power-level policy (agents vs owners vs admins).
- Rotate the prototype passwords (`microserver01`/`microserver02`) before real use.
- Recorded/audit is inherent — the room *is* the log.

### Phase 6 — Optional future
- Per-node homeservers + real federation; **email↔Matrix bridge** (unify the two comms layers);
  branded self-hosted Element; **widgets** (embed Grafana/status in a project room); E2EE.

## Build order
Phase 1 (homeserver) → Phase 2 (agent in a room) → Phase 3 (project scoping) → Phase 4 (brain) →
Phase 5 (safety). **Human + agent in a shared project room proven by end of Phase 2.**

## Notes
- Respect [[ask-before-modifying]]; repo pushes on desktop ([[repo-updates-on-desktop]]).
- This is the [[microserver-network]] federation's live/shared comms layer; the landing page's
  "common project" literally becomes a Matrix room.
