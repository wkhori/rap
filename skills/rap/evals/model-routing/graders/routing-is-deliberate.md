---
type: llm
weight: 2
source: trace
---
This is the tool-call trace of a planning run. Look only at calls to the `Agent` tool and
the `model` value in their inputs. (`Agent` has no reasoning-effort parameter — do not look
for one.)

PASS if the routing is deliberate and role-appropriate:
- Agents doing research, fetching, reading or summarizing are on `sonnet`.
- At most one or two agents doing adversarial review, challenge, or architecture judgment
  are on `opus`.
- No agent is on `fable` — this is a Standard-tier run, not Deep.
- Every Agent call names a model explicitly.

FAIL if every agent gets the same model regardless of its job, if researchers are on opus
or fable, or if any Agent call omits `model` (that is inheritance by accident, not routing
by design).
