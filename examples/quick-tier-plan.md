# Plan: Markdown-to-HTML converter (small Node library)

**Mode:** greenfield · **Size:** S · **Tier:** Quick (forced by `--quick`)
**Run dir:** `docs/plans/2026-08-26-md-to-html-lib/`

## Summary

A zero-dependency Node library exposing one function, `render(md)`, that converts a Markdown string to an HTML string. Supports: headings (`#`–`######`), bold, italics, links, and fenced code blocks. Implemented as a single-pass, regex/line-based converter — not a full CommonMark parser — since the brief scopes a small, specific feature set.

## Decisions

All items below were undetermined in the brief. Per instruction, decided directly with no question round; each tagged `(assumed)`.

- **Package name:** `md-to-html-lib` `(assumed)`
- **Module format:** ESM (`"type": "module"`, named export `render`) — matches current Node/library conventions `(assumed)`
- **Package layout:** single implementation file `src/index.js`; no build step, no bundler `(assumed)`
- **Testing:** Node's built-in `node:test` + `node:assert/strict` — keeps the library genuinely zero-dependency `(assumed)`
- **Parsing strategy:** line-oriented pass for block elements (headings, code fences, paragraphs) + regex substitution for inline elements (bold, italics, links) inside non-code lines `(assumed)`
- **Syntax supported, exactly per brief:**
  - Headings: `# H1` … `###### H6` → `<h1>`…`<h6>`
  - Bold: `**text**` and `__text__` → `<strong>`
  - Italics: `*text*` and `_text_` → `<em>`
  - Links: `[text](url)` → `<a href="url">text</a>`
  - Code fences: ```` ```[lang]\ncode\n``` ```` → `<pre><code class="language-{lang}">code</code></pre>` (lang omitted when not given)
  - Everything else: consecutive non-blank, non-block lines become one `<p>…</p>`, inline rules applied
- **Not in scope (no CLI, no lists, no blockquotes, no tables, no inline code, no nested emphasis edge cases beyond simple non-overlapping matches)** — brief lists exactly five constructs; anything else is a non-goal for this pass `(assumed)`
- **HTML escaping:** escape `&`, `<`, `>` in all input text before applying Markdown transforms, and re-decode only inside constructed tags — prevents raw HTML/script injection into output `(assumed, security default)`
- **Code fence content is escaped but not further processed** (no inline bold/italics/links inside code) — standard Markdown behavior `(assumed)`

## Setup & commands

```bash
npm init -y                 # then hand-edit package.json per below
npm test                    # runs: node --test test/
```

`package.json` fields to set: `"name": "md-to-html-lib"`, `"type": "module"`, `"main": "src/index.js"`, `"exports": "./src/index.js"`, `"scripts": {"test": "node --test test/"}`. No dependencies or devDependencies.

## Phases

### Phase 1 — Scaffold (S)
- Create `package.json` (fields above), `src/index.js` (empty `export function render(md) {}`), `test/render.test.js` (empty), `README.md` (usage stub).
- Acceptance: `npm test` runs (0 tests, exits 0).

### Phase 2 — Block elements: headings, code fences, paragraphs (M)
- In `src/index.js`, implement line-splitting logic: detect fenced code blocks first (```` ``` ```` … ```` ``` ````, extract optional language, HTML-escape content verbatim, emit `<pre><code>`), then detect heading lines (`^#{1,6}\s+`), then group remaining non-blank lines into paragraphs.
- Tests in `test/render.test.js`:
  - `render('# Title')` → `'<h1>Title</h1>'`
  - `render('###### Deep')` → `'<h6>Deep</h6>'`
  - `render('plain text')` → `'<p>plain text</p>'`
  - ` ```js\nconst x = 1;\n``` ` → `<pre><code class="language-js">const x = 1;</code></pre>`
  - fence with no language → `<pre><code>...</code></pre>` (no class attr)
  - `render('<script>alert(1)</script>')` → tags escaped as text inside `<p>`
- Acceptance: `npm test` — all above pass.

### Phase 3 — Inline elements: bold, italics, links (M)
- Add an `applyInline(text)` helper run over paragraph/heading text (not code fence content): links first (`\[([^\]]+)\]\(([^)]+)\)` → `<a href="$2">$1</a>`), then bold (`\*\*(.+?)\*\*` and `__(.+?)__` → `<strong>$1</strong>`), then italics (`\*(.+?)\*` and `_(.+?)_` → `<em>$1</em>`) — bold patterns matched before italics so `**x**` doesn't get parsed as nested `*`.
- Tests:
  - `render('**bold**')` → `'<p><strong>bold</strong></p>'`
  - `render('*italic*')` → `'<p><em>italic</em></p>'`
  - `render('__bold__')` and `render('_italic_')` variants
  - `render('[Claude](https://claude.ai)')` → `'<p><a href="https://claude.ai">Claude</a></p>'`
  - `render('# **Bold** heading')` → inline rules applied inside headings too
  - mixed: `render('a **b** and *c* and [d](e)')` → all three applied in one paragraph
- Acceptance: `npm test` — all pass.

### Phase 4 — Polish (S)
- Handle edge cases: empty input (`render('')` → `''`), multiple blank lines between paragraphs, trailing newline in input, unterminated code fence (treat rest of doc as code rather than throwing).
- Finalize `README.md`: install/usage snippet (`import { render } from 'md-to-html-lib'`), supported syntax table, explicit non-goals list.
- Acceptance: `npm test` — full suite green; manual `node -e "import('./src/index.js').then(m => console.log(m.render('# Hi\n\nSome **bold** and [a link](https://x.com)')))"` produces well-formed HTML.

## Challenge

- **Assumption:** regex-based bold/italic won't handle nesting or overlap correctly (e.g. `*a **b** c*`) → **failure scenario:** malformed or swapped tags on adjacent/nested emphasis → **fix applied:** scope explicitly excludes nested-emphasis correctness (Phase 3 test set only covers non-overlapping cases); documented as a non-goal in README so it's a known, not silent, limitation.
- **Assumption:** naive HTML escaping could double-escape entities inside constructed `<a href>` URLs → **failure scenario:** a URL containing `&` (e.g. `?a=1&b=2`) renders as `&amp;amp;` → **fix applied:** escape body text before inline substitution, but insert `href` URLs raw (only escaping `"` inside the URL) rather than passing already-escaped text back through the link regex's replacement.
- **Assumption:** paragraph grouping might swallow heading/code-fence lines if block-detection order is wrong → **failure scenario:** a `#` line inside surrounding prose gets merged into a paragraph instead of becoming a heading → **fix applied:** Phase 2 processes the document as an explicit line-by-line state machine (in-fence / heading / paragraph-buffer), each line classified once, in a fixed precedence order (fence > heading > paragraph), rather than global regex replace over the whole string.

## Handoff prompt

You are implementing `md-to-html-lib`, a small zero-dependency Node library. Full plan: `docs/plans/2026-08-26-md-to-html-lib/plan.md` (this file). Read it in full before starting — all decisions are locked, no open questions remain.

Build in order: Phase 1 (scaffold) → Phase 2 (block elements: headings, code fences, paragraphs) → Phase 3 (inline elements: bold, italics, links) → Phase 4 (edge cases + README). Each phase lists its own test cases and an acceptance command (`npm test`, plus one manual check in Phase 4) — implement the code, write the named tests into `test/render.test.js`, and confirm the acceptance command passes before moving to the next phase.

Constraints: ESM module, single file `src/index.js`, one exported function `render(md)`, zero runtime dependencies, `node:test`/`node:assert/strict` for tests only. Do not add CLI, lists, blockquotes, tables, or inline-code support — those are explicit non-goals. Escape raw HTML in input text. Do not ask clarifying questions; if you hit an undocumented edge case, pick the simplest behavior consistent with the "Challenge" section above and note it in the README's non-goals list.
