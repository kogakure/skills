---
name: obsidian-vault-add
description: Add a new book, podcast, TV show, or movie to the Obsidian Zettelkasten vault. Creates the resource note from a template, fills in metadata from the web, downloads cover art, updates today's daily note, and re-indexes qmd. Use when the user says "add book", "add podcast", "add show", "add movie", or wants to log media in their vault.
allowed-tools: Bash(obsidian*), Bash(python3*), Bash(qmd*), Bash(ls*), Bash(wc*), WebSearch, Read, Edit, Write
---

# vault-add

Add a new resource (book, podcast, TV show, or movie) to the vault: create the note, download cover art, update today's daily note, and re-index.

## Argument parsing

Arguments: `<type> <title> [extra info]`

- `type` (required): `book`, `podcast`, `show` (or `tv`), `movie`
- `title` (required): the resource title
- `extra info` (optional): author, host, episode number, season/episode, etc.

Examples:

- `/vault-add book "Atlas Shrugged"`
- `/vault-add podcast "Aethervox Ehrenfeld"`
- `/vault-add show "Silicon Valley" 1.1`
- `/vault-add movie "Dune"`

If type or title is missing, ask the user before proceeding.

## Step-by-step workflow

### 1. Web search for metadata

Search for the title to gather:

**Book**: title, subtitle, authors, published year, genres, pages, ISBN, short description (German preferred)
**Podcast**: full name, host(s), language, genres, start year, description (German preferred)
**TV show**: full name, actors, genres, network, seasons, episodes, IMDb rating, description (German preferred)
**Movie**: full name, director(s), actors, genres, year, IMDb rating, description (German preferred)

### 2. Check if note already exists

```bash
obsidian read file="<title>" 2>/dev/null | grep -Ev "^(20[0-9]{2}-|Your Obsidian)"
```

If the note already exists, inform the user and stop (unless they want to update it).

### 3. Create note from template

| Type    | Path                                 | Template           |
| ------- | ------------------------------------ | ------------------ |
| book    | `03 - Resources/Bücher/<title>.md`   | `Book Template`    |
| podcast | `03 - Resources/Podcasts/<title>.md` | `Podcast Template` |
| show    | `03 - Resources/Serien/<title>.md`   | `TV Show Template` |
| movie   | `03 - Resources/Filme/<title>.md`    | `Movie Template`   |

```bash
obsidian create path="<path>" template="<Template>" 2>/dev/null | grep -Ev "^(20[0-9]{2}-|Your Obsidian)"
```

### 4. Fill in frontmatter

Edit the note file directly (Read then Edit) — do NOT use `obsidian property:set` for list fields as it does not reliably handle arrays. Set all fields in one Edit call by replacing the entire frontmatter block.

**Book frontmatter fields**: `aliases`, `tags: [Buch]`, `photo`, `urls`, `published` (YYYY-MM-DD), `authors` (list), `genres` (list), `rating`, `pages`

**Podcast frontmatter fields**: `aliases`, `tags: [Podcast]`, `photo`, `urls`, `hosts` (list), `guests`, `genres` (list), `language`, `rating`, `status`, `started`, `ended`, `episodes`

**TV show frontmatter fields**: `aliases`, `tags: [Serie]`, `photo`, `urls`, `actors` (list), `genres` (list), `rating`, `imdb_rating`, `network`, `seasons`, `episodes`

**Movie frontmatter fields**: `aliases`, `tags: [Film]`, `photo`, `urls`, `directors` (list), `actors` (list), `genres` (list), `rating`, `imdb_rating`, `year`

Remove the `BOAT` tag from `tags` — notes with links are not BOAT.

### 5. Add description to body

After the frontmatter, add a short German-language description paragraph (2–4 sentences). Keep any template section headers (`## Zusammenfassung`, `## Kernaussagen`, `## Lieblingsfolgen`, etc.).

The image embed `![[filename.webp]]` will be added after cover download (step 6) — do not add it manually.

### 6. Download cover art

Use inline Python (not the download scripts, which require manual list editing). Use Pillow if available for WebP output, otherwise JPEG.

**Book** — Open Library by title search:

```python
import json, urllib.request, urllib.parse, io, os

query = "<title>"
url = f"https://openlibrary.org/search.json?title={urllib.parse.quote(query)}&limit=3"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 VaultBot/1.0"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())
docs = data.get("docs", [])
cover_id = next((d["cover_i"] for d in docs if d.get("cover_i")), None)
if cover_id:
    img_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
    # download and save as WebP using Pillow
```

Output path: `99 - Meta/assets/books/<title> (<first author>).webp`

**Podcast** — iTunes Search API:

```python
import json, urllib.request, urllib.parse

query = "<podcast name>"
params = urllib.parse.urlencode({"term": query, "entity": "podcast", "limit": 5})
url = f"https://itunes.apple.com/search?{params}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 VaultBot/1.0"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())
artwork = data["results"][0].get("artworkUrl600") if data["results"] else None
# download and save as WebP using Pillow
```

Output path: `99 - Meta/assets/podcasts/<title>.webp`

**TV show** — TVMaze API:

```python
import json, urllib.request, urllib.parse

query = "<show title>"
url = f"https://api.tvmaze.com/singlesearch/shows?q={urllib.parse.quote(query)}&embed=images"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 VaultBot/1.0"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())
image_url = data.get("image", {}).get("original") or data.get("image", {}).get("medium")
# download and save as WebP using Pillow
```

Output path: `99 - Meta/assets/series/<title>.webp`

**Movie** — Wikipedia REST API (search for poster):

```python
import json, urllib.request, urllib.parse

title = "<movie title>"
search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0 VaultBot/1.0"})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())
image_url = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
# download and save as WebP using Pillow
```

Output path: `99 - Meta/assets/movies/<title>.webp`

**After successful download:**

1. Set `photo: <filename>` in frontmatter (Edit the file)
2. Add `![[<filename>]]` to the note body using Edit (insert before the description paragraph) — do NOT use `obsidian prepend`, as it escapes the `!` and produces `\![[...]]`

If cover download fails, note it to the user and continue without a photo.

Also add the new entry to the appropriate download script so future re-runs include it:

| Type    | Script                                         |
| ------- | ---------------------------------------------- |
| book    | `99 - Meta/scripts/download-book-covers.py`    |
| podcast | `99 - Meta/scripts/download-podcast-covers.py` |
| show    | `99 - Meta/scripts/download-series-covers.py`  |
| movie   | `99 - Meta/scripts/download-movie-covers.py`   |

### 7. Update today's daily note

Append to today's daily note using the correct emoji and wikilink format:

| Type    | Format                                     |
| ------- | ------------------------------------------ |
| book    | `📚 [[<title>]] angefangen zu lesen (0 %)` |
| podcast | `🎙️ [[<title>]]: <episode/topic if known>` |
| show    | `📺 [[<title>]] <season>.<episode>`        |
| movie   | `🎬 [[<title>]]`                           |

```bash
obsidian daily:append content="<entry>" 2>/dev/null | grep -Ev "^(20[0-9]{2}-|Your Obsidian)"
```

If the user provided season/episode or episode title in the arguments, use it; otherwise use a sensible placeholder or ask.

### 8. Re-index qmd

```bash
qmd update && qmd embed
```

Run this after the note is created and finalized so it's immediately searchable.

### 9. Report to user

Summarize what was done:

- Note path created
- Metadata filled (list key fields)
- Cover art status (saved path or skip reason)
- Daily note entry added
- qmd indexed

## Error handling

- If note creation fails, check if the path already exists
- If cover download returns a tiny image (< 5 KB), skip it and warn the user
- If `obsidian daily:append` fails, tell the user the entry to add manually
- If `qmd embed` takes too long, run it in the background with `run_in_background: true`
