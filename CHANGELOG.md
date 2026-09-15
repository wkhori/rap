# Changelog

## 0.1.1 — 2026-09-15

Fixes from the first Standard-tier dry run (18 min, 3 Sonnet researchers, 1 Opus
Challenger). Model routing held; these are all prompt and rule fixes.

- Run directory: use the repo's existing plans or specs folder when it has one; `docs/plans/`
  is only the fallback when none exists.
- Researchers must verify negatives — a zero-match search is only a finding once the target
  is confirmed to exist and be installed; otherwise it is `Unknown`, confidence L.
- Challenger may overturn a `LOCKED` decision when its fix is sourced. The lock is re-tagged
  `LOCKED: … Revised by Challenger from: …`, listed in the chat summary, and the user is
  re-asked only if scope, cost, or a stated preference changes.
- Challenger now has a budget (≤15 tool calls, read-only) and a boundary: fixes are edits to
  `plan.md` only — never a ticket comment, PR, or other external write.
- A ticket key counts as a brief; the ticket text is written to `brief.md` so a handoff
  session without the ticket CLI can read it.
- `WebSearch`/`WebFetch` preload is scoped to whoever actually fetches, not unconditional.
- Researcher tool budget is now a 20-call target with a hard stop at 30 (observed runs hit
  24, 34, 38 under the old advisory cap).
- `AskUserQuestion` layout: labels ≤6 words, the one-sentence why lives in `description`.

## 0.1.0 — 2026-08-26

First public release. Claude Code-native.

- Tier system (Quick / Standard / Deep) chosen from scope signals, with hard agent and
  tool-call caps per tier.
- Fact vs. preference split — the skill researches facts and only asks you preferences.
- Single `AskUserQuestion` round, max 4 questions, each with a recommendation.
- Parallel researchers appending to a shared `research.md` with sources and confidence.
- Challenger pass (and a Deep-tier gap pass) applied before the plan is delivered.
- `Workflow`-runner deep research path for ≥4 independently verifiable questions.
- Plans end in a handoff prompt for a fresh session.
