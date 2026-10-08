# File-share / object-store channel (placeholder)

**Shared medium:** a file share or object store two runs can both access.
**Channel class:** storage.
**Carrier category:** file metadata and the presence/naming of marker files.

No implementation is provided. The defensive requirement is that monitoring
watch metadata mutations and directory churn, not only content writes. In the testbed this category is exercised only through the benign
`ChannelProbe` interface (an inert operator-planted marker), never a real
encoder.
