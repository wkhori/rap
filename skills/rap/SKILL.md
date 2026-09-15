---
name: rap
description: Research And Plan. Turns a brief into one executable plan file — researches the codebase and primary sources in parallel, sizes the work, asks only the high-impact decisions, runs an adversarial Challenger, and ends with a handoff prompt. Use when the user says "rap", "/rap", "research and plan", "presearch", "plan this feature", "plan this project", or hands over a brief and wants a plan before building.
argument-hint: "[brief, feature description, or path to a brief file] [--quick|--standard|--deep]"
user-invocable: true
license: MIT
metadata:
  author: Walid Khori
  homepage: https://github.com/wkhori/rap
  version: 0.1.1
---

# rap — Research And Plan

Turn a brief into one plan an agent can execute end-to-end. Fit the effort to the job: a small change gets a one-page plan in minutes; a new system gets parallel research, a Challenger, and a full plan. Never the reverse — long sessions that produce mediocre plans are the failure mode this skill exists to prevent.

Brief: `$ARGUMENTS`. If empty, ask exactly one intake question ("What are we building or changing — and is there a brief, rubric, or deadline I should read?") and never ask another intake question. A ticket key (Jira, Linear, GitHub issue) counts as a brief: fetch the ticket and treat its text as the brief. A `--quick|--standard|--deep` flag forces the tier.

## 1. Triage (lead, inline)

Read the brief in full (if it is a path, read the file). Orient in the repo: `CLAUDE.md`, `AGENTS.md`, `README`, one glob pass, where docs/plans already live. If the user supplied a research or design doc, treat it as settled — extend it, don't redo it.

Decide three things and state them in chat in ≤3 lines before continuing:

- **Mode** — `greenfield` (new repo) · `feature` (existing repo, additive) · `revision` (changing existing design/behavior). Mode is not size: a greenfield 1-file tool is S.
- **Size** — by scope signals, never by time. When signals straddle bands, take the larger.
  - **S** one file or one concept; no new deps; no schema change
  - **M** a handful of files in one subsystem; ≤1 new concept; ≤1 new dep
  - **L** crosses 2+ subsystems, or new dep + a schema/API/IPC boundary
  - **XL** new service, protocol, or architecture; breaking changes; multi-surface greenfield product
  - Greenfield has no existing files to count, so size it by surfaces instead: **S** one file or script · **M** one service with one storage concern · **L** persistence + API + UI · **XL** multi-surface product
- **Tier** — S/M → **Quick**, L → **Standard**, XL → **Deep**. Step up one tier if the brief carries a rubric/eval criteria, regulated or PII data, or the user asked for depth; step down if they asked for speed. Re-tier upward at most once mid-run, and say so. Never silently step down.

| | Quick | Standard | Deep |
|---|---|---|---|
| Research | lead, inline, ≤15 tool calls | 2–4 parallel researchers | parallel researchers; `Workflow` optional |
| Agent cap (hard, whole run) | 2 | 5 | 10 |
| Challenger | self-pass, written into plan | 1 agent | 1 agent + gap pass |
| Decision questions (one round) | 1–2 | 2–4 | 3–4 |
| Plan length | ~1 page | 2–4 pages | ≤8 pages; overflow → research.md |

**Agent & model fit** — spawn with the `Agent` tool. Route by what the role actually
demands, not by how important the project feels.

Every spawn is `subagent_type: general-purpose` — researchers need Bash to append to
`research.md`, which read-only agents can't do. Pass `model` explicitly on all of them;
`Agent` has no reasoning-effort parameter (only the `Workflow` runner's `agent()` does).

| Role | `model` | Why this tier |
|---|---|---|
| Researcher (fetch, read, cite, summarize) | `sonnet` | I/O-bound work — fetch a page, quote it, rate confidence. Reasoning strength buys almost nothing here; volume and cost do |
| Verifier (refute one claim) | `sonnet` | One narrow question with a yes/no answer |
| Challenger — Standard | `opus` | Adversarial reasoning over a bounded plan |
| Challenger — Deep, gap pass | `fable` | The one role where the strongest model pays for itself: long-horizon reasoning across a whole architecture, where a missed structural flaw costs more than the run |

**Cost discipline.** Sonnet 5 is $2/$10 per Mtok, Opus 5 $5/$25, Fable 5 $10/$50 — Fable is
5× Sonnet in and out. Spend it on judgment, never on retrieval. Concretely:

- Never step the *researchers* up a tier because the brief is high-stakes. Step the
  **Challenger** up instead — that is where model strength converts into caught mistakes.
- A Quick run should not reach for `opus` or `fable` at all; if it feels like it needs to,
  you mis-tiered — re-tier and say so.
- **Always pass `model` explicitly on every spawn**, even when it matches the session model.
  Inheriting by omission is routing by accident: it makes a run unauditable, and it silently
  puts researchers on whatever the lead happens to be using.
- Prices as of Aug 2026 — re-check before trusting them.

(Quick tier's lone `Explore` agent is the exception: it's read-only, so it returns findings and the lead writes `research.md` itself.) Send parallel agents as multiple `Agent` calls in **one** message or they run sequentially. `WebSearch`/`WebFetch` may be deferred; load them with `ToolSearch("select:WebSearch,WebFetch")` only before you yourself fetch — at Standard and Deep the lead usually does no web work — and tell every researcher to load them before its first fetch.

**Run directory** — check first whether a run directory for this same work already exists; if it does, do not create a second one — switch to `revision` mode over its `plan.md`. Otherwise create it now. If the repo already has a plans or specs folder under any name (`docs/plans/`, `docs/specs/`, `plans/`, `specs/`, `docs/design/` …), use it and follow its naming convention for the subfolder; fall back to `docs/plans/YYYY-MM-DD-<slug>/` only when none exists. Greenfield: create the project folder first and put the run dir inside it; never write into a non-project cwd (e.g. a Desktop). Files: `plan.md` (always), `research.md` (create with a title line only — each researcher's heredoc opens with its own `## <angle>` heading, since `>>` can only append at end-of-file), `brief.md` when the brief came as a file, a long paste, or a ticket key — for a ticket, write the fetched ticket text into `brief.md` so a handoff session without the ticket CLI can read it; if the brief is a large document, `brief.md` holds a one-line pointer to the original rather than a copy.

## 2. Research

Goal: facts that change a decision, not a survey. Two lenses, always:

- **Known knowns** — what the brief asserts or implies. Verify the load-bearing ones (does that API exist, does the installed version support X, does the current code behave as the brief assumes).
- **Unknown unknowns** — what the brief never mentions but the work needs. Walk `references/agent-prompts.md#unknown-unknowns`; surface anything material as a decision question, an assumption, or a non-goal.

Rules:
- Codebase first: files, patterns, tests, conventions the change touches. Cite `path:line`. Read code, don't guess from filenames.
- Web: primary sources only — official docs, source, specs, changelogs, pricing pages. `WebFetch` the real page over trusting search snippets. Every claim gets a URL and a confidence (H/M/L). Never invent a URL or a number; "no data found" is a finding. Record versions and as-of dates — model memory of library APIs is stale.
- Verify negatives: a zero-match search is only a finding after you confirm the search target exists and is installed (`ls` the path, `pnpm ls <pkg>` / `npm ls <pkg>`, the worktree's `node_modules` is populated). Otherwise report it as `Unknown`, confidence L — never "zero matches, confidence H".
- Findings go to `research.md` as Finding · Source · Key numbers · Gotcha · Confidence. Later agents read the file, not chat.
- **Revision mode**: research = read the existing design doc and the code it describes; write a `## Drift` table (doc says · code does · keep / reopen) into `plan.md`. Only reopened decisions enter the decision frontier; the rest are listed `KEPT`. The old doc gets a one-line pointer to the run dir — never a rewrite.

Delegation by tier:
- **Quick** — do it yourself. One `Explore` agent only if the codebase is unfamiliar; collect its output and write `research.md` yourself.
- **Standard** — spawn researchers in parallel, one per angle the brief needs (codebase; primary-source web; plus at most two of domain/design/data/infra), prompt `references/agent-prompts.md#researcher`. Each appends under its own heading in `research.md` with a single Bash heredoc (`cat >> research.md <<'EOF'`) — never read-then-write the shared file — and returns a ≤300-word summary.
- **Deep** — as Standard. When ≥4 independent research questions need adversarial verification, use the `Workflow` runner (`references/deep-workflow.md`); otherwise parallel researcher + verifier agents. Budget rule either way: `questions + 2·high-stakes + 1 ≤ 8` agents.

Budget: lead inline research ≤15 tool calls (Quick) / ≤25 (Standard, Deep). Every researcher targets 20 tool calls and has a hard stop at 30: at call 30 it stops, appends what it has, and returns — no exceptions. Research **ends** when every frontier question has a recommendation. Anything still unverified becomes an `Unknown` line in `research.md` with what we'll do about it — never another research pass.

## 3. Decide

Split every open item into **fact** (you find it) or **preference** (user decides). Never ask the user for a fact.

- Low-impact or easily reversible → choose a sensible default and tag it `(assumed — not in brief)`.
- High-impact or hard to reverse (data store, auth, hosting, core UX model, scope cuts, which innovations to keep, anything a rubric scores) → **decision frontier**. For Standard/Deep architectural choices, consider ≥2 structurally distinct options before recommending.

Ask the frontier in **one** `AskUserQuestion` call — count per the tier table (max 4 questions, which is also the tool's cap). If the frontier exceeds 4, the extras are by definition lower-impact — default and tag them. Each question gets 2–4 options. Labels are ≤6 words including `(Recommended)` on the first, recommended option; the one-sentence *why* goes in that option's `description`, never in the label — the tool renders labels as narrow chips and truncates anything longer. At least one question should come from the unknown-unknowns pass. If the frontier is empty, say "no decisions needed; N assumptions" and continue. If the brief says autonomous / no questions, or the user says "just decide", skip the round, take every recommendation, annotate.

Lock every decision as `LOCKED: X — because Y. Rejected: A (why), B (why).`

## 4. Draft

Write `plan.md` from `references/plan-template.md` — at minimum Summary, Decisions, Setup & commands, Phases — dropping sections the tier doesn't warrant.

- No time estimates. Each phase has exactly one size (S/M/L/XL); if you want to write "M–L", split the phase.
- Phases are independently testable; order: scaffold → riskiest unknown → core path → edges → polish; types/schema before consumers; tests named, not counted.
- Real file paths, function names, commands. No placeholders, no "TBD", no open questions — only locked decisions and tagged assumptions.
- Innovations (`CORE / STRETCH / CUT`) only when the brief invites them (greenfield product, demo, rubric); every CORE item lands in a named phase.

## 5. Challenge

- **Quick** — self-pass written into `plan.md` as `## Challenge`: 3 lines of `assumption → failure scenario → fix applied`. A Quick plan without this section is incomplete.
- **Standard / Deep** — spawn one Challenger (`references/agent-prompts.md#challenger`) pointed at the run dir — `model: opus` at Standard, `model: fable` at Deep. It answers `HOLDS` or `BLOCKER: … → FIX`. Apply fixes to `plan.md`; reconcile conflicts in favor of sourced data over opinion.
  - **Budget and boundary.** The Challenger gets ≤15 tool calls and is read-only. Every FIX is an edit to `plan.md` that the lead applies — never a ticket comment, a PR, a commit, or any write outside the run dir. A fix that amounts to "tell an external system something" is out of scope: turn it into a phase step for the implementer if the plan needs it, otherwise drop it.
  - **Overturning a lock.** A Challenger may replace a `LOCKED` decision when its fix is sourced (`research.md` or a `path:line` / URL it cites). Re-tag the decision `LOCKED: <new X> — because <Y>. Revised by Challenger from: <old X> (<why it failed>).` and list every revised lock in the chat summary. Re-ask the user only if the revision changes scope, cost, or a preference the user stated in the question round — otherwise no second question round.
- **Deep** — add the gap pass (`#gap-pass`): trace every requirement to a phase and a named test; patch the plan, don't report holes.

## 6. Finalize & deliver

Append the **Handoff prompt** (`references/agent-prompts.md#handoff`) to `plan.md`. In chat, ≤150 words: tier, run directory, 3–5 key decisions in plain language, any locks the Challenger revised, assumptions count, the single biggest risk. Then: "Start Phase 1 here, or hand off?" — for Deep, recommend handing off to a fresh session (this one's context is already large). Do not implement unless told to.

## Example run

> `/rap add magic-link auth to the Next.js app, we already use Postgres`

```
Mode: feature · Size: L · Tier: Standard
Run dir: docs/plans/2026-08-26-magic-link-auth/
```
Three researchers spawned in one message — codebase (`general-purpose`, `sonnet`), primary-source web (same), data/infra (same). They append `## codebase`, `## web`, `## data` to `research.md`. Web researcher finds the installed `next-auth` is v4 and the brief's assumed API is v5-only → contradiction, confidence H, cited to the changelog.

One `AskUserQuestion` round, 3 questions: session storage (DB sessions *(Recommended)* / JWT), link TTL (15 min *(Recommended)* / 1 hr), email provider (Resend *(Recommended)* / SES / SMTP). Everything else defaulted and tagged — 6 assumptions.

Challenger returns two BLOCKERs: no rate limit on the send-link endpoint, and no handling for a link redeemed twice. Both fixed into phases before the plan is finalized.

Output: `plan.md` — 4 phases (schema → send/verify path → rate limit + replay → UI states), each with named tests and an acceptance command, ending in a handoff prompt.

## You'll know it worked when

- One run directory exists with `plan.md`, and `research.md` if the tier called for it.
- You were asked **one** round of questions, all preferences — never a question whose answer is a fact discoverable in the repo or the docs.
- Every phase names real files, real test cases, and a command you can run to prove it's done.
- `plan.md` contains no "TBD", no placeholder, and no open question.
- A fresh session can execute the plan from the handoff prompt without asking you anything.

## Guardrails

- Agent caps (2/5/10) include researchers, Challenger, verifiers, and every `Workflow`-spawned agent. Wanting more means you mis-tiered — re-scope, don't spawn. Hard stops (agent caps, the lead's inline budget, the researcher's 30-call stop, the Challenger's 15) are stop lines, not targets.
- One question round. One run directory. Everything else is chat.
- Every subagent prompt carries the brief verbatim, the locked decisions, the run directory path, and "no preamble, no questions back" — agents start cold.
- Don't re-run research a supplied document already settled; revise an existing plan, don't rewrite it.
- If a Quick run blows its budget, it isn't Quick — re-tier once and say so; if budgets blow again, write the plan with what you have and tag gaps as assumptions.
