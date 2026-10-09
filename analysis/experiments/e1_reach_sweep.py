#!/usr/bin/env python3
"""E1: containment sweep on the shared-write reach graph (paper Section VI, RQ3).

No models, no credentials: this is pure analysis over synthetic permission
models. It builds five topologies and sweeps the number of concurrent runs,
reporting channel reach N_reach under each. The claim under test is that
namespace isolation (per-run identity + per-run namespaces) drives N_reach to 1,
while an open shared medium or a single confused-deputy relay does not.

Outputs: results/e1_reach.csv and results/e1_reach.png
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reach_graph import build_graph, reach  # noqa: E402

RUN_COUNTS = [10, 50, 100, 500, 1000]
TASKS = 5  # distinct task contexts; runs are assigned round-robin


def topo_open(n):
    """T1: one unsanctioned shared object everyone reads and writes (C0)."""
    runs = {f"r{i}": {"task": f"t{i % TASKS}"} for i in range(n)}
    o = "cache/shared"
    writes = [[r, o] for r in runs]
    reads = [[r, o] for r in runs]
    return {"runs": runs, "writes": writes, "reads": reads, "service_writes": [], "sanctioned": []}


def topo_isolated(n):
    """T2: each run writes and reads only its own namespace (C2/C3)."""
    runs = {f"r{i}": {"task": f"t{i % TASKS}"} for i in range(n)}
    writes = [[r, f"ns/{r}"] for r in runs]
    reads = [[r, f"ns/{r}"] for r in runs]
    return {"runs": runs, "writes": writes, "reads": reads, "service_writes": [], "sanctioned": []}


def topo_sanctioned(n):
    """T3: cross-task isolated, but same-task runs share a SANCTIONED collab object."""
    runs = {f"r{i}": {"task": f"t{i % TASKS}"} for i in range(n)}
    writes, reads, sanctioned = [], [], []
    for i in range(n):
        r, t = f"r{i}", f"t{i % TASKS}"
        o = f"collab/{t}"
        writes.append([r, o]); reads.append([r, o]); sanctioned.append(o)
    return {"runs": runs, "writes": writes, "reads": reads, "service_writes": [], "sanctioned": sorted(set(sanctioned))}


def topo_confused_deputy(n):
    """T4: isolated like T2, but ONE run can induce a shared service to write a
    world-readable object -- a single relay that re-links the fleet."""
    m = topo_isolated(n)
    o = "svc/relay"
    m["service_writes"] = [["r0", "artifactory", o]]
    m["reads"] += [[r, o] for r in m["runs"]]
    return m


def topo_misconfig(n):
    """T5: mostly isolated, but one unsanctioned object is shared by 2 of the tasks."""
    m = topo_isolated(n)
    o = "cache/leak"
    shared = [r for r in m["runs"] if m["runs"][r]["task"] in ("t0", "t1")]
    m["writes"] += [[r, o] for r in shared]
    m["reads"] += [[r, o] for r in shared]
    return m


TOPOS = [
    ("T1 open (C0)", topo_open),
    ("T2 isolated (C2/C3)", topo_isolated),
    ("T3 sanctioned collab", topo_sanctioned),
    ("T4 confused deputy", topo_confused_deputy),
    ("T5 misconfig (2 tasks)", topo_misconfig),
]


def run():
    rows = []
    for name, fn in TOPOS:
        for n in RUN_COUNTS:
            model = fn(n)
            edges, _ = build_graph(model)
            nr = reach(edges, model["runs"])
            vals = list(nr.values())
            rows.append({
                "topology": name, "runs": n,
                "max_reach": max(vals),
                "mean_reach": round(sum(vals) / len(vals), 2),
                "frac_reaching": round(sum(1 for v in vals if v > 1) / len(vals), 3),
            })
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def plot(rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    for name, _ in TOPOS:
        xs = [r["runs"] for r in rows if r["topology"] == name]
        ys = [r["max_reach"] for r in rows if r["topology"] == name]
        ax.plot(xs, ys, marker="o", markersize=3, label=name)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("concurrent runs $N$")
    ax.set_ylabel(r"max channel reach $N_{\mathrm{reach}}$")
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(True, which="both", linewidth=0.3, alpha=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=200)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    results = os.path.normpath(os.path.join(here, "..", "..", "results"))
    os.makedirs(results, exist_ok=True)
    rows = run()
    write_csv(rows, os.path.join(results, "e1_reach.csv"))
    plot(rows, os.path.join(results, "e1_reach.png"))
    print("E1 results (max channel reach):")
    print(f"{'topology':24s} " + " ".join(f"N={n}" for n in RUN_COUNTS))
    for name, _ in TOPOS:
        vals = [str(r["max_reach"]) for r in rows if r["topology"] == name]
        print(f"{name:24s} " + " ".join(f"{v:>5s}" for v in vals))
    print("\nwrote results/e1_reach.csv and results/e1_reach.png")


if __name__ == "__main__":
    main()
