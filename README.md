# rap — Research And Plan

A Claude Code skill that turns a brief into **one plan an agent can actually execute**.

It researches the codebase and primary sources, sizes the work honestly, asks you only the
decisions that matter, tears its own plan apart before you see it, and writes a single
`plan.md` ending in a handoff prompt.

```bash
npx skills add wkhori/rap
```

Then, in Claude Code:

```
/rap add magic-link auth to the Next.js app, we already use Postgres
```

---

## Why this exists

Most planning prompts fail in one of two directions: they produce a one-paragraph plan for a
new system, or they burn forty minutes and 30k tokens producing a mediocre plan for a
two-file change.

`rap` fixes the effort to the job with an explicit tier system, and enforces it with hard
agent and tool-call caps.

| | Quick | Standard | Deep |
|---|---|---|---|
| For | S/M changes | L changes | XL / new systems |
| Research | inline, ≤15 tool calls | 2–4 parallel researchers | researchers + adversarial verification |
| Agent cap | 2 | 5 | 10 |
| Challenger | self-pass | 1 agent | 1 agent + gap pass |
| Plan length | ~1 page | 2–4 pages | ≤8 pages |

Tier is chosen from scope signals — files touched, subsystems crossed, new dependencies,
schema boundaries — never from a time estimate.

## What it actually does differently

**Never asks you a question it can answer itself.** Every open item is split into *fact*
(the skill finds it) or *preference* (you decide). Facts are researched. Only preferences
reach you.

**One question round. Ever.** High-impact, hard-to-reverse decisions get bundled into a
single `AskUserQuestion` call — max 4, each with a recommendation and a reason. Everything
lower-impact is defaulted and tagged `(assumed — not in brief)` so you can scan what was
decided for you.

**Primary sources only.** Official docs, source, specs, changelogs. Every claim carries a URL
and a confidence rating. Model memory of library APIs is stale, and the skill treats it that
way — it records versions and as-of dates, and "no data found" is a valid finding rather than
an invitation to guess.

**An adversarial pass before you read it.** A Challenger agent reads the draft plan and the
research, then reports `HOLDS` or `BLOCKER → FIX` per decision and per phase. Fixes land in
the plan before it reaches you. Deep tier adds a gap pass that traces every requirement in
your brief to a phase and a named test.

**Plans that execute.** Real file paths, named test cases, an acceptance command per phase.
No "TBD", no placeholders, no open questions. The last section is a handoff prompt you can
paste into a fresh session.

## Output

```
docs/plans/2026-08-26-magic-link-auth/
├── plan.md        # decisions, phases, tests, acceptance, handoff prompt
├── research.md    # findings with sources and confidence
└── brief.md       # only if the brief came as a file or long paste
```

## Flags

```
/rap <brief>              # tier chosen automatically from scope
/rap <brief> --quick      # force Quick
/rap <brief> --standard   # force Standard
/rap <brief> --deep       # force Deep
/rap docs/brief.md        # a path works too
```

## You'll know it worked when

- One run directory exists, with a `plan.md` containing no "TBD" and no open questions.
- You were asked exactly one round of questions, all of them genuine preferences.
- Every phase names real files, real test cases, and a command that proves it's done.
- A fresh session can execute the plan from the handoff prompt without asking you anything.

## Requirements

Claude Code. The skill calls `Agent`, `AskUserQuestion`, `WebSearch`/`WebFetch`, and
optionally the `Workflow` runner at Deep tier, by name. That's deliberate — naming the real
tools makes the behaviour deterministic instead of conditional. It is not portable to other
agent harnesses as-is.

## Feedback

This is v0.1.0 and I'm actively looking for feedback — especially on whether the tier
triage picks the right size, and whether the plans actually survive execution.

**[Open a feedback issue](https://github.com/wkhori/rap/issues/new?template=feedback.yml)** —
it's four questions and takes a minute.

## License

MIT © Walid Khori
