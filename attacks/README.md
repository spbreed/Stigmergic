# attacks/ — category placeholders

Each subfolder names a **category** of shared medium that can carry a stigmergic
channel, and states the monitoring an operator must add to cover it. These are
placeholders by design: this repository does **not** implement channels, encode
payloads, or evade monitors. The point of the paper and of this tooling is
defensive — to characterize the attack surface and detect use of it, not to
provide working carriers.

Each folder maps to a row of the paper's channel-media table (§III) and is
exercised in the testbed only through the benign `ChannelProbe` interface
(`testbed/runner_interface.py`), i.e. an operator-planted, non-functional marker
used to measure observability between runs.

| Folder | Shared medium | Channel class | Monitoring requirement |
|--------|---------------|---------------|------------------------|
| `vcs/` | Version control | Storage | Inspect commit metadata and ignore lists, not only tracked diffs |
| `fileshare/` | File share / object store | Storage | Watch metadata mutations and directory churn, not only content writes |
| `tracker/` | Issue tracker / workspace | Storage | Record label and edit-history changes, not only final comment text |
| `process_socket/` | Process / socket table | Storage / timing | Treat the local process and socket table as readable shared state |
