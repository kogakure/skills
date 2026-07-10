# AI Agent Code Skills

Custom [AI Agent Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) for personal use.

## Skills

| Skill                                    | Description                                                                                          |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `obsidian/obsidian-search-vault`          | Search the Obsidian Zettelkasten vault using hybrid search (BM25 + vector + LLM re-ranking)           |
| `obsidian/obsidian-vault-add`             | Add a new book, podcast, TV show, movie, person, country, or city to the vault                        |
| `obsidian/obsidian-weekly-summary`        | Summarize the current week from Obsidian daily notes into a structured German recap                   |
| `obsidian/obsidian-process-notes`         | Process new Obsidian Web Clipper notes into the AI-maintained Wiki layer                              |
| `obsidian/obsidian-process-pages`         | Batch-clean and sort old unsorted notes in the vault's `pages/` archive into `04 Permanent/`/`03 Resources/` |
| `misc/handoff`                            | Compact the current conversation into a structured handoff document for another agent                |
| `misc/daily-summary`                      | Search all Claude Code sessions of the current day and produce a short German bullet list summary of tasks completed, grouped by project/repo |
| `presentations/ia-presenter`              | Create high-quality presentations for iA Presenter (Mac) with proper Markdown syntax                  |
| `presentations/presentation-zen`          | Design and deliver perfect, engaging presentations using the Presentation Zen philosophy              |
| `infographics/tufte`                      | Apply Edward Tufte's information design principles to create, critique, or improve any chart, graph, infographic, dashboard, or data visualization |

## Installation

### Using npx (recommended)

```bash
npx skills add kogakure/skills
```

### Manual

Clone this repo and add the skills to your Claude Code configuration:

```bash
git clone https://github.com/kogakure/skills ~/.claude/skills
```

Then register them in your `~/.claude/settings.json`:

```json
{
  "skills": [
    "~/.claude/skills/obsidian/obsidian-search-vault",
    "~/.claude/skills/obsidian/obsidian-vault-add",
    "~/.claude/skills/obsidian/obsidian-weekly-summary",
    "~/.claude/skills/obsidian/obsidian-process-notes",
    "~/.claude/skills/obsidian/obsidian-process-pages",
    "~/.claude/skills/misc/handoff",
    "~/.claude/skills/misc/daily-summary",
    "~/.claude/skills/presentations/ia-presenter",
    "~/.claude/skills/presentations/presentation-zen",
    "~/.claude/skills/infographics/tufte"
  ]
}
```
