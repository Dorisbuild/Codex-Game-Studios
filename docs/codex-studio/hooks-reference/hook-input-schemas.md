# Explicit helper interface

The framework has no event-payload schema. Its helpers run as terminal
commands, not assistant event handlers. Read a script's usage first.

Configuration reads, artifact inspection and story status are read-only.
Checkpoint rotation and configuration migration can write: inspect their
preview/options and the user's scope before running them.

Any future lifecycle integration must separately verify the current host's
event schema, actual payload, output visibility, exit status, approval behavior
and error cases before being registered. No such integration ships here.
