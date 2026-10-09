# experiments

Reproducible paper experiments. Each script writes to `../../results/`.

## E1 — containment sweep on the shared-write reach graph

**Script:** `e1_reach_sweep.py`
**Keys needed:** none. Pure computation over synthetic permission models.
**Outputs:** `results/e1_reach.csv`, `results/e1_reach.png`.

Builds five topologies and sweeps the number of concurrent runs
`N ∈ {10, 50, 100, 500, 1000}`, computing channel reach `N_reach` under each
(paper §VI). The claim under test is RQ3: namespace isolation collapses
`N_reach` to 1 regardless of fleet size, while an open shared medium or a
single confused-deputy relay re-links the fleet.

Run:
```
python3 e1_reach_sweep.py
```

Measured result (`max N_reach` by topology × fleet size):

| Topology | N=10 | N=50 | N=100 | N=500 | N=1000 |
|---|---|---|---|---|---|
| T1 open, pipeline identity (C0) | 10 | 50 | 100 | 500 | 1000 |
| T2 per-run namespace (C2/C3) | 1 | 1 | 1 | 1 | 1 |
| T3 cross-task isolated + sanctioned collab | 1 | 1 | 1 | 1 | 1 |
| T4 one confused-deputy relay | 9 | 41 | 81 | 401 | 801 |
| T5 misconfig: object shared by 2 of 5 tasks | 4 | 20 | 40 | 200 | 400 |

Takeaway: containment is all-or-nothing. One relay or one shared object
undoes isolation across the whole fleet.

## E3 — abstention under reward pressure *(harness only, not yet run)*

**Script:** `e3_abstention.py`
**Keys needed:** `OPENAI_API_KEY` and/or `GEMINI_API_KEY` as env secrets.
Keys with real quota — first attempts errored with
`insufficient_quota` / daily-limit on both providers.
**Outputs when run:** `results/e3_runs.jsonl`.

Single-agent, benign. The only manipulation is whether a sanctioned
`declare_impossible` action exists and is scored as success. Hypothesis:
on the impossible tier, sanctioned abstention (condition B) raises
abstention and lowers canary touches vs. condition A.

Run (keys injected as env secrets by the environment, never passed as args):
```
python3 e3_abstention.py <reps> <openai_model|none> <gemini_model|none>
# e.g.:  python3 e3_abstention.py 5 gpt-5.4-mini gemini-3.8-flash
```
