# rap

Research And Plan. Turns a brief into one plan file an agent can execute.

## Why

Planning prompts fail in two directions: a one-paragraph plan for a new system, or forty
minutes and 30k tokens spent on a two-file change. rap picks a tier from scope signals and
enforces it with hard agent and tool-call caps, so the effort matches the job.

## Install

```bash
npx skills add wkhori/rap
```

Or copy it in directly:

```bash
git clone https://github.com/wkhori/rap && cp -r rap/skills/rap ~/.claude/skills/rap
```

## Usage

```
/rap add magic-link auth to the Next.js app, we already use Postgres
/rap docs/brief.md
/rap <brief> --quick | --standard | --deep
```

Invoke it as `/rap`. The bare word `rap` is also a trigger but doesn't reliably fire on
small briefs — the model tends to just write the code instead.

## Tiers

Chosen automatically from scope signals — files touched, subsystems crossed, new
dependencies, schema boundaries. Never from a time estimate. The tier is stated in chat
before any work starts.

| | Quick | Standard | Deep |
|---|---|---|---|
| For | S/M changes | L changes | XL / new systems |
| Research | inline, ≤15 tool calls | 2–4 parallel researchers | researchers + adversarial verification |
| Agent cap | 2 | 5 | 10 |
| Challenger | self-pass | 1 agent | 1 agent + gap pass |
| Plan length | ~1 page | 2–4 pages | ≤8 pages |

## How it works

1. **Triage** — mode, size, tier, stated up front.
2. **Research** — codebase first, then primary sources only. Every claim carries a URL or
   `path:line` and a confidence rating. Versions and as-of dates recorded.
3. **Decide** — open items split into *fact* (researched) and *preference* (yours). One
   round of at most 4 questions, each with a recommendation. Everything lower-impact is
   defaulted and tagged `(assumed — not in brief)`.
4. **Draft** — phases with real file paths, named test cases, an acceptance command each.
5. **Challenge** — a Challenger agent reads the draft and reports `HOLDS` or
   `BLOCKER → FIX` per decision and phase. Fixes land before you see the plan.

## Output

```
docs/plans/2026-08-26-magic-link-auth/
├── plan.md        # decisions, phases, tests, acceptance, handoff prompt
├── research.md    # findings with sources and confidence
└── brief.md       # only if the brief came as a file, long paste, or ticket key
```

The run directory goes in the repo's existing plans or specs folder when it has one
(`docs/specs/`, `plans/`, …); `docs/plans/` is only the fallback.

[`examples/quick-tier-plan.md`](examples/quick-tier-plan.md) is real, unedited output from a
one-sentence brief.

## Model routing

| Role | Model |
|---|---|
| Researcher, verifier | `sonnet` |
| Challenger — Standard | `opus` |
| Challenger — Deep, gap pass | `fable` |

Retrieval is I/O-bound, so it runs cheap. A high-stakes brief steps the Challenger up, not
the researchers.

## Cost

A Quick run is about $0.15. Standard is a few dollars. Deep is more — it routes the
Challenger to Fable 5.

## Evals

Five cases under `skills/rap/evals/`, in the `claude plugin eval` format, plus a local
runner that works today:

```bash
python3 skills/rap/evals/run_local.py --case quick-* --runs 1
```

The runner re-runs each prompt with the skill disabled and reports the delta. On
`plan-executability` that delta is 100% vs 0% — the baseline writes no plan at all.
`skills/rap/evals/README.md` lists what isn't covered yet.

## Requirements

Claude Code. The skill calls `Agent`, `AskUserQuestion`, `WebSearch`/`WebFetch` and
optionally `Workflow` by name, so it isn't portable to other agent harnesses as-is.

## License

MIT © Walid Khori
