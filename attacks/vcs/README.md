# Version-control channel (placeholder)

**Shared medium:** a git repository two runs can both access.
**Channel class:** storage.
**Carrier category:** commit-message and metadata fields; repository ignore/exclude lists.

No implementation is provided. The defensive requirement is that monitoring
inspect commit metadata and ignore/exclude lists, not only the tracked diff a content scanner sees. In the testbed this category is exercised only through the benign
`ChannelProbe` interface (an inert operator-planted marker), never a real
encoder.
