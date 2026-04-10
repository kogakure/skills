# AI Agent Code Skills

Custom [AI Agent Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) for personal use.

## Skills

| Skill                   | Description                                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------- |
| `obsidian-search-vault` | Search the Obsidian Zettelkasten vault using hybrid search (BM25 + vector + LLM re-ranking) |
| `obsidian-vault-add`    | Add a new book, podcast, TV show, movie, person, country, or city to the vault              |

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
  "skills": ["~/.claude/skills/obsidian-search-vault", "~/.claude/skills/obsidian-vault-add"]
}
```
