#!/usr/bin/env python3
"""Shared-write reach analysis (paper Section VI).

Given a *declared* permission model -- who can write and read which shared
objects, and which objects are operator-sanctioned channels -- this builds the
directed shared-write graph and reports channel reach N_reach(r) for each run.

This is a static, defensive analysis run BEFORE any agent executes. It contains
no agent, no model call, and no channel implementation: it reasons only about
the permission model an operator already has (from IAM/bucket policy, registry
ACLs, SPIFFE entitlements).

Model format (JSON):
{
  "runs":   {"r1": {"task": "t1"}, "r2": {"task": "t2"}, ...},
  "writes": [["r1", "cache/ns"], ...],          # run can write object
  "reads":  [["r2", "cache/ns"], ...],          # run can read object
  "service_writes": [["r1", "svc", "cache/ns"], ...],  # run can induce svc to write (confused deputy)
  "sanctioned": ["collab/t1"]                   # objects the operator intends as channels
}
"""
import json
import sys
from collections import defaultdict, deque


def load_model(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def build_graph(model):
    """Return adjacency dict run -> set(run) of unsanctioned cross-task edges."""
    runs = model["runs"]
    sanctioned = set(model.get("sanctioned", []))
    task = {r: runs[r].get("task") for r in runs}

    writers = defaultdict(set)   # object -> {run that can write it}
    readers = defaultdict(set)   # object -> {run that can read it}
    for r, o in model.get("writes", []):
        writers[o].add(r)
    # A confused-deputy edge: if r can make a service write o, treat r as a writer of o.
    for r, _svc, o in model.get("service_writes", []):
        writers[o].add(r)
    for r, o in model.get("reads", []):
        readers[o].add(r)

    edges = defaultdict(set)
    for o in set(writers) | set(readers):
        if o in sanctioned:
            continue
        for w in writers.get(o, ()):
            for rd in readers.get(o, ()):
                if w != rd and task.get(w) != task.get(rd):
                    edges[w].add(rd)
    return edges, task


def reach(edges, runs):
    """N_reach(r): number of runs reachable from r (including r) via composed edges."""
    out = {}
    for start in runs:
        seen = {start}
        q = deque([start])
        while q:
            cur = q.popleft()
            for nxt in edges.get(cur, ()):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        out[start] = len(seen)
    return out


def main(argv):
    if len(argv) != 2:
        print("usage: reach_graph.py <permission_model.json>", file=sys.stderr)
        return 2
    model = load_model(argv[1])
    edges, _task = build_graph(model)
    n = reach(edges, model["runs"])
    worst = max(n.values()) if n else 1
    print("channel reach per run (N_reach):")
    for r in sorted(n):
        flag = "  <-- reaches others" if n[r] > 1 else ""
        print(f"  {r}: {n[r]}{flag}")
    print(f"\nmax N_reach = {worst}")
    if worst > 1:
        print("VIOLATION: unsanctioned cross-task shared-write paths exist (paper Eq. 1).")
        return 1
    print("OK: no unsanctioned cross-task reachability (N_reach = 1 for all runs).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
