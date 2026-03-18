# Claude Code Skills

Custom [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills) for personal use.

## Skills

### `search-vault`

Search the Obsidian Zettelkasten vault using `qmd` hybrid search (BM25 + vector + LLM re-ranking).

**Usage:** `/search-vault <query> [-c <collection>] [-n <num>] [--full] [--bm25] [--vector]`

**Examples:**
```
/search-vault stoicism and virtue
/search-vault "Marcus Aurelius" -c people
/search-vault recent books on productivity -c books --full
/search-vault nietzsche -n 10 --bm25
```

**Collections:** `quotes`, `people`, `books`, `literature-notes`, `moc`, `permanent-notes`, `unsorted-notes`, `movies`, `lyrics`

---

### `vault-add`

Add a new book, podcast, TV show, or movie to the vault. Creates the resource note from a template, fills in metadata from the web, downloads cover art, updates today's daily note, and re-indexes `qmd`.

**Usage:** `/vault-add <type> "<title>" [extra info]`

**Examples:**
```
/vault-add book "The Not So Wild, Wild West"
/vault-add podcast "Kontrafunk - Die Sonntagsrunde"
/vault-add show "Silicon Valley" 1.1
/vault-add movie "Dune"
```

**Types:** `book`, `podcast`, `show` (or `tv`), `movie`

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
    "~/.claude/skills/search-vault",
    "~/.claude/skills/vault-add"
  ]
}
```
