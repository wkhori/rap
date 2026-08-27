# Example output

`quick-tier-plan.md` is real, unedited output — the `plan-executability` eval case run
through `evals/run_local.py` on 2026-08-26. Nothing was cleaned up for presentation.

The brief was one sentence:

> `/rap --quick Plan a Markdown-to-HTML converter as a small Node library: parse headings,
> bold, italics, links and code fences, and expose one render(md) function. Just decide
> anything I haven't specified — no questions.`

It cost $0.24 and took 101 seconds. Worth noticing in the output:

- Every default the skill chose for you is tagged `(assumed)` — you can scan what was
  decided on your behalf without reading the whole plan.
- HTML escaping appears as a locked security decision, though the brief never mentions it.
  That's the unknown-unknowns pass, not the model being clever.
- Each phase names real file paths, individual test cases, and a command that proves it's
  done — no "implement the parser", no "5 tests".
- It ends with a handoff prompt a fresh session can execute cold.

On the identical prompt with the skill disabled, the baseline arm wrote no plan at all — it
answered conversationally in 12 seconds. That is the +100% ablation delta in `evals/`.
