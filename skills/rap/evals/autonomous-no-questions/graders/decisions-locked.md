---
type: regex
source: {source: file, path: "**/plan.md"}
pattern: 'LOCKED:'
match: contains
---
Every decision is recorded as "LOCKED: X — because Y. Rejected: A (why), B (why)."
