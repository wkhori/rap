# Changelog

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
