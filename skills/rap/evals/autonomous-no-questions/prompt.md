---
name: autonomous-no-questions
tags: [guardrail, cheap]
plugins: ["../.."]
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Write, Edit, Agent, AskUserQuestion, WebSearch, WebFetch, Skill, TodoWrite]
---
/rap Plan a URL shortener service: create short codes, redirect, and count hits. Work autonomously — do not ask me any questions, just decide and annotate what you assumed.
