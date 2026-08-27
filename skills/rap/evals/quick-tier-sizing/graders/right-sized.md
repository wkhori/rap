---
type: llm
weight: 1
---
Judge whether the effort matched the job. PASS if the response reports a Quick-tier run:
a short plan, research done inline rather than delegated, and no elaborate multi-phase
architecture for what is a single Python file.

FAIL if it treated a one-file script as a large project — for example by spawning multiple
researchers, producing more than roughly two pages of plan, inventing subsystems, or
proposing phases that are not independently meaningful for a single script.

Ignore whether the plan is well-formatted. Judge only the sizing.
