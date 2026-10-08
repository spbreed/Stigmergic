# Stigmergic

Measurement and containment tooling for the paper *Stigmergic Communication in
Multi-Agent AI Systems: How Shared Infrastructure Becomes a Covert Channel, and
How to Contain It* (Ramamoorthy and Gupta).

This repository is the **defensive and measurement** side of that work: it lets
an operator reason about, detect, and contain stigmergic channels — covert
coordination between concurrent agent runs through writable shared
infrastructure. It does **not** ship working covert channels.

## What is here

| Path | What it is | Status |
|------|------------|--------|
| `analysis/reach_graph.py` | Builds the shared-write graph from a declared permission model and computes channel reach `N_reach` (paper §VI). | Working |
| `monitor/shared_write_monitor.py` | Reads a sandbox event log and flags cross-task reads and namespace churn — the runtime detector the paper argues for. | Working |
| `testbed/` | The air-gapped testbed design: conditions C0–C3, benign canaries, and a documented runner **interface**. | Scaffold |
| `attacks/` | One placeholder folder per channel **category** (version control, file share, issue tracker, process/socket). Each states the category and the monitoring it requires. | Placeholders, by design |
| `results/` | Result templates (all `TBD`) matching the paper's tables. | Templates |

## What is deliberately not here

- **No channel implementations.** The `attacks/` folders are placeholders. This
  repository does not contain code that encodes data into commit metadata, file
  attributes, marker files, port bindings, or any other carrier, and it does not
  contain code to evade a monitor. Those are the offensive half of the dual-use
  line and are out of scope for a public release.
- **No model execution.** `testbed/runner_interface.py` defines the interface a
  model runner must satisfy; it is not implemented. Running a live multi-agent
  elicitation study is the authors' experiment to conduct under their own
  institutional safety review, in the contained, air-gapped environment the
  paper specifies, never against production infrastructure.

## Intended use

Defensive security research and reproducibility of the paper's **measurement**
claims: compute `N_reach` for a proposed harness configuration before launch,
and run the monitor against a captured event log to detect board formation. See
`SECURITY.md` for the responsible-use boundary and `DISCLOSURE.md` for the
AI-assistance disclosure that accompanies the paper.

## Quick start

```
python3 analysis/reach_graph.py analysis/permission_model.example.json
python3 monitor/shared_write_monitor.py monitor/events.example.jsonl
```

## License

Apache-2.0. See `LICENSE`.
