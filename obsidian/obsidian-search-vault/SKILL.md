---
name: obsidian-search-vault
description: Search the Obsidian Zettelkasten vault using qmd hybrid search (BM25 + vector + LLM re-ranking). Use when the user wants to find notes, quotes, people, books, literature notes, permanent notes, or any content in their personal knowledge base.
allowed-tools: Bash(qmd*)
---

# Search Vault

Search the user's Obsidian Zettelkasten using `qmd`. The user's query is passed as arguments to `/obsidian-search-vault`.

## Argument parsing

The argument string may contain:

- A query (required): any free-form text
- `-c <collection>`: restrict search to a collection; repeat the flag for several
  (`-c quotes -c people`). A comma-separated list is **not** supported and fails with
  `Collection not found: quotes,people`.
- `--full`: fetch and display the full content of the top result
- `-n <num>`: number of results (default: 5)
- `--bm25`: use fast keyword-only search instead of hybrid
- `--vector`: use pure vector search instead of hybrid

If no arguments are provided, ask the user what they want to search for.

## Collections

The vault is indexed one collection per folder. Sizes are indicative, not exact.

| Name               | Folder                         | Contents                                                    | Files |
| ------------------ | ------------------------------ | ----------------------------------------------------------- | ----: |
| `permanent`        | `04 Permanent`                 | Evergreen atomic Zettelkasten notes — the core of the vault |  3900 |
| `quotes`           | `03 Resources/Zitate`          | Quotations with their author and source                     |  2000 |
| `areas`            | `02 Areas`                     | Ongoing areas: essays, fitness, languages, work             |   520 |
| `daily`            | `06 Daily`                     | Daily journal entries: read, watched, trained, thought      |   270 |
| `people`           | `03 Resources/Personen`        | Biographical notes on real and fictional persons            |   155 |
| `moc`              | `00 Maps of Content`           | Maps of Content — thematic navigation hubs                  |   140 |
| `literature-notes` | `03 Resources/Literatur Notes` | Notes from books, talks, articles and videos                |   140 |
| `podcasts`         | `03 Resources/Podcasts`        | Podcast episodes and shows, with guests and topics          |    76 |
| `archives`         | `07 Archives`                  | Completed projects and retired MOCs                         |    63 |
| `projects`         | `01 Projects`                  | Active projects, including their mirrored Linear tickets    |    58 |
| `books`            | `03 Resources/Bücher`          | Book notes with metadata, rating and reading progress       |    48 |
| `development`      | `03 Resources/Entwicklung`     | Software development reference: languages, tools, config    |    48 |
| `series`           | `03 Resources/Serien`          | TV series, with episodes watched                            |    46 |
| `prompts`          | `03 Resources/Prompts`         | AI prompts kept for reuse                                   |    25 |
| `lyrics`           | `03 Resources/Lyrics`          | Song lyrics and poems                                       |    23 |
| `companies`        | `03 Resources/Firmen`          | Companies and organizations                                 |    18 |
| `products`         | `03 Resources/Produkte`        | Products and tools in use                                   |    11 |
| `movies`           | `03 Resources/Filme`           | Movie notes with metadata and rating                        |     9 |
| `fleeting`         | `05 Fleeting`                  | Temporary notes not yet worked into permanent ones          |     7 |
| `countries`        | `03 Resources/Länder`          | Countries, with their politics, history and culture         |     3 |
| `clippings`        | `03 Resources/Clippings`       | Articles clipped from the web and kept verbatim             |     1 |
| `philosophy`       | `03 Resources/Philosophie`     | Philosophical source texts                                  |     1 |
| `neovim`           | `03 Resources/Neovim`          | Neovim configuration and shortcuts                          |     1 |

Not indexed, so never searchable: `99 Meta/` (templates, scripts, the category registry) and
`pages/`. Read those with `Read` when you need them.

`03 Resources/Städte`, `Orte` and `Reisen` are configured but hold no notes yet, so no `cities`,
`places` or `trips` collection exists. They appear on their own once notes arrive and the
collections are re-registered.

Because `quotes` is a quarter of the corpus, an unscoped search tends to return quotes. When the
user is after ideas rather than aphorisms, scope with `-c permanent -c moc -c literature-notes`.

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

# Several collections at once — repeat -c, never comma-separate
qmd query "<query>" -c permanent -c moc -c literature-notes

# Fetch full note content
qmd get "qmd://books/Atlas Shrugged.md"   # quote it — most titles contain spaces
qmd get '#6e813e'                         # or by the docid shown in results

# List files in a collection
qmd ls quotes

# What the index currently holds
qmd collection list
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

## When a collection is missing

If a search fails with `Collection not found`, the index predates the per-folder split. Check
with `qmd collection list`; if it shows a single `zettelkasten` collection, the machine has not
been set up yet — re-register them from the seiza project:

```bash
qmd collection remove zettelkasten
cd ~/Code/personal/obsidian/seiza && pnpm qmd:setup --global --update
```
