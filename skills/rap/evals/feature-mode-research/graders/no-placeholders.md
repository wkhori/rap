---
type: regex
source: {source: file, path: "**/plan.md"}
pattern: '\b(TBD|TODO|FIXME|to be determined)\b'
flags: i
match: not_contains
---
No placeholders in a finished plan.
