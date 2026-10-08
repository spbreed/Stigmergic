# Process / socket channel (placeholder)

**Shared medium:** a host whose process table and local sockets two runs can both observe.
**Channel class:** storage / timing.
**Carrier category:** process names/arguments and local port bindings.

No implementation is provided. The defensive requirement is that monitoring
treat the local process and socket table as readable shared state and monitor accordingly. In the testbed this category is exercised only through the benign
`ChannelProbe` interface (an inert operator-planted marker), never a real
encoder.
