---
name: search-vault
description: Search the Obsidian Zettelkasten vault using qmd hybrid search (BM25 + vector + LLM re-ranking). Use when the user wants to find notes, quotes, people, books, literature notes, permanent notes, or any content in their personal knowledge base.
allowed-tools: Bash(qmd*)
---

# Search Vault

Search the user's Obsidian Zettelkasten using `qmd`. The user's query is passed as arguments to `/search-vault`.

## Argument parsing

The argument string may contain:

- A query (required): any free-form text
- `-c <collection>`: restrict search to a specific collection
- `--full`: fetch and display the full content of the top result
- `-n <num>`: number of results (default: 5)
- `--bm25`: use fast keyword-only search instead of hybrid
- `--vector`: use pure vector search instead of hybrid

If no arguments are provided, ask the user what they want to search for.

## Collections

| Name               | Contents                                                              |
| ------------------ | --------------------------------------------------------------------- |
| `quotes`           | Short quotes and aphorisms from philosophers, scientists, politicians |
| `people`           | Biographical notes on real and fictional persons                      |
| `books`            | Book notes with ratings and summaries                                 |
| `literature-notes` | Notes from articles, videos, and podcasts                             |
| `moc`              | Maps of Content — thematic navigation hubs                            |
| `permanent-notes`  | Evergreen atomic Zettelkasten notes                                   |
| `unsorted-notes`   | Large mixed collection (5000+ notes)                                  |
| `series`           | TV series notes                                                       |
| `movies`           | Movie notes                                                           |
| `lyrics`           | Lyrics and poems                                                      |
| `clippings`        | Web clippings and saved articles                                      |
| `podcasts`         | Podcast notes                                                         |
| `companies`        | Company and business notes                                            |
| `prompts`          | AI prompt notes                                                       |
| `countries`        | Country notes                                                         |
| `cities`           | City notes                                                            |
| `places`           | Place notes (restaurants, cafes, locations)                           |
| `trips`            | Trip and travel notes                                                 |

## Steps

1. Parse the query and flags from the user's arguments
2. Choose the right command (default: `qmd query` for hybrid search)
3. Run the search and display results clearly
4. If `--full` is specified, or the user asks to open/read a note, fetch it with `qmd get <docid>`
5. If results are poor, suggest alternative collections or rephrase

## Commands

```bash
# Hybrid search — query expansion + BM25 + vector + LLM re-ranking (best quality)
qmd query "<query>"
qmd query "<query>" -c <collection>
qmd query "<query>" -n 10

# Fast BM25 keyword search (instant, no models)
qmd search "<query>"
qmd search "<query>" -c <collection>

# Pure vector similarity search
qmd vsearch "<query>"

# Fetch full note content
qmd get qmd://collection/filename.md

# List files in a collection
qmd ls <collection>
```

## Output format

Present results as a clear numbered list:

- **Title** with score badge
- Collection name
- Relevant excerpt from the note
- `qmd get` path for reference

After showing results, offer to:

- Fetch the full content of any result
- Search a specific collection
- Try a different query
