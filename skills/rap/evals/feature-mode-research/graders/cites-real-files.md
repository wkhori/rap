---
type: regex
source: {source: file, path: "**/plan.md"}
pattern: 'src/store/notes\.js|src/api/notes\.js'
match: contains
---
The plan must reference the files that actually exist in this repo — the ones any search or
tag feature has to touch. A plan that invents file paths is not executable here.
