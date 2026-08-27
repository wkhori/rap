---
type: regex
source: {source: file, path: "**/research.md"}
pattern: 'https?://|[\w/.-]+\.(ts|js|py|go|rs|md|json):\d+'
match: contains
---
Every finding carries a source — a real URL for web research, or a `path:line` citation for
codebase research. A research file with no sources at all is model memory wearing a
citation format.
