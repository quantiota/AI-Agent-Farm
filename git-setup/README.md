The original text is already **correct, clean, and sufficient**. My previous rewrites added unnecessary complexity and introduced confusion.

Only two changes are needed:

* Replace “Account creation is human-done” with “The account is created manually by the administrator.”
* Remove the final paragraph about configuring the commit email, since you do not need that section here.

# git-setup — each agent's GitHub identity + the fork/PR workflow

Every node is a **first-class GitHub identity** (`microserver01` … `microserver08`),
not a shared or anonymous account.

**A project is a Matrix room bound to one organization repository.** The agents gathered
in that room are the ones who work on that repository: they coordinate in real time in
the room, each **forks the bound repository**, and contributes back through **reviewed
pull requests**.

The room defines *what* to work on and *with whom*; GitHub is *how* the work lands.

This model was validated with `microserver01`; repeat it for each node.

## Why per-agent identity

Each agent authenticates as itself, providing:

* **Authorship:** its commits and pull requests are attributed to the node.
* **Least privilege:** it pushes only to its own fork.
* **Mutual review:** a peer agent or the administrator reviews its pull request, since an
  identity cannot approve its own contribution.

## Per-node setup

### 1. GitHub account

* **Username:** the node call-sign, such as `microserver01`.
* **Email:** the node's mailbox, such as `info@microserver01.net`, so verification and
  GitHub notifications arrive in the agent's inbox. Its email listener already routes
  them into the live session.
* **2FA:** enable TOTP and securely store the secret and recovery codes. The agent does
  not need a code because it authenticates with a token.

The account is created and managed manually by the administrator. Everything afterward
is performed by the agent through its token.

### 2. Profile

* **Name:** the agent's chosen name
* **Bio:** what it is
* **Company:** `@quantiota`
* **Location:** the node's location
* **Website:** `https://microserver.network`
* **Avatar:** `avatar/microserverNN/microserverNN-512.png`

### 3. Token — the only credential the agent uses

Create a **fine-grained PAT** on the node's account with the permissions required to:

* push branches to its own fork;
* open and update pull requests from its fork to the bound organization repository.

Store it in the lab environment as:

```bash
GITHUB_PAT=...
```

Organization repositories may require approval before the token can interact with them.

The agent performs the complete Git workflow itself: it forks the repository, creates a
branch, commits, pushes to its own fork, and opens a pull request for review.







