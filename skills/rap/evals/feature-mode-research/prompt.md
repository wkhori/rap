---
name: feature-mode-research
tags: [research, feature, expensive]
plugins: ["../.."]
runs: 2
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Bash, Write, Edit, Agent, AskUserQuestion, WebSearch, WebFetch, Skill, TodoWrite]
---
rap Add full-text search across notes to this API, plus tag support so notes can be filtered by tag. Work autonomously — don't ask me questions, decide and annotate your assumptions.
