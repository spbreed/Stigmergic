# Issue-tracker / workspace channel (placeholder)

**Shared medium:** a shared issue tracker or workspace.
**Channel class:** storage.
**Carrier category:** label/draft state and comment edit history.

No implementation is provided. The defensive requirement is that monitoring
record label and edit-history changes, not only final comment text. In the testbed this category is exercised only through the benign
`ChannelProbe` interface (an inert operator-planted marker), never a real
encoder.
