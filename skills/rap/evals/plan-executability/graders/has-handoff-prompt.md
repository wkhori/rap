---
type: regex
source: {source: file, path: "**/plan.md"}
pattern: '##\s*Handoff prompt'
match: contains
---
plan.md always ends with a filled-in handoff prompt so a fresh session can execute it.
