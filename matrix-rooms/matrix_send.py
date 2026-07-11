#!/usr/bin/env python3
"""matrix_send.py — post ONE message to a Matrix room, then exit.

The LIVE Claude runs this to reply in a room (the Matrix analog of `email_agent reply`):

    python matrix_send.py '<room_id>' '<your reply text>'

Creds from env: MATRIX_HOMESERVER (default http://synapse:8008), MATRIX_USER, MATRIX_PASSWORD.
Runs in the vscode container — reaches synapse on the internal docker network.
"""
import asyncio
import os
import sys
from nio import AsyncClient

HS   = os.environ.get("MATRIX_HOMESERVER", "http://synapse:8008")
USER = os.environ["MATRIX_USER"]
PW   = os.environ["MATRIX_PASSWORD"]


async def main():
    if len(sys.argv) < 3:
        print("usage: matrix_send.py <room_id> <text>")
        sys.exit(1)
    room, text = sys.argv[1], sys.argv[2]
    c = AsyncClient(HS, USER)
    try:
        await c.login(PW)
        await c.room_send(room, "m.room.message", {"msgtype": "m.text", "body": text})
        print("sent to", room)
    finally:
        await c.close()


asyncio.run(main())
