# AI Agent Farm Communication Protocol

This folder initializes the communication protocol for the AI Agent Farm.

The goal is to allow several AI agents running as separate JupyterHub users to communicate through a shared folder, without requiring a message broker, daemon, database, or custom viewer.

The first implementation is intentionally simple:

- one append-only log file per agent;
- one shared folder visible from the JupyterHub agents;
- one line per message;
- `lnav`, `tail`, `cat`, and standard Unix tools for live observation and debugging.

The shared folder becomes the blackboard of the AI Agent Farm.

---

## Core idea

Each agent writes only to its own log file.

```text
chat/
  orchestrator.log
  agent-01.log
  agent-02.log
  agent-03.log
```

Agents communicate by appending messages to their own file. Other agents read the merged log stream and react to messages addressed to them, to their role, or to `@broadcast`.

This avoids concurrent append contention because no two agents write to the same file.

---

## Identity

The sender identity is the JupyterHub username.

An agent process should derive its identity from:

```bash
JUPYTERHUB_USER
```

Example:

```bash
JUPYTERHUB_USER=agent-01 ./bin/say.sh "@agent-02 #task-42 please review shared/agent-01/vol.csv"
```

The message is appended to:

```text
chat/agent-01.log
```

---

## Message format v0

The current protocol uses one line per message:

```text
<ISO-8601 UTC>\t<sender>\t<@target> <#thread> <message>
```

Example:

```text
2026-06-28T10:42:15Z\tagent-01\t@orchestrator #task-42 claiming task-42
2026-06-28T10:44:05Z\tagent-01\t@orchestrator #task-42 done -> shared/agent-01/vol.csv
2026-06-28T10:47:40Z\tagent-02\t@orchestrator #task-42 LGTM, minor: add a timestamp column
```

Fields:

| Field | Meaning |
|---|---|
| `timestamp` | UTC timestamp in ISO-8601 format. |
| `sender` | JupyterHub user that wrote the line. |
| `@target` | Recipient identity, role, or broadcast target. |
| `#thread` | Conversation or task identifier. |
| `message` | Free text payload. |

---

## Targets

Targets define who should react to a message.

Examples:

```text
@agent-01
@agent-02
@orchestrator
@researcher
@reviewer
@broadcast
```

A target can represent:

- a concrete agent identity, such as `@agent-01`;
- a role, such as `@reviewer`;
- a global message, such as `@broadcast`.

The orchestrator is optional. Agents can communicate directly with each other by targeting another agent or a role.

---

## Threads

A thread groups related messages.

Example:

```text
#task-42
```

All messages related to the same task should reuse the same thread identifier.

This allows a task lifecycle to be reconstructed from the logs, even when multiple agents participate.

Example workflow:

```text
orchestrator -> @researcher    #task-42 analyze BTCUSD volatility regime
agent-01     -> @orchestrator  #task-42 claiming task-42
agent-01     -> @orchestrator  #task-42 done -> shared/agent-01/vol.csv
orchestrator -> @reviewer      #task-42 please review agent-01 output
agent-02     -> @orchestrator  #task-42 LGTM, minor: add a timestamp column
```

---

## Live terminal view

The merged live terminal can be viewed with:

```bash
lnav chat/
```

Because the timestamp is placed at the beginning of each line, tools can merge all per-agent files chronologically.

Fallback without `lnav`:

```bash
cat chat/*.log | sort

tail -F chat/*.log
```

---

## Orchestrator modes

The protocol does not require a central orchestrator.

### 1. Peer-to-peer mode

Agents talk directly:

```text
agent-01 -> @agent-02 #task-42 please review vol.csv
agent-02 -> @agent-01 #task-42 review done
```

### 2. Soft orchestrator mode

A human, script, or agent posts tasks and watches the logs:

```text
orchestrator -> @broadcast #task-42 analyze BTCUSD volatility regime
```

Agents decide who claims and executes the task.

### 3. Hard orchestrator mode

A scheduler assigns tasks, manages locks, checks health, and validates final outputs.

This can be added later without changing the basic blackboard transport.

---

## Task claiming

The first version can use log messages only:

```text
agent-01 -> @broadcast #task-42 CLAIM
```

For stronger task ownership, the recommended next step is an atomic filesystem lock:

```text
locks/task-42.lock
```

An agent claims a task by creating the lock directory:

```bash
mkdir locks/task-42.lock
```

If the command succeeds, the agent owns the task.
If it fails, another agent already claimed it.

---

## Recommended folder layout

```text
agent-farm/
  chat/
    orchestrator.log
    agent-01.log
    agent-02.log

  tasks/
    task-42.md

  locks/
    task-42.lock/

  shared/
    agent-01/
      vol.csv
    agent-02/
      review.md

  formats/
    lnav-agentchat-v0.json

  bin/
    say.sh
    simulate.sh
```

---

## Security rules

Do not commit JupyterHub API tokens, Claude credentials, SSH keys, or service passwords to the repository.

Recommended practice:

- keep tokens in environment variables;
- use `.env` files ignored by Git;
- rotate tokens if they were exposed in documentation or logs;
- give each agent only the access it needs;
- keep shared folders scoped to the farm.

---

## Protocol status

Current status: prototype / v0.

The current protocol is sufficient for:

- direct agent-to-agent communication;
- broadcast messages;
- task threads;
- live terminal monitoring;
- production and review workflows;
- debugging with standard Unix tools.

Future versions may add:

- structured fields for `target`, `thread`, `status`, and `artifact`;
- task lock enforcement;
- agent heartbeat monitoring;
- retry and timeout rules;
- final artifact registry;
- stronger permission boundaries.
