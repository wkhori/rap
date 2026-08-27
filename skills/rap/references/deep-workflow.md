# Deep-tier research workflow (`Workflow` runner)

Use only in **Deep** tier, and only when ≥4 independent research questions deserve adversarial verification. Otherwise spawn researchers with the Agent tool. Running this skill's instructions counts as the user's opt-in for the Workflow tool.

**Budget rule: `Q + 2·H + 1 ≤ 8`** where Q = questions, H = high-stakes questions (each gets one verifier that judges up to 2 findings — two refutation angles, not one per finding). That leaves ≥2 of the 10-cap for the Challenger and gap pass. The script throws if the plan exceeds 8 — pair questions or lower stakes until it fits, and `log()` what you dropped.

Pass `args` as `{ brief, notesPath: "<run dir>/research.md", questions: [{ id, angle, question, stakes: "high"|"low" }] }`. The lead has already created `notesPath`.

```js
export const meta = {
  name: 'rap-deep-research',
  description: 'Parallel primary-source research per question, adversarial verify on high-stakes ones, one synthesis',
  phases: [
    { title: 'Research', detail: 'one researcher per question' },
    { title: 'Verify', detail: 'refute top findings of high-stakes questions' },
    { title: 'Synthesize', detail: 'append to research.md' },
  ],
}

if (!args?.questions?.length) return { error: 'no questions supplied' }
const { brief, notesPath, questions } = args
const high = questions.filter(q => q.stakes === 'high')
const planned = questions.length + 2 * high.length + 1
if (planned > 8) throw new Error(`${planned} agents planned > 8 — pair questions or lower stakes`)
log(`planned agents: ${planned} (Q=${questions.length}, H=${high.length})`)

const FINDINGS = {
  type: 'object',
  required: ['summary', 'findings'],
  properties: {
    summary: { type: 'string' },
    findings: { type: 'array', maxItems: 4, items: { type: 'object',
      required: ['claim', 'source', 'confidence'],
      properties: {
        claim: { type: 'string' }, source: { type: 'string' },
        numbers: { type: 'string' }, gotcha: { type: 'string' },
        confidence: { type: 'string', enum: ['H', 'M', 'L'] },
      } } },
  },
}
const VERDICTS = {
  type: 'object', required: ['verdicts'],
  properties: { verdicts: { type: 'array', items: { type: 'object',
    required: ['claim', 'refuted', 'reason'],
    properties: { claim: { type: 'string' }, refuted: { type: 'boolean' }, reason: { type: 'string' }, correction: { type: 'string' } } } } },
}

const rules = `Primary sources only (official docs, source, specs, changelogs). WebSearch/WebFetch may be deferred — load via ToolSearch("select:WebSearch,WebFetch"). Every claim: URL or path:line + confidence H/M/L. Never invent a URL or number; "no data found" is a valid finding. Record versions/as-of dates. Budget ≤20 tool calls. No preamble, no questions back.`

const results = await pipeline(
  questions,
  q => agent(
    `You are a Researcher (angle: ${q.angle}) on a research-and-plan run.\nBrief:\n${brief}\n\nAnswer only: ${q.question}\n\n${rules}`,
    { label: `research:${q.id}`, phase: 'Research', schema: FINDINGS, effort: 'medium' }),
  async (r, q) => {
    if (q.stakes !== 'high') return { q, r, verdicts: [] }
    const top = r.findings.slice(0, 2)
    const pair = await parallel([0, 1].map(i => () =>
      agent(`Try to REFUTE these research claims using primary sources (refutation angle ${i + 1}: ${i ? 'look for version/date drift and contradicting official sources' : 'verify the cited source actually says this'}). Default to refuted=true if you cannot confirm.\n${JSON.stringify(top)}\nFor each: claim, refuted, reason, correction (if refuted).\n\n${rules}`,
        { label: `verify:${q.id}:${i + 1}`, phase: 'Verify', schema: VERDICTS, effort: 'medium' })))
    return { q, r, verdicts: pair.filter(Boolean).flatMap(v => v.verdicts) }
  },
)

const kept = results.filter(Boolean)
log(`${kept.length}/${questions.length} questions researched`)

const synthesis = await agent(
  `Append these research results to ${notesPath} under "## Deep research" (grouped by question; Finding · Source · Key numbers · Gotcha · Confidence; mark claims refuted by ≥1 verifier with their correction). Append with a single Bash heredoc — never Read-then-Write the file. Then return a ≤300-word summary of the facts most likely to change a decision and every contradiction with the brief.\n\nBrief:\n${brief}\n\nResults:\n${JSON.stringify(kept, null, 2)}`,
  { label: 'synthesize', phase: 'Synthesize', agentType: 'general-purpose' })

return { summary: synthesis, results: kept }
```

After it returns, continue at step 3 (Decide) of the skill with the summary; the Challenger reads `research.md`.
