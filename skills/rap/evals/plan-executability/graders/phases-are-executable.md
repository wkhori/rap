---
type: llm
weight: 2
source: {source: file, path: "**/plan.md"}
---
You are judging whether this plan could be handed to a fresh coding agent and executed
without the agent needing to ask anything.

PASS only if ALL of these hold:
- Every phase names real, specific file paths — not "the parser module" but `src/parser.js`.
- Every phase names its test cases individually, rather than counting them
  ("rejects an unclosed code fence", not "5 tests").
- Every phase states an observable acceptance condition, including a command to run.
- Each phase carries exactly one size (S, M, L or XL) — never a range like "M–L".
- There are no open questions left anywhere in the document.

FAIL if any phase is a vague instruction ("implement the parser"), if acceptance is
described only as "it works", or if the reader would have to make a design decision the
plan left open.
