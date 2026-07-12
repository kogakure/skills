---
name: obsidian-process-pages
description: >
  Batch-clean and sort old unsorted notes in the pages/ folder of the Obsidian
  Zettelkasten vault: classify each note's type (Note, Quote, Book, Person, etc.),
  rebuild frontmatter in the correct template field order, strip inline footnotes
  into structured fields (authors, year, sources, publication, published, urls,
  reference), run prettier, and move the note to its target folder. Trigger on
  "process N notes", "process N pages", "clean up pages", "sort old notes", or any
  request to work through the pages/ archive. This is NOT obsidian-process-notes
  (which builds a separate wiki vault from inbox/ clippings) — this skill sorts the
  vault's own legacy pages/ folder into 04 Permanent/ and 03 Resources/.
allowed-tools: Bash(obsidian*), Bash(python3*), Bash(prettier*), Bash(ls*), Bash(mv*), Bash(test*), Bash(grep*), Bash(wc*), Bash(qmd*), Read, Edit, Write
---

# obsidian-process-pages

Replicate the manual cleanup workflow for the vault's `pages/` archive (old,
flat, unsorted notes) so an agent can process them in batches instead of one at a time by
hand. Processes notes **alphabetically from the top of `pages/`**, in full, one at a time.

Run this skill from the vault root (the Obsidian Zettelkasten vault directory). All paths
below are relative to that root. Never read, write, or move anything outside it.

## Argument parsing

Arguments: `<N> [--dry-run] [--enrich]`

- `N` (optional, default **20**): how many notes to process this batch.
- `--dry-run`: run detection + plan the transform and destination for each note, print the
  full report, but make **no edits and no moves**. Recommend this for a user's first run.
- `--enrich` (optional, default **off**): when a referenced Person/Book/etc. note already
  exists but is malformed, fix it via the `obsidian-vault-add` skill (keeping any info
  already present in it). Never creates a new note for something that doesn't exist yet —
  that's out of scope even with `--enrich`. Leave this off unless the user explicitly asks.

Examples: `Process 20 notes`, `Process 50 pages --dry-run`, `Process 10 notes --enrich`.

If the user just says "process notes" with no number, use N=20 and tell them you did.

## Batch selection

1. List `pages/*.md` and sort alphabetically — this mirrors what the user sees at the top
   of Obsidian's file explorer.
   ```bash
   ls "pages/" | grep '\.md$' | sort
   ```
2. Skip any file that already has a `❓` tag (35+ notes are pre-tagged from earlier manual
   triage; more accumulate as this skill runs):
   ```bash
   grep -q "❓" "pages/<name>.md" && echo SKIP
   ```
3. Take the first **N** survivors. This is the batch.

There is no separate progress/state file — progress is implicit in the filesystem:
processed notes leave `pages/` (moved to their destination folder), and `❓`-tagged notes
stay behind but are always skipped on future runs. Re-running the skill is always safe.

## Per-note workflow

Process one note fully before starting the next. For each file in the batch:

### 1. Read

Read the full note (frontmatter + body).

### 2. Detect type

Default assumption: **Note** or **Quote** — these cover nearly the whole backlog. Full
heuristics (including the rarer resource types and the MOC/index trap) are in
`references/type-detection.md` — read it before classifying if the note isn't an obvious
plain Note.

Quick rule of thumb: title is `Author - Statement...`, OR the note has the `Zitat` tag, OR
the body's point is a `>` blockquote of someone else's words → **Quote**. Otherwise → **Note**.
A callout (`> [!SUMMARY]`) or an illustrative dialogue blockquote does **not** make a note a Quote.

If you cannot confidently classify → go to **Ambiguity handling** below (skip this note,
continue the batch).

### 3. Parse and remove footnotes

If the note has `[^id]` markers and a matching `[^id]: [[Author]] (YYYY): _Title_, <url>.`
definition line, extract structured data from it and delete both the marker and the
definition. Full parsing rules, multi-author splitting, and the `published`-date rule are
in `references/footnote-parsing.md` — read it whenever a note has a footnote to parse.

If a note has no footnote at all, skip this step and continue — that's the normal case for
plain evergreen notes.

If a `[^id]:` line doesn't match the expected pattern well enough to extract cleanly, don't
guess — treat this note as ambiguous (❓ + skip).

### 3b. Quote attribution line (independent of footnotes)

For every note classified `type: Quote`, `authors` **must** end up populated — this holds
whether or not the note has a footnote. Most quotes carry their real citation in the
attribution line right under the blockquote, not in a footnote:

```
> Facts don’t care about your feelings.
>
> [[Ben Shapiro]]
```

```
> Jefferson's principle...
>
> [[Bret Weinstein]], [DarkHorse Podcast: Cave of Mirrors...](url), 16. Jul 2024
```

Parse that line every time, independent of whether a footnote also exists:

- The `[[Wikilink]]` name(s) right after the blockquote → `authors`. Multiple names joined
  by `and`/`und`/`,` → split, same rule as footnote multi-author splitting.
- A podcast/article/book title after the author (plain text or `[Text](url)`) → `sources`.
- A trailing date (`16. Jul 2024`, `12. Jul 2023`) → `published` (full `YYYY-MM-DD` only) and
  `year`.
- A verse/chapter/timestamp (`Verse 316`, `6.2.35b`, `[52:00]`) → `position`.
- A bare URL in the attribution line (not already in `urls`) → append to `urls`.

**Never let a footnote's byline silently stand in for `authors` on a Quote.** A footnote
often cites the *reporter* (a video creator, journalist, podcast host) who is not the person
being quoted — e.g. a Mussolini quote sourced via an "Academy of Ideas" YouTube essay has
footnote author `[[Academy of Ideas]]`, but the actual speaker in the attribution line is
`[[Benito Mussolini]]`. `authors` on a Quote note means "who said/wrote these words," which
is the name in the attribution line, not necessarily the footnote's byline. When both exist
and agree, no conflict. When they disagree, the attribution line wins for `authors`; the
footnote's byline/source still legitimately fills `sources`/`urls`/`reference` (it's still
where you found the quote). If a Quote genuinely has no named speaker (an anonymous quote,
an organization's own public statement), it's fine for `authors` to be the reporter/reporting
org instead — that's not a violation of this rule, just the note's only available author.

Before finishing a Quote note, re-check: is `authors` non-empty? If not, look again at the
blockquote's attribution line — it's very rarely actually missing.

### 4. Rebuild frontmatter

Using the type resolved in step 2, rebuild the frontmatter in the **exact field order** of
that type's template (`references/templates.md` has every type's field order and destination
folder). Rules:

- Preserve `created` exactly as it currently appears (don't reformat date-only vs datetime).
- Set `updated` to the current datetime (`YYYY-MM-DDTHH:MM`) — every processed note gets a
  fresh `updated`, even if it already had one.
- Keep existing `aliases`, `tags`, `related`, `urls` values; merge in anything newly extracted
  from footnotes (don't discard existing entries).
- Keep the type's mandated tag if the template specifies one (e.g. Quote → `Zitat`, Book →
  `Buch`). If reclassifying a `Zitat`-tagged Note into `type: Quote`, keep the `Zitat` tag and
  switch to the Quote field order.
- Map footnote-extracted data per `references/footnote-parsing.md`: `authors` as
  `[[Wikilink]]` list, `sources` as a plain string (never wikilinked), `year`, `publication`
  as `[[Wikilink]]` (Quote/Literature Note only, best-effort), `published` only with a full
  `YYYY-MM-DD`, `urls` list, `reference` list of footnote ids.
- Drop any frontmatter field that isn't part of the target type's template.
- Never write a bare `[[Text: With A Colon]]` wikilink — a colon inside double brackets is
  invalid syntax and prettier will silently mangle it (drops everything after the colon).
  See "Wikilinks with a colon in the display text" in `references/templates.md` for the fix
  (alias syntax if the note exists, italic plain text if it doesn't).

### 5. Format with prettier

```bash
prettier --write "pages/<name>.md"
```

Run this while the file is still in `pages/`, after editing, before moving. No flags needed —
the vault's root `.prettierrc.json` is auto-discovered and its markdown override applies
(tabs, tabWidth 2, double quotes, printWidth 100, LF, trailing newline). If `prettier` isn't
on `PATH`, this is a batch-level precondition failure — stop and tell the user rather than
guessing an install location.

### 6. Move to destination

Look up the destination folder for the resolved type in `references/templates.md`. Check for
a name collision before moving — never overwrite:

```bash
test -e "<destination-folder>/<name>.md" && echo COLLISION
```

- If a collision exists: this is a possible duplicate. Add `❓` to the `pages/` note's tags,
  leave it in `pages/` untouched otherwise, log it as skipped, and move on.
- Otherwise:
  ```bash
  mv "pages/<name>.md" "<destination-folder>/<name>.md"
  ```
  A plain `mv` is safe — the vault uses shortest-path wikilinks, so any inbound `[[Title]]`
  links elsewhere in the vault keep resolving after the move.

Skip this entire step under `--dry-run` — just record the planned destination.

### 7. `--enrich` (optional, only if the user passed this flag)

If an `authors`/`related` wikilink points to an existing Person (or other resource) note that
is missing expected fields or otherwise malformed, invoke the `obsidian-vault-add` skill to
fill it in, explicitly preserving whatever information is already in that note. Do not create
notes for wikilinks that don't resolve to anything yet — leave those as ordinary (red) links.

### 8. QA pass before reporting

Before writing the end-of-batch report, spot-check the batch's own output, not just the
plan:

- Every moved `type: Quote` file has a non-empty `authors` field (see step 3b). An empty
  `authors` on a Quote is a processing bug, not an acceptable outcome — go back and fix it
  rather than reporting the batch done.
- No `[[...]]` in any touched file contains a bare colon (see the wikilink-colon rule in
  `references/templates.md`).

This check is cheap (grep for `authors:\n(  - .*\n)*` immediately followed by a non-list
field, or for `\[\[[^\]|]*:[^\]|]*\]\]`) and catches the two most common silent failure modes
of this skill.

## Ambiguity handling: `❓` and continue

Never pause the batch to ask about an individual note — that defeats the point of batch
processing. When a note can't be safely and confidently processed:

1. Add `❓` to its `tags` list (append, don't replace existing tags).
2. Leave the rest of the note untouched — no frontmatter reorder, no move.
3. Record it (with a short reason) for the end-of-batch report.
4. Continue to the next note.

Mark `❓` when: type can't be confidently determined; a footnote doesn't match the expected
pattern closely enough to extract cleanly; the destination already has a same-named file
(collision); author/source can't be cleanly separated from the footnote; the note is an
index/MOC/link-hub rather than real content (see `references/type-detection.md`).

Do **not** mark `❓` just because a note is missing optional data — publication, position, or
published date being absent is normal; proceed anyway. A note that's already well-formed
(right type, right field order, no footnote) still gets prettier-run and moved — reprocessing
it is idempotent and expected.

Only interrupt the whole batch to ask the user (not per-note) if a batch-level precondition
fails: `pages/` is empty, N survivors are fewer than requested (finish with what's available
and say so), or the `prettier` binary is unavailable.

## End-of-batch report

After the batch finishes (or after a `--dry-run` pass), report:

- Selected / processed / `❓`-skipped / collision counts.
- Per-type move counts, e.g. `Quote → 03 Resources/Zitate/: 6`, `Note → 04 Permanent/: 12`.
- List of moved files: `<name>.md → <destination-folder>/`.
- List of `❓`-skipped files with a one-line reason each.
- How many notes remain in `pages/` afterward.
- Confirmation that `qmd update` was run (skip under `--dry-run`).

## Re-index

After a live (non-dry-run) batch completes, re-index so moved/edited notes are searchable:

```bash
qmd update
```

Run `qmd embed` too if the user's setup requires it for semantic search; if it's slow, run it
`run_in_background: true`.

## Error handling

- Any single-note failure (unexpected parse error, unreadable file) → treat as ambiguous:
  `❓`-tag it if possible, log it, and continue with the rest of the batch. Never abort the
  whole batch over one bad note.
- Never write, move, or delete anything outside the vault root.
- Never run `git` commands in the vault — Obsidian Git auto-commits on its own schedule;
  don't fight it.
- Never overwrite an existing file at a destination path — always ❓-skip on collision.
