---
type: llm
weight: 2
source: trace
---
This is the tool-call trace of a planning run. Look only at calls to the `Agent` tool and
the `model` and `effort` values in their inputs.

PASS if the routing is deliberate and role-appropriate:
- Agents doing research, fetching, reading or summarizing are on `sonnet`.
- At most one or two agents doing adversarial review, challenge, or architecture judgment
  are on `opus` (or the model field is omitted to inherit the session model).
- No agent is on `fable` — this is a Standard-tier run, not Deep.
- Effort values are not uniformly maxed out; cheap mechanical roles use lower effort.

FAIL if every agent gets the same model regardless of its job, if researchers are on opus
or fable, or if no `model` is ever specified on any agent (that is inheritance by accident,
not routing by design).
