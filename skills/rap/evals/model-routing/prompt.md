---
name: model-routing
tags: [routing, expensive]
plugins: ["../.."]
runs: 2
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Bash, Write, Edit, Agent, AskUserQuestion, WebSearch, WebFetch, Skill, TodoWrite]
---
/rap --standard Design a multi-tenant webhook delivery service: accept events from customer apps, fan them out to subscriber endpoints with retries and exponential backoff, expose delivery logs per tenant, and guarantee at-least-once delivery. Work autonomously — no questions, decide and annotate.
