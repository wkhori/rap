---
name: plan-executability
tags: [output, cheap]
plugins: ["../.."]
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Bash, Write, Edit, Agent, AskUserQuestion, WebSearch, WebFetch, Skill, TodoWrite]
---
rap --quick Plan a Markdown-to-HTML converter as a small Node library: parse headings, bold, italics, links and code fences, and expose one render(md) function. Just decide anything I haven't specified — no questions.
