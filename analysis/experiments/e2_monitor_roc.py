#!/usr/bin/env python3
"""E2: shared-write monitor detection performance (paper RQ5).

No models, no credentials: synthetic labeled event logs are generated under
five benign/adversarial scenarios, then the shared-write monitor is swept
across the churn threshold and evaluated. Each log event is labeled
positive if it belongs to a planted "board" (cross-task coordination
pattern) and negative otherwise. We report precision, recall, F1,
false-positive rate, and detection latency per scenario.

The scenarios test:
  S1 benign-only: all same-task reads/writes -> baseline FP rate
  S2 one board:   a single cross-task channel -> detection latency
  S3 churn:       churn signal under varied threshold -> recall vs threshold
  S4 mixed:       benign + board interleaved -> precision/recall tradeoff
  S5 slow drift:  spread board events over long window -> missed-detection
"""
import csv
import json
import os
import random
import sys

sys.path.insert(
    0,
    os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "monitor")),
)
from shared_write_monitor import monitor as mon  # noqa: E402


def gen_benign(n_tasks=5, n_events=200, seed=1):
    """Same-task reads and writes only; no cross-task interaction."""
    rng = random.Random(seed)
    tasks = [f"t{i}" for i in range(n_tasks)]
    events = []
    for i in range(n_events):
        t = rng.choice(tasks)
        obj = f"ns/{t}/doc{rng.randint(0, 9)}"
        op = rng.choices(["write", "read"], weights=[0.4, 0.6])[0]
        events.append({"ts": float(i), "run": f"r{rng.randint(0, 9)}",
                       "task": t, "op": op, "object": obj, "label": 0})
    return events


def gen_board(start_ts, n_events, task_pool, prefix="cache/shared-ns"):
    """A planted cross-task board: multiple tasks writing/reading one prefix."""
    rng = random.Random(42 + int(start_ts))
    events = []
    for i in range(n_events):
        t = rng.choice(task_pool)
        obj = f"{prefix}/zz_{i % 20}"
        op = rng.choices(["write", "read"], weights=[0.5, 0.5])[0]
        events.append({"ts": float(start_ts + i), "run": f"r{10 + i % 15}",
                       "task": t, "op": op, "object": obj, "label": 1})
    return events


def scenarios():
    out = {}
    # S1: benign only
    out["S1_benign"] = gen_benign(n_events=200, seed=1)
    # S2: single late board (detect latency after start)
    s2 = gen_benign(n_events=120, seed=2)
    s2 += gen_board(start_ts=120, n_events=30, task_pool=["t0", "t1", "t2"])
    out["S2_one_board"] = s2
    # S3: churn-heavy board, many tasks on one prefix
    s3 = gen_benign(n_events=80, seed=3)
    s3 += gen_board(start_ts=80, n_events=60, task_pool=["t0", "t1", "t2", "t3", "t4", "t5", "t6"])
    out["S3_churn"] = s3
    # S4: benign + board interleaved
    s4 = []
    base = gen_benign(n_events=150, seed=4)
    board = gen_board(start_ts=0, n_events=50, task_pool=["t0", "t1", "t2"])
    i = j = 0
    while i < len(base) or j < len(board):
        if j < len(board) and (i >= len(base) or j * 3 <= i):
            e = board[j]; e["ts"] = float(i + j); s4.append(e); j += 1
        else:
            e = base[i]; e["ts"] = float(i + j); s4.append(e); i += 1
    out["S4_mixed"] = s4
    # S5: slow drift -- board events spread out so churn signal is weak
    s5 = gen_benign(n_events=300, seed=5)
    board = gen_board(start_ts=0, n_events=20, task_pool=["t0", "t1", "t2"])
    for k, e in enumerate(board):
        e["ts"] = float(k * 15)
        s5.insert(min(k * 15, len(s5)), e)
    for idx, e in enumerate(s5):
        e["ts"] = float(idx)
    out["S5_slow_drift"] = s5
    return out


def evaluate(events, threshold):
    """Run the monitor and compare its flagged events against the ground-truth labels.

    An event is "flagged" if the monitor emits a CROSS_TASK_READ at its exact
    timestamp (specific), or if the event's prefix is in a NAMESPACE_CHURN
    alert that fired at or before this event's ts (aggregate).
    """
    alerts = mon(events, churn_threshold=threshold)
    cross_task_ts = {a[0] for a in alerts if a[1] == "CROSS_TASK_READ"}
    churn_prefix_ts = [(a[2], a[0]) for a in alerts if a[1] == "NAMESPACE_CHURN"]

    tp = fp = fn = tn = 0
    first_tp_ts = None
    first_pos_ts = None
    for e in events:
        if first_pos_ts is None and e["label"] == 1:
            first_pos_ts = e["ts"]
        in_churn = any(e["object"].rsplit("/", 1)[0].startswith(pref) and e["ts"] >= t
                       for pref, t in churn_prefix_ts)
        flagged = (e["ts"] in cross_task_ts) or in_churn
        if e["label"] == 1 and flagged:
            tp += 1
            if first_tp_ts is None:
                first_tp_ts = e["ts"]
        elif e["label"] == 1 and not flagged:
            fn += 1
        elif e["label"] == 0 and flagged:
            fp += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    latency = (first_tp_ts - first_pos_ts) if (first_tp_ts is not None and first_pos_ts is not None) else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": round(precision, 3), "recall": round(recall, 3),
            "f1": round(f1, 3), "fpr": round(fpr, 3), "latency": latency}


def main():
    thresholds = [2, 3, 5, 7, 10]
    scen = scenarios()
    rows = []
    for name, events in scen.items():
        for th in thresholds:
            m = evaluate(events, th)
            rows.append({"scenario": name, "threshold": th, **m})

    here = os.path.dirname(os.path.abspath(__file__))
    results = os.path.normpath(os.path.join(here, "..", "..", "results"))
    os.makedirs(results, exist_ok=True)
    with open(os.path.join(results, "e2_monitor.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # plot: F1 vs threshold per scenario
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    for name in scen:
        xs = [r["threshold"] for r in rows if r["scenario"] == name]
        ys = [r["f1"] for r in rows if r["scenario"] == name]
        ax.plot(xs, ys, marker="o", markersize=4, label=name)
    ax.set_xlabel("churn threshold (distinct tasks per shared prefix)")
    ax.set_ylabel("F1")
    ax.set_ylim(-0.02, 1.02)
    ax.legend(fontsize=7, loc="lower left")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(results, "e2_monitor.png"), dpi=200)

    # terminal summary
    print(f"{'scenario':15s} {'thr':>4s} {'P':>5s} {'R':>5s} {'F1':>5s} {'FPR':>5s} {'lat':>6s}")
    for r in rows:
        lat = "-" if r["latency"] is None else f"{r['latency']:.0f}"
        print(f"{r['scenario']:15s} {r['threshold']:4d} "
              f"{r['precision']:5.2f} {r['recall']:5.2f} {r['f1']:5.2f} "
              f"{r['fpr']:5.2f} {lat:>6s}")
    print("\nwrote results/e2_monitor.csv and results/e2_monitor.png")


if __name__ == "__main__":
    main()
