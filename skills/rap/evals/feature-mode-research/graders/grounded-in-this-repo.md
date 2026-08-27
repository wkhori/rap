---
type: llm
weight: 2
source: {source: file, path: "**/plan.md"}
---
This plan was written for an existing tiny Express + SQLite service. Its real shape:

- `src/server.js` — express app, mounts `/notes`
- `src/api/notes.js` — GET /, GET /:id, POST /
- `src/store/notes.js` — better-sqlite3, a `notes` table with id/title/body/created_at
- `test/notes.test.js` — node:test
- No auth, no migrations system, no ORM

PASS only if the plan is clearly grounded in THAT codebase:
- It works with better-sqlite3 and the existing `notes` table rather than proposing a
  different database, an ORM, or a search service the project doesn't have — unless it
  explicitly justifies adding one as a locked decision with rejected alternatives.
- It says how the existing `notes` table gets a search index and a tags relation, given
  there is no migration tooling.
- Its tests fit `node:test`, matching `test/notes.test.js`.

FAIL if the plan reads like generic advice about adding search to "an API" — if you could
swap in any other codebase and the plan would read the same, it fails.
