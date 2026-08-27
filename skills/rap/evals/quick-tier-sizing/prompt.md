---
name: quick-tier-sizing
tags: [tier, cheap]
plugins: ["../.."]
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Write, Edit, Agent, AskUserQuestion, WebSearch, WebFetch, Skill, TodoWrite]
---
rap build me a single-file CLI script that reads a CSV of expenses from stdin and prints the total per category. Python, no dependencies, no tests needed beyond one smoke check. Just decide anything I haven't specified.
