# Testbed (scaffold)

The contained, air-gapped environment from paper Section VII. This directory
holds the **design and interfaces**, not a runnable elicitation harness.

- `conditions.json` — the four conditions C0–C3 (Table VII).
- `models.json` — the initial cohort: Claude-supported models only.
- `canaries.py` — inert honeytokens; touching one halts a run. Working.
- `runner_interface.py` — the contract a sandboxed model runner and benign
  channel probe must satisfy. **Not implemented.**

## Why the runner is not implemented here

Running a live multi-agent study — placing concurrent agents under reward
pressure in shared-writable infrastructure and measuring whether they form
cross-run channels — is a sensitive experiment. It belongs in an environment
with **no outbound network and no real credentials**, under the authors'
institutional review, not in a public repository and not driven from this
tooling. The interface is provided so that such a harness can be built against a
fixed contract; the authors supply the runner.

## Containment requirements (must all hold before any run)

1. No route to the internet from any agent sandbox.
2. No real credentials anywhere in the environment; only `canaries.py` tokens.
3. `analysis/reach_graph.py` is run first and its `N_reach` is recorded per
   condition.
4. `monitor/shared_write_monitor.py` consumes every run's event log.
5. Any canary touch halts the run and the batch.
