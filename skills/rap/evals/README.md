# rap evals

Behavioural tests for the skill. Each case is a prompt plus graders that check what the
run actually *did* — which tools fired, which models were routed to, what landed in
`plan.md` — rather than whether the prose sounds good.

## Cases

| Case | Asks | Checks |
|---|---|---|
| `quick-tier-sizing` | one-file Python CLI | picks Quick, stays under the 2-agent cap, doesn't over-plan |
| `autonomous-no-questions` | URL shortener, "no questions" | zero `AskUserQuestion` calls, assumptions tagged, decisions `LOCKED:` |
| `plan-executability` | Markdown→HTML lib | no TBD, has Challenge + Handoff sections, phases are executable |
| `feature-mode-research` | add search to a scaffolded Express app | actually reads the codebase, cites real files, plan fits *this* repo |
| `model-routing` | multi-tenant webhook service | researchers on `sonnet`, Challenger on `opus`, no `fable` at Standard |

`feature-mode-research` and `model-routing` are tagged `expensive` — they run full Standard
tier with subagents.

## Running

**Official harness** (preferred, once your account has it — it is early-access gated):

```bash
cd skills/rap
claude plugin eval . --allow-tools Bash Write Edit WebFetch WebSearch
```

It runs each case in a sandboxed session, several times, plus a no-plugin baseline arm, and
reports the score delta and an HTML report. Self-test whether you have access: run
`claude plugin eval` in an empty directory — `No eval cases found` means you're enabled,
`` `plugin eval` is currently in early access `` means you're not.

**Local runner** (works today, same case files):

```bash
python3 evals/run_local.py                              # all cases, with + without arms
python3 evals/run_local.py --case quick-* --runs 1       # fast iteration
python3 evals/run_local.py --no-ablation --json out.json # skip the baseline arm
```

It runs headless `claude -p` sessions with the skill copied into a throwaway workspace at
`.claude/skills/rap`, parses the stream-json trace for tool calls, and grades. The
`without` arm re-runs the identical prompt with `--disallowedTools Skill`, so the delta
tells you whether the skill actually beat no-skill.

Cost is real — roughly $0.15 per Quick run and meaningfully more for the `expensive` cases,
multiplied by runs × arms. Start with `--runs 1 --no-ablation`.

## Grader types

`tool_used` (`tool`, `input_match`, `min`, `max`), `tool_order` (`before`, `after`),
`file_exists` (`path` glob over created files), `regex` (`pattern`, `flags`, `match:
contains|not_contains|count:N`), and `llm` (body is the rubric; a judge model votes).
Sources: `last_message` (default), `trace`, `files`, or `{source: file, path: <glob>}` for
a produced file's contents.

Prefer deterministic graders. LLM judges get noisy on long documents, which is why the
plan-quality rubrics are narrow and list explicit fail conditions.

A grader whose `tool` is `Skill` is treated as a *plugin-fired indicator* rather than a
scored criterion — it can't pass in the baseline arm by construction, so scoring it would
make every delta look artificially good.

## Known gaps

- **The one-question-round rule isn't directly tested.** Every case tells the skill to work
  autonomously, because a headless run has no one to answer `AskUserQuestion`. The
  autonomous path is covered; the "asks exactly once, and only about preferences" path
  still needs a human run.
- **Trigger reliability is a real finding, not a harness bug.** `quick-tier-sizing` and
  `feature-mode-research` invoke by the bare word `rap`, and the skill does not always
  fire — on a small brief the model sometimes just writes the code instead. That is why
  those two keep a `tool_used: Skill` grader; treat its score as the trigger-reliability
  metric.
- **`/rap` in headless `-p` never calls the `Skill` tool.** The slash form is expanded into
  the prompt directly, so a Skill-tool grader reports 0 calls even on a flawless run. The
  slash-form cases use a `skill-shaped-the-run` regex on the plan's mode/size/tier header
  instead. Don't "fix" a 0 there by loosening the grader.

## Cost

Measured, not estimated: one `autonomous-no-questions` run took **11 minutes and $2.30**;
one `quick-tier-sizing` run took 40s and $0.15. Multiply by runs × arms before launching the
full suite — the default `runs: 3` across 5 cases and 2 arms is a serious bill. Iterate with
`--runs 1 --no-ablation` and save the full sweep for release candidates.
