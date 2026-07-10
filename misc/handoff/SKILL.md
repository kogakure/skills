---
name: handoff
description: >
  Compacts the current conversation into a structured handoff document so another
  agent (or a new session) can immediately pick up where this one left off.
  Use this skill whenever the user says "handoff", "hand off", "create a handoff",
  "summarize for next agent", "new session", "pass context", "fresh context",
  "write a handoff doc", or anything that signals wanting to transfer work to a
  new agent. Also trigger proactively when the conversation is getting very long
  and the user mentions starting fresh or switching models.
---

# Handoff Skill

Your job is to produce a **handoff document** — a compact, self-contained markdown
file that a brand-new agent (with zero context from this conversation) can read
and immediately continue the work effectively.

## Why this matters

Agents lose context across sessions. A good handoff document lets work continue
without the incoming agent asking "what are we doing?" or making decisions the
current session already resolved. Everything the new agent needs should be in the
document; nothing else should be assumed.

## What to extract from the conversation

Read the full conversation carefully. Pull out:

1. **Goal** — What the user is ultimately trying to accomplish. One sentence.
   If the goal shifted during the conversation, note the current goal.

2. **Context** — Project name, directory, tech stack, key constraints, relevant
   background the user shared. Keep it tight — only what shapes decisions.

3. **What's been done** — Concrete completed actions: files created/edited,
   commands run, features implemented, PRs opened. Reference specific file paths
   and line numbers when known.

4. **Key decisions made** — Choices that were discussed and settled. Include the
   _reason_ — "we chose X because Y" — so the new agent doesn't re-litigate them.

5. **Current state** — Where things stand right now. What's working, what's
   broken, what's half-done. If there are uncommitted changes or a partial
   implementation, say so.

6. **Open items / blockers** — What's unresolved, what's blocked and why,
   what the user was unsatisfied with.

7. **Next steps** — Specific, ordered actions for the incoming agent to take.
   Write these as imperatives ("Run X", "Edit Y at line Z", "Ask the user about W").
   Be concrete enough that the agent can start immediately.

8. **User preferences observed** — Communication style, things the user
   corrected or pushed back on, workflow preferences. This helps the new agent
   avoid the same friction.

9. **Key files** — A short list of the most important files, with one-line
   descriptions. Not every file touched — only the ones that matter for next steps.

## Output format

Write the handoff document in this exact structure (use these headings):

```markdown
# Handoff: [brief description of the work]

**Date:** [today's date]
**Project:** [project name or path]
**Status:** [one of: In Progress / Blocked / Ready for Review / Done]

## Goal

[One to two sentences.]

## Context

[Bullet list of key background — project, tech stack, constraints.]

## What's Been Done

[Bullet list. Specific. File paths, commands, decisions.]

## Key Decisions

[Bullet list. Each item: decision + reason.]

## Current State

[Short description of where things stand. What's working, what's not, what's partial.]

## Open Items

[Bullet list. Include blockers.]

## Next Steps

1. [First thing the agent should do]
2. [Second thing]
3. [...]

## User Preferences

[Bullet list. Things the user corrected, likes, dislikes, or prefers about working style.]

## Key Files

| File           | Purpose      |
| -------------- | ------------ |
| `path/to/file` | what it does |
```

## Calibrate length to complexity

- Short session (< 20 turns, single task): aim for ~200–350 words
- Medium session: 350–600 words
- Long session with many threads: 600–900 words. Do NOT exceed 1000 words — if it
  can't fit, you're summarizing at too fine a grain. Prioritize next steps, current
  state, and key decisions over exhaustive history.

## Delivery

1. Write the handoff document to a file: `handoff-YYYYMMDD-TITLE.md` in the current working
   directory (or wherever the project files are).

2. Also print the full content in the conversation so the user can see and copy it.

3. After printing, say one sentence about what the incoming agent should do first.

## What NOT to include

- Conversation filler, pleasantries, or anything that doesn't help the new agent act
- Duplicate information (say each thing once)
- Long code blocks — reference the file and line instead
- Speculation about future work beyond what the user discussed
- Tool outputs or command results verbatim — summarize them
