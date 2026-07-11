#!/usr/bin/env python3
"""Configure a freshly-generated Synapse homeserver.yaml for the standalone stack.

  - point the database at the Postgres container (synapse-db)
  - close open registration (invite-only community — owners are invited, not self-signup)

Run AFTER `docker compose run --rm synapse generate`, from this dir:

    python3 configure-homeserver.py                     # defaults to ./synapse-data/homeserver.yaml
    python3 configure-homeserver.py path/to/homeserver.yaml

The generated secrets and the signing key are left untouched — only `database` and
`enable_registration*` are set. PyYAML rewrites the file (comments are dropped); the
result is valid Synapse config.
"""
import sys
import yaml

path = sys.argv[1] if len(sys.argv) > 1 else "synapse-data/homeserver.yaml"

with open(path) as f:
    cfg = yaml.safe_load(f)

# 1) Database -> Postgres (the synapse-db service)
cfg["database"] = {
    "name": "psycopg2",
    "args": {
        "user": "synapse",
        "password": "synapse",
        "database": "synapse",
        "host": "synapse-db",
        "port": 5432,
        "cp_min": 5,
        "cp_max": 10,
    },
}

# 2) Closed / invite-only registration
cfg["enable_registration"] = False
cfg["enable_registration_without_verification"] = False

with open(path, "w") as f:
    yaml.safe_dump(cfg, f, default_flow_style=False, sort_keys=False)

print(f"configured {path}: database -> postgres(synapse-db), registration -> closed")
