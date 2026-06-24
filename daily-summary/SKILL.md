---
name: daily-summary
description: >
  Searches all Claude Code sessions of the current day and produces a short
  German bullet list summary of all tasks completed, grouped by project or
  repository. Invoke whenever the user says "was habe ich heute gemacht",
  "Tagesrückblick", "daily summary", "heute erledigt", "summarize today's work",
  "show today's sessions", "what did I do today", "kurze Zusammenfassung heute",
  or asks for any daily recap of work done across sessions.
allowed-tools: Bash(python3*), mcp__plugin_claude-mem_mcp-search__timeline, mcp__plugin_claude-mem_mcp-search__get_observations
---

# Daily Summary Skill

Produce a short German bullet list of today's work across all Claude Code sessions, grouped by project or repository.

## Step 1: Get today's date

```bash
python3 -c "from datetime import date; print(date.today().isoformat())"
```

## Step 2: Load the memory tools

Use ToolSearch to load the required tool schemas in one call:

ToolSearch with query `select:mcp__plugin_claude-mem_mcp-search__search,mcp__plugin_claude-mem_mcp-search__get_observations`

## Step 3: Fetch today's observations

Call `mcp__plugin_claude-mem_mcp-search__search` with `dateStart` and `dateEnd` both set to today's ISO date (e.g. `2026-06-24`), `limit` 100, `orderBy` `date_asc`. The tool returns a list of observations for the day.

Focus on actionable observation types:

| Symbol | Type      | Include?                             |
| ------ | --------- | ------------------------------------ |
| ✓      | Change    | Yes                                  |
| ◆      | Feature   | Yes                                  |
| ●      | Bug fix   | Yes                                  |
| ↻      | Refactor  | Yes                                  |
| ⚖      | Decision  | Yes if architectural/significant     |
| ○      | Discovery | Only if no other entries for project |
| ⚠/⚷    | Security  | Yes                                  |

Session entries (prefix `S`) provide the headline title — use these to name the project if content is ambiguous.

## Step 4: Group by project

Map each session/observation to a project or repository. Common signals:

- Repo or package name in the session title (e.g., `app-startpage`, `skills`, `translations-app`)
- File paths or package names mentioned in observation text
- Branch names or PR references

If a session spans multiple repos, split into separate bullets per repo.

## Step 5: Produce the German summary

Output directly in the conversation — no file needed.

### Format

```
## Tagesrückblick — DD. Monat YYYY

- [x] **Projektname**: Ein Satz im Perfekt, was heute erledigt wurde.
- [x] **Projektname**: Ein Satz im Perfekt, was heute erledigt wurde.
```

### Rules

- One checked off bullet per project — dense, not exhaustive
- German Perfekt tense (`wurde X implementiert`, `wurden Y Fehler behoben`)
- Bold the project/repo name
- Date in German long form: `24. Juni 2026`
- Omit projects where only trivial formatting or config changes happened — unless that was the only work
- If no sessions found: output `Heute wurden keine Claude-Code-Sitzungen aufgezeichnet.`
- Max one sentence per bullet — if more happened, pick the most significant item
