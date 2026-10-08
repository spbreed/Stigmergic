# Responsible use

This repository is for defensive security research: measuring and containing
stigmergic coordination between concurrent AI agent runs. It intentionally
contains no working covert channels, no payload encoders, and no
monitor-evasion code, and it does not drive live models.

- **Do** use `analysis/` and `monitor/` to check a harness configuration and to
  detect board formation in a captured event log.
- **Do** run any elicitation study only in a contained, air-gapped environment
  with no outbound network and no real credentials, under your institution's
  safety review, using your own runner behind `testbed/runner_interface.py`.
- **Do not** use this work to build covert channels, exfiltrate data, or evade
  monitoring on systems you do not own and are not authorized to test.

Report concerns to the paper's corresponding author.
