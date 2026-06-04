# AGENTS.md

This file provides guidance to agentic agents when working with code in this repository.

## What this repository is

A collection of custom agentic skills for personal use.

## Skill structure

Each skill lives in its own directory:

```
skill-name/
  SKILL.md                  # Required — main skill entry point
  references/               # Optional — deep reference files loaded lazily
    *.md
  evals/
    evals.json              # Optional — eval prompts for testing the skill
```

### SKILL.md anatomy

Every `SKILL.md` must start with YAML frontmatter:

```yaml
---
name: skill-name # kebab-case, matches directory name
description: > # Trigger description — when Claude should invoke this skill.
  One or more sentences.    # Be explicit and proactive ("Do NOT wait for the user to say X").
---
```

The body contains the skill's methodology, workflows, and quick references. Keep it lean (< 500 lines). Defer deep content to `references/*.md` files that the skill loads only when needed — this is the **progressive disclosure pattern**.

## Architecture pattern

- **Dual-entry workflows**: Design from scratch vs. critique/improve existing. Both funnel to a shared checklist.
- **Exemplar anchoring**: Ground judgment toward excellence with canonical examples, not just anti-patterns.
- **Methodology-only**: Skills describe _how to think and act_, not rendering or tooling. No external dependencies.

## Adding a new skill

1. Create `skill-name/SKILL.md` with YAML frontmatter.
2. Add any reference files under `skill-name/references/`.
3. Add evals under `skill-name/evals/evals.json` (see existing evals for format).
4. Register in `README.md` skills table.
5. Register in the `settings.json` example block in `README.md`.

## Installation (for users of this repo)

```bash
npx skills add kogakure/skills
```

Or manually clone and add paths to `~/.claude/settings.json` under `"skills"`.

## skills-lock.json

Tracks externally installed skills (e.g., from `github/awesome-copilot`). Do not edit manually.
