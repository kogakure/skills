---
name: obsidian-process-notes
description: Process inbox notes into the standalone LLM Wiki vault. Use this skill whenever the user asks to process notes, process clippings, ingest clippings, build the wiki, update the wiki from new notes, run obsidian-process-notes, run obsidian-build-wiki, or maintain the AI wiki layer. It reads new files from `inbox/`, creates or updates German LLM-generated wiki pages in `wiki/`, appends to the wiki log, and moves processed notes unchanged into `sources/`.
allowed-tools: Bash(ls*), Bash(find*), Bash(wc*), Bash(grep*), Bash(qmd*), Bash(mv*), Bash(mkdir*), Read, Edit, Write
---

# obsidian-process-notes

Process inbox notes into the AI-maintained Wiki layer.

This skill operates on the standalone LLM Wiki vault at
`~/Code/personal/obsidian/llm-wiki`.

**Safety:** Never touch `~/Code/personal/obsidian/zettelkasten/` or any path
outside the `llm-wiki` vault.

## Core Paths

All paths are relative to `~/Code/personal/obsidian/llm-wiki/`.

- Inbox (unprocessed): `inbox/`
- Processed sources: `sources/`
- Source assets: `sources/assets/`
- Wiki output: `wiki/`
- Wiki assets: `wiki/assets/`
- Navigation index: `meta/Index.md`
- Operational log: `meta/Wiki-Log.md`
- Agent rules: `.agents/wiki.md`
- Wiki note template: `meta/templates/Wiki Note.md`
- Source note template: `meta/templates/Source Note.md`

## Trigger Arguments

Accept natural language requests and slash-style phrases such as:

- `obsidian-process-notes`
- `obsidian-build-wiki`
- `process new notes`
- `process clippings`
- `ingest the new inbox notes`
- `build out the wiki from inbox`

If the user names a specific file, process only that file. If they give a
limit such as "process 3 notes", process the oldest or first listed matching
unprocessed notes unless they specify another priority. If they do not
specify scope, list available inbox notes and process a small batch that is
reasonable for the current turn.

## Non-Negotiable Rules

- Write content only inside `wiki/` and `meta/`.
- Do not edit existing notes in `sources/` or `inbox/`.
- The only permitted file move is `inbox/X.md` → `sources/X.md`.
- Use `meta/templates/Wiki Note.md` as the frontmatter basis for every
  new wiki page. Use `type: Wiki` — not `type: Note`.
- Do not use hard line-breaks in paragraphs or lists unless absolutely needed.
  Keep a block of text as one coherent block in Markdown.
- Write wiki note bodies exclusively in German. Use Umlauts and German
  special characters (ä, ö, ü, ß instead of ae, oe, ue, ss), in text
  and filenames.
- For important terms, add the English term in parentheses after the German
  translation, for example `Abruf (retrieval)`.
- Add `🤖` to the `tags` field of every LLM-generated wiki page.
- Preserve uncertainty, contradictions, and missing context. Do not smooth
  over disagreement between sources.
- Wikilinks to non-existing notes are allowed. Cross-vault links to the
  Zettelkasten will appear unresolved — that is acceptable.

## Workflow

### 1. Load Operating Context

Read these files first:

1. `.agents/wiki.md`
2. `meta/Index.md`
3. `meta/Wiki-Log.md`

Then read any relevant wiki pages before writing.

### 2. Identify Unprocessed Notes

Find Markdown files directly under `inbox/`.

```bash
find ~/Code/personal/obsidian/llm-wiki/inbox -maxdepth 1 -name "*.md"
```

If no inbox notes exist, say so briefly and stop.

### 3. Read and Triage Each Note

For each selected note:

- Identify title, source URL, author, date if available, and central claims.
- Decide whether the note needs:
  - a source page,
  - updates to existing concept/entity/synthesis pages,
  - new concept/entity/synthesis pages,
  - a contradiction or open-question note in an existing page.
- Prefer integrating into existing wiki pages over creating duplicates.

### 4. Write Wiki Updates

For each new wiki page, use this frontmatter shape:

```yaml
---
type: Wiki
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

Use German headings and prose. Keep pages concise but specific enough that
future agents can update them without re-reading every raw source.

Recommended sections by page type:

- Source page: `# Titel`, `## Kernaussagen`, `## Relevanz für das Wiki`,
  `## Verbindungen`, `## Offene Fragen`
- Concept page: `# Begriff`, `## Definition`, `## Kontext`, `## Quellenlage`,
  `## Verbindungen`, `## Offene Fragen`
- Entity page: `# Name`, `## Kurzprofil`, `## Relevanz`, `## Quellenlage`,
  `## Verbindungen`
- Synthesis page: `# These/Frage`, `## Kurzfassung`, `## Argumente`,
  `## Gegenpunkte`, `## Quellen`, `## Offene Fragen`

### 5. Update Navigation and Log

Update `meta/Index.md` when:

- a new page is created,
- a page changes category,
- an existing one-line description becomes stale,
- new important open paths appear.

Append to `meta/Wiki-Log.md` using:

```markdown
## [YYYY-MM-DD] ingest | Note Title

- Quelle verarbeitet: `inbox/Note Title.md`
- Wiki-Seiten erstellt: [[...]]
- Wiki-Seiten aktualisiert: [[...]]
- Offene Fragen/Widersprüche: ...
```

Use `query` instead of `ingest` if the user asked a question and the durable
answer was filed back into the wiki.

### 6. Move Processed Note

After wiki updates are complete, move the original note unchanged:

```bash
mv ~/Code/personal/obsidian/llm-wiki/inbox/"Note Title.md" \
   ~/Code/personal/obsidian/llm-wiki/sources/"Note Title.md"
```

Do not rewrite or normalize the note content.

### 7. Re-Index

Run `qmd update` from inside the vault root after processing:

```bash
cd ~/Code/personal/obsidian/llm-wiki && qmd update
```

If it fails, report the failure briefly. Do not let indexing failure
invalidate completed wiki work.

## Output To User

End with a compact report:

- notes processed,
- wiki pages created,
- wiki pages updated,
- notes moved to `sources/`,
- any unresolved contradictions or follow-up questions,
- whether `qmd update` succeeded.

Use clickable file links for local files when reporting results.

## Safety Checks Before Final Answer

- Confirm no files outside `wiki/` and `meta/` were edited, except for the
  explicit inbox → sources move.
- Confirm every created or updated wiki note has `tags: [🤖]` or an equivalent
  YAML list containing `🤖`.
- Confirm the processed note exists in `sources/` after moving.
- Confirm no files in `~/Code/personal/obsidian/zettelkasten/` were touched.
