# AI Agent Code Skills

Custom [AI Agent Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) for personal use.

## Skills

| Skill                     | Description                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------------- |
| `obsidian-search-vault`   | Search the Obsidian Zettelkasten vault using hybrid search (BM25 + vector + LLM re-ranking) |
| `obsidian-vault-add`      | Add a new book, podcast, TV show, movie, person, country, or city to the vault              |
| `obsidian-weekly-summary` | Summarize the current week from Obsidian daily notes into a structured German recap         |
| `obsidian-process-notes`  | Process new Obsidian Web Clipper notes into the AI-maintained Wiki layer                    |
| `handoff`                 | Compact the current conversation into a structured handoff document for another agent       |
| `ia-presenter`            | Create high-quality presentations for iA Presenter (Mac) with proper Markdown syntax       |
| `presentation-zen`        | Design and deliver perfect, engaging presentations using the Presentation Zen philosophy    |

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
    "~/.claude/skills/obsidian-search-vault",
    "~/.claude/skills/obsidian-vault-add",
    "~/.claude/skills/obsidian-weekly-summary",
    "~/.claude/skills/obsidian-process-notes",
    "~/.claude/skills/handoff",
    "~/.claude/skills/ia-presenter",
    "~/.claude/skills/presentation-zen"
  ]
}
```
