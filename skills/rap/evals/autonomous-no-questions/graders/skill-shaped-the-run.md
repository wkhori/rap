---
type: regex
source: {source: file, path: "**/plan.md"}
pattern: '\*\*Mode:\*\*|\bMode:\s*(greenfield|feature|revision)\b'
match: contains
---
Proof the skill actually shaped the run rather than the model free-styling a plan: the
mode/size/tier header is specific to this skill's template.

(Not a `tool_used: Skill` grader — in headless `claude -p`, the `/rap` slash form is
expanded into the prompt rather than dispatched through the Skill tool, so a Skill-tool
grader reports 0 calls even on a perfect run.)
