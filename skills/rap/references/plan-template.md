# Plan template

Written as `plan.md` inside the run directory (the repo's existing plans or specs folder if it has one — e.g. `docs/specs/YYYY-MM-DD-<slug>/` — else `docs/plans/YYYY-MM-DD-<slug>/`) alongside `research.md` and optional `brief.md`. Keep every section that earns its place for the tier; delete the rest.

Tier guidance — **Quick**: Summary, Brief, Assumptions, Decisions, Setup & commands, Phases, Challenge, Handoff. **Standard** adds Research, Risks, Requirements trace, Non-goals. **Deep** keeps everything, ≤ ~8 pages; overflow goes to `research.md`. **Revision** mode adds Drift.

```markdown
# <Feature / Project name>

**Mode:** greenfield | feature | revision · **Size:** S/M/L/XL · **Tier:** Quick | Standard | Deep
**Research:** `./research.md` (omit if none) · **Brief:** `./brief.md` (if supplied as a file, long paste, or ticket)

## Summary
3–4 sentences: what we're building, the approach, why this approach over the obvious alternative.

## Brief
Verbatim user brief if short; otherwise "see `./brief.md`". Do not paraphrase.

## Assumptions
Every default chosen for the user, each tagged `(assumed — not in brief)`. One line each. Deadline note if any ("no deadline given — ordered by risk, not calendar").

## Drift                         <!-- revision mode only -->
| Design doc says | Code actually does | Keep / Reopen |
Reopened rows become decisions below; kept rows are listed as `KEPT: …`.

## Research findings            <!-- Standard / Deep -->
Only findings that changed a decision. Per finding: **Finding** · Source (URL or `path:line`) · Key numbers · Gotcha · Confidence H/M/L.
Separate **Found** (evidence) from **Inferred** (reasoning) from **Unknown** (could not verify — and what we'll do about it).

## Decisions
`LOCKED: <decision> — because <reason>. Rejected: <alt A> (<why>), <alt B> (<why>).`
A lock the Challenger overturned with a sourced fix: `LOCKED: <new decision> — because <reason>. Revised by Challenger from: <old decision> (<why it failed>).`
Standard/Deep add per decision: Confidence H/M/L · Reversibility easy/hard. Mark which came from the user's answers vs. recommended defaults.

## Setup & commands
Install · env var names (not values) · run dev · test · lint/typecheck · build · branch name (`git init` if greenfield). Quick: 3 lines is fine. Rollback = commit per phase; say so.

## Risks & failure modes        <!-- Standard / Deep -->
| Failure mode | Impact | Mitigation | Designed? |
"We'll handle it" is not designed — either design it in a phase or mark it a non-goal.
Three lines: most likely to go wrong · most catastrophic · phase most likely underestimated.

## Innovations                  <!-- only if the brief invites it -->
CORE (lands in phase N) · STRETCH (after MVP) · CUT (why). Test for CORE: visible in a demo, not invisible plumbing.

## Phases
Ordered: scaffold → riskiest unknown → core path → edges → polish. Types/schema before consumers.

### Phase N — <name>   (Size: S/M/L/XL)
**Goal:** one sentence.
**Depends on:** phase(s) or "none".
**Touches:** `path/one.ts`, `path/two.tsx` (create/modify/delete)
**Requirements**
- [ ] concrete, checkable requirement
**Tests** — named cases, not counts: happy path · one edge · one error; file `path/x.test.ts`
**Acceptance** — observable conditions that prove the phase is done (include the `command` to run)

## Requirements trace           <!-- Standard / Deep -->
| Brief requirement (quote) | Phase | Test |
Every line of the brief maps somewhere or is listed under Non-goals with a reason.

## Non-goals
What we are explicitly not doing, and why.

## Challenge                    <!-- Quick: self-pass; Standard/Deep: Challenger verdicts applied -->
`assumption → failure scenario → fix applied` × 3 (Quick). Standard/Deep: list BLOCKERs received and the fix applied to each.

## Handoff prompt
See agent-prompts.md#handoff — paste the filled block here.
```
