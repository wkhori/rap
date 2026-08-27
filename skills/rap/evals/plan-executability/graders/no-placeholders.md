---
type: regex
source: {source: file, path: "**/plan.md"}
pattern: '\b(TBD|TODO|FIXME|\bXXX\b|<placeholder>|to be determined)\b'
flags: i
match: not_contains
---
"No placeholders, no TBD, no open questions — only locked decisions and tagged assumptions."
A plan with a TBD in it is not executable, which is the whole promise of this skill.
