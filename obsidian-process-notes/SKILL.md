---
name: obsidian-process-notes
description: Process new Obsidian Web Clipper notes into the vault's AI-maintained Wiki. Use this skill whenever the user asks to process notes, process clippings, ingest clippings, build the wiki, update the wiki from new notes, run obsidian-process-notes, run obsidian-build-wiki, or maintain the AI wiki layer. It reads new files from `03 Resources/Clippings`, creates or updates German LLM-generated wiki pages in `03 Resources/Wiki`, appends to the wiki log, and moves processed clippings unchanged into `03 Resources/Clippings/Processed`.
allowed-tools: Bash(ls*), Bash(find*), Bash(wc*), Bash(grep*), Bash(qmd*), Bash(mv*), Read, Edit, Write
---

# obsidian-process-notes

Process new Obsidian Web Clipper notes into the AI-maintained Wiki layer.

This skill belongs to the Obsidian Zettelkasten vault at
`~/Code/personal/obsidian/zettelkasten`.

## Core Paths

- Raw clippings: `03 Resources/Clippings/`
- Processed clippings: `03 Resources/Clippings/Processed/`
- Wiki: `03 Resources/Wiki/`
- Wiki index: `03 Resources/Wiki/Index.md`
- Wiki log: `03 Resources/Wiki/Wiki-Log.md`
- Wiki agent rules: `.agents/wiki.md`
- Note template basis: `99 Meta/templates/Note Template.md`

## Trigger Arguments

Accept natural language requests and slash-style phrases such as:

- `obsidian-process-notes`
- `obsidian-build-wiki`
- `process new notes`
- `process clippings`
- `ingest the new Web Clipper notes`
- `build out the wiki from clippings`

If the user names a specific clipping, process only that file. If they give a
limit such as "process 3 notes", process the oldest or first listed matching
unprocessed clippings unless they specify another priority. If they do not
specify scope, list available unprocessed clippings and process a small batch
that is reasonable for the current turn.

## Non-Negotiable Rules

- Write content only inside `03 Resources/Wiki/`.
- Do not edit existing notes outside `03 Resources/Wiki/`.
- The only permitted mutation outside the Wiki is moving a processed clipping,
  unchanged, from `03 Resources/Clippings/` to
  `03 Resources/Clippings/Processed/`.
- Use `99 Meta/templates/Note Template.md` as the frontmatter basis for every
  new Wiki note.
- Do not use hard line-breaks in paragraphs or lists unless absolutely needed, keep a block of text as one coherent block of text in Markdown
- Write Wiki note bodies exclusively in German. Use Umlauts and German special characters (ä, ö, ü, ß instead of ae, oe, ue, ss), in files and filenames
- For important terms, add the English term in parentheses after the German
  translation, for example `Abruf (retrieval)`.
- Add `🤖` to the `tags` field of every LLM-generated Wiki note.
- Preserve uncertainty, contradictions, and missing context. Do not smooth over
  disagreement between sources.
- Link freely to existing vault notes outside the Wiki, but do not edit them.
- It is allowed to create wikilinks to non-existing future notes.

## Workflow

### 1. Load Operating Context

Read these files first:

1. `.agents/wiki.md`
2. `03 Resources/Wiki/Index.md`
3. `03 Resources/Wiki/Wiki-Log.md`

Then read any relevant Wiki pages from the index before writing.

### 2. Identify Unprocessed Clippings

Find Markdown files directly under `03 Resources/Clippings/`, excluding
`03 Resources/Clippings/Processed/`.

Prefer `find` or `ls` for file discovery. Use `grep` or `qmd` only when useful
for content search.

If no unprocessed clippings exist, say so briefly and stop.

### 3. Read and Triage Each Clipping

For each selected clipping:

- Identify title, source URL, author, date if available, and central claims.
- Decide whether the clipping needs:
  - a source page,
  - updates to existing concept/entity/synthesis pages,
  - new concept/entity/synthesis pages,
  - a contradiction or open-question note in an existing page.
- Prefer integrating into existing Wiki pages over creating duplicate pages.

### 4. Write Wiki Updates

For each new Wiki page, use this frontmatter shape:

```yaml
---
type: Note
created: YYYY-MM-DDTHH:mm
updated: YYYY-MM-DDTHH:mm
aliases:
tags:
  - 🤖
urls:
related:
authors:
sources:
year:
reference:
---
```

Use German headings and prose. Keep pages concise enough to remain useful, but
specific enough that future agents can update them without re-reading every
raw source.

Recommended sections by page type:

- Source page: `# Titel`, `## Kernaussagen`, `## Relevanz fuer das Wiki`,
  `## Verbindungen`, `## Offene Fragen`
- Concept page: `# Begriff`, `## Definition`, `## Kontext`, `## Quellenlage`,
  `## Verbindungen`, `## Offene Fragen`
- Entity page: `# Name`, `## Kurzprofil`, `## Relevanz`, `## Quellenlage`,
  `## Verbindungen`
- Synthesis page: `# These/Frage`, `## Kurzfassung`, `## Argumente`,
  `## Gegenpunkte`, `## Quellen`, `## Offene Fragen`

### 5. Update Navigation and Log

Update `03 Resources/Wiki/Index.md` when:

- a new page is created,
- a page changes category,
- an existing one-line description becomes stale,
- new important open paths appear.

Append to `03 Resources/Wiki/Wiki-Log.md` using:

```markdown
## [YYYY-MM-DD] ingest | Clipping Title

- Quelle verarbeitet: `03 Resources/Clippings/Clipping Title.md`
- Wiki-Seiten erstellt: [[...]]
- Wiki-Seiten aktualisiert: [[...]]
- Offene Fragen/Widersprueche: ...
```

Use `query` instead of `ingest` if the user asked a question and the durable
answer was filed back into the Wiki.

### 6. Move Processed Clipping

After Wiki updates are complete, move the original clipping unchanged to:

`03 Resources/Clippings/Processed/`

Use `mv` only for this clipping move. Do not rewrite or normalize the clipping
content.

### 7. Re-Index if Available

Try `qmd update` after processing. If it fails because of local tooling, report
the failure briefly and include the relevant cause. Do not let indexing failure
invalidate completed Wiki work.

## Output To User

End with a compact report:

- clippings processed,
- Wiki pages created,
- Wiki pages updated,
- clippings moved,
- any unresolved contradictions or follow-up questions,
- whether `qmd update` succeeded.

Use clickable file links for local files when reporting results.

## Safety Checks Before Final Answer

- Confirm no files outside `03 Resources/Wiki/` were edited, except
  `AGENTS.md`, `CLAUDE.md`, `.agents/`, or the explicit processed clipping
  move if the current task asked for setup rather than ingestion.
- Confirm every created or updated Wiki note has `tags: [🤖]` or an equivalent
  YAML list containing `🤖`.
- Confirm the processed clipping still exists in `Processed/` after moving.
