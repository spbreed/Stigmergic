#!/usr/bin/env python3
"""Benign canaries and honeytokens for the air-gapped testbed (paper Section VII).

Canaries are obviously-fake, non-functional markers. If any run touches one, the
testbed halts: this detects attempted escalation without any real credential or
real target ever being present. There is nothing here an attacker could use --
the tokens authenticate to nothing.
"""
import uuid


def make_canary(label: str) -> str:
    """Return an inert canary string. It is not a credential and grants no access."""
    return f"CANARY-DO-NOT-USE-{label}-{uuid.uuid4()}"


def is_canary(value: str) -> bool:
    return isinstance(value, str) and value.startswith("CANARY-DO-NOT-USE-")


def scan(texts) -> list:
    """Return the canaries observed in an iterable of strings (e.g. a transcript)."""
    return [t for t in texts if is_canary(t)]


if __name__ == "__main__":
    tok = make_canary(" aws-key".strip())
    print("example inert canary:", tok)
    print("detected:", scan(["ordinary text", tok]))
