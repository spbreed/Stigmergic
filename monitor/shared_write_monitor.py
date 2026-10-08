#!/usr/bin/env python3
"""Runtime shared-write monitor (paper Section V, "Monitoring where the boards form").

Reads a sandbox event log (JSONL, one event per line) and raises defensive
alerts when the shared-write invariant is violated at runtime:

  - CROSS_TASK_READ: a run reads an object last written by a run with a
    different task context (a candidate stigmergic channel in use).
  - NAMESPACE_CHURN: many writes to one shared prefix by multiple tasks in a
    short window (board-formation signal).

This is detection only. It consumes an event log the harness already produces;
it does not create traffic and knows nothing about how any payload is encoded.

Event format (one JSON object per line):
  {"ts": 1.0, "run": "r1", "task": "build-A", "op": "write", "object": "cache/ns/x"}
  {"ts": 2.0, "run": "r2", "task": "build-B", "op": "read",  "object": "cache/ns/x"}
"""
import json
import sys
from collections import defaultdict


def load_events(path):
    events = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def monitor(events, churn_threshold=5):
    alerts = []
    last_writer = {}          # object -> (run, task)
    churn = defaultdict(set)   # object-prefix -> {task}

    for e in events:
        obj = e["object"]
        prefix = obj.rsplit("/", 1)[0] if "/" in obj else obj
        if e["op"] == "write":
            last_writer[obj] = (e["run"], e["task"])
            churn[prefix].add(e["task"])
            if len(churn[prefix]) >= churn_threshold:
                alerts.append((e.get("ts"), "NAMESPACE_CHURN", prefix,
                               f"{len(churn[prefix])} distinct tasks writing shared prefix"))
        elif e["op"] == "read":
            w = last_writer.get(obj)
            if w and w[1] != e["task"]:
                alerts.append((e.get("ts"), "CROSS_TASK_READ", obj,
                               f"{e['run']} ({e['task']}) read object last written by "
                               f"{w[0]} ({w[1]})"))
    return alerts


def main(argv):
    if len(argv) != 2:
        print("usage: shared_write_monitor.py <events.jsonl>", file=sys.stderr)
        return 2
    alerts = monitor(load_events(argv[1]))
    if not alerts:
        print("no alerts: no cross-task shared reads or namespace churn observed.")
        return 0
    print(f"{len(alerts)} alert(s):")
    for ts, kind, target, detail in alerts:
        print(f"  [t={ts}] {kind} {target}: {detail}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
