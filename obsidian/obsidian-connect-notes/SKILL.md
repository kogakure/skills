---
name: obsidian-connect-notes
description: >
  Vernetzt den Obsidian-Zettelkasten: wählt N zufällige, noch unbearbeitete Notizen
  (Standard 10, bevorzugt Notizen ohne Tags/Verweise), ergänzt breite Kategorie-Tags
  aus einer Kategorien-Registry (`99 Meta/Kategorien.md`) und Querverweise in
  `related:`, pflegt die Maps of Content in `00 Maps of Content/` und strukturiert
  `00 - Index.md`. Trigger on "vernetze 10 Notizen", "verknüpfe Notizen",
  "kategorisiere Notizen", "Tags ergänzen", "Kategorien-Registry aktualisieren",
  "MOCs pflegen", "Index aufräumen", "connect notes", "link notes", "tag notes",
  "curate MOCs", "build the index", "weave the vault", "connect the brain". Bearbeitet
  ausschließlich Frontmatter (`tags:`, `related:`, `updated:`) einer normalen Notiz —
  niemals ihren Inhalt; bei MOC-Dateien und `00 - Index.md` ist zusätzlich
  append-only Body-Bearbeitung erlaubt. This is NOT obsidian-process-pages (which
  sorts the legacy `pages/` folder and rebuilds whole frontmatter blocks from
  footnotes — this skill never touches `pages/` and never rebuilds a block, only
  appends to it), NOT obsidian-search-vault (read-only search, no writes), and NOT
  obsidian-process-notes (a separate wiki vault built from `inbox/`).
allowed-tools: Bash(python3*), Bash(qmd*), Bash(prettier*), Bash(obsidian tags*), Bash(obsidian unresolved*), Bash(obsidian aliases*), Bash(obsidian backlinks*), Bash(ls*), Bash(wc*), Bash(test*), Bash(grep*), Read, Edit, Write
---

# obsidian-connect-notes

Chips away at the vault's connective tissue a few notes per run: broad category tags,
cross-links in `related:`, curated Maps of Content, and a structured `00 - Index.md`. A
machine-readable, human-vetoable **category registry** at `99 Meta/Kategorien.md` keeps every
run cheap — no run ever has to re-derive topic clusters from the whole vault.

Run this skill from the vault root (the Obsidian Zettelkasten vault directory). All paths below
are relative to that root. Never read, write, or move anything outside it.

**The governing distinction, stated once because everything below depends on it:** a "normale
Notiz" is any note that is neither tagged `MOC`/`Übersicht` nor `00 Maps of Content/00 - Index.md`.
On a normale Notiz, the skill may only touch frontmatter (`tags:`, `related:`, `updated:`) plus
run `prettier --write` on it — content, wording, and structure of the body are never rewritten,
reordered, or deleted. On a MOC file or the Index, the body may additionally be edited
**append-only**: new links added, nothing existing removed, reordered, or reworded.

## Argument parsing

Arguments: `<N> [--mode notes|moc|index|all] [--dry-run] [--scope core|wide] [--seed <int>] [--pure-random] [--include-quotes]`

- `N` (optional, default **10**, hard cap **50**): how many notes to process this batch (only
  meaningful for `--mode notes`; `moc` and `index` have their own per-run caps, see their
  reference files). If N > 50, refuse and ask the user to run smaller batches instead — this
  skill is designed for many small runs, not one huge one.
- `--mode` (default **notes**): `notes` tags/links individual notes; `moc` maintains
  `00 Maps of Content/`; `index` structures `00 - Index.md`; `all` runs all three in that order
  (notes first, since it's what feeds new categories into `moc`, which feeds new entries into
  `index`).
- `--dry-run`: plan everything — category decisions, link decisions, registry updates, MOC/Index
  diffs — print the full report, but write **nothing**: no note, no registry, no journal file.
  Recommend this for a user's first run of each mode.
- `--scope` (default **wide**, only for `--mode notes`): `wide` = `04 Permanent/`,
  `02 Areas/`, `01 Projects/`, `03 Resources/Literatur Notes/`, `03 Resources/Personen/`. `core` =
  `04 Permanent/` only. See `references/kandidaten-auswahl.md` for the full exclusion list and why.
- `--seed` (default: current `YYYYMMDDHHMM`, always printed): seeds the random batch selection.
  This is a **provenance record for the report, not a reproducibility guarantee** — replaying the
  same seed after a live run draws a different batch, because processed notes leave the pool.
- `--pure-random`: sample uniformly over the whole eligible pool instead of the default
  gaps-first strategy (untagged/unlinked notes first, see `references/kandidaten-auswahl.md`).
- `--include-quotes`: include `03 Resources/Zitate/` in the `--mode notes` pool. Off by default —
  see the exclusion table in `references/kandidaten-auswahl.md` for why.

Examples: `Vernetze 10 Notizen`, `connect notes --dry-run`, `Pflege die MOCs --mode moc`,
`Räume den Index auf --mode index`, `10 --mode all`.

If the user just says "vernetze Notizen" / "connect notes" with no number, use N=10 and say so.

## Vorbedingungen (once per run, before touching anything)

```bash
test -d "00 Maps of Content" && test -d "04 Permanent" && test -f ".prettierrc.json" \
  || echo "NICHT IM VAULT-ROOT — Abbruch"
python3 -c "import yaml" || echo "PyYAML fehlt — Abbruch"
obsidian unresolved total 2>/dev/null      # Baseline für die Nachprüfung am Ende
qmd status 2>/dev/null | grep -E "Pending|Documents|Total"
```

If the root check or the PyYAML check fails, stop and tell the user — this is a hard
precondition, not a per-note ambiguity.

If `qmd status` shows `Pending > 0` (unembedded documents), semantic neighbour search
(`qmd vsearch`) is unreliable for that fraction of the vault. Tell the user, and use
`qmd search` (BM25, no model download, always available) as the neighbour primitive for this
run instead. **Never invoke `qmd vsearch` blind** — on an incompletely embedded index it can
trigger a large model download mid-command.

## Die Kategorien-Registry

Read `references/kategorien-registry.md` before touching `99 Meta/Kategorien.md` — it has the
full column semantics, the bootstrap snippet, and the promotion rules.

If `99 Meta/Kategorien.md` does not exist yet: **bootstrap it once**, from the 28 existing
`00 - Index.md` entries plus a cheap frontmatter tag tally (no note bodies read). Never
re-bootstrap if the file already exists — that would silently discard human decisions
(`abgelehnt` candidates, renamed categories). There is deliberately no `--rebootstrap` flag; to
redo it, the user deletes the file themselves.

Every run (any mode) refreshes the registry's derived counts and appends newly observed tags to
`## Kandidaten`, per the promotion rules in the reference file, then
`prettier --write "99 Meta/Kategorien.md"`.

## Batch selection (`--mode notes` and `--mode all`)

Read `references/kandidaten-auswahl.md` for the exact selector, the full exclusion list with
reasons, and the idempotence argument. Summary: the pool is every note under the scope's folders
minus anything tagged `🔒`, `❓`, `🤖`, `🔗`, `MOC`, or `Übersicht`, minus `type: Daily
Note`/`Quote`/`Outline`, minus unparseable frontmatter, minus `pages/`, `06 Daily/`, `99 Meta/`,
`05 Fleeting/`, `07 Archives/`, and (unless `--include-quotes`) `03 Resources/Zitate/`.

`🔗` is the processed marker — a note that gets it is permanently out of the pool. This is what
makes repeated runs never redraw the same note. `🔒`-tagged notes have **no override flag**:
private content must never be sent to a remote model.

## Per-note workflow (`--mode notes`)

Process one note fully before starting the next.

### 1. Read

Read the full note (frontmatter + body). Reading the body is required to judge topicality —
reading is not writing.

### 2. Derive a query

Title + `aliases` + existing `tags` + the first two sentences of the body, in German, capped at
roughly 200 characters. Strip wikilink brackets, blockquote markers, and footnote references.

### 3. Find neighbours

```bash
qmd search "<Query>" -c permanent -c moc -c areas -c literature-notes -c books -c people -n 12
```

(or `qmd vsearch` instead, only if the preflight showed `Pending == 0`). The vault is indexed one
collection per folder; `obsidian-search-vault` documents the full table. Repeat `-c` per
collection — a comma-separated list fails with `Collection not found`.

Scoping to these six is most of step 4 done in advance: `daily`, `quotes` and the meta folders
are simply not searched. If `qmd` answers `Collection not found`, the index on this machine is
still the old single `zettelkasten` collection — tell the user and fall back to an unscoped
`qmd search "<Query>" -n 12` for this run.

### 4. Filter candidates

Drop, in order: the note itself · anything already in its `related:` · anything under
`06 Daily/`, `99 Meta/`, or `pages/` · anything tagged `🔒` · any title that is a duplicated
basename (list in `references/kandidaten-auswahl.md` — resolution is undefined for these). Keep
at most 8.

### 5. Decide 0–3 category tags

Read `references/tagging-richtlinien.md` first. Summary of the hard rule: **only tags that
already exist in the registry's `Tag` column may be written onto a note.** If the note's topic
has no fitting row, add the candidate to `## Kandidaten` in the registry and either use the
nearest existing ancestor category or add no category tag at all — never invent a tag directly
on a note. If the note already carries a tag listed in some row's `Absorbiert` column, that
category is already covered; add nothing more for it. Never remove or rename an existing tag.

### 6. Decide 0–5 `related:` links

At least one upward link to the note's category MOC when the registry has one for it; the rest
should be sibling notes, not more hubs. **Verify every target resolves** (exact basename or known
alias) before writing — never write a link to a title that doesn't exist. Caps, enforced every
time: at most 3 additions per note, at most 6 entries total in `related:` afterwards, and at most
3 notes per run may gain a link to the same target (anti-hub cap — without it, repeated runs turn
the graph into a star around a handful of mega-hubs).

### 7. Apply the frontmatter edit

Read `references/frontmatter-bearbeitung.md` and use the mutator described there — an inline
`python3` snippet that splits the file on its `---` fences and rewrites only the YAML block. Do
**not** use `obsidian property:set` for this (it's a single-value `set`, not a list append, and
would collapse the vault's bare-empty-key convention) and do not hand-edit the YAML with the
`Edit` tool as the primary method (fallback only, if the mutator itself refuses).

Always: append `🔗` to `tags:` (even if no category tag or link was warranted — see Ambiguity
handling), bump `updated` to `YYYY-MM-DDTHH:MM` (now).

### 8. Normalize formatting

```bash
prettier --write "<pfad zur notiz>"
```

Any note may be prettified at any time — this is a deliberate, separate, idempotent step after
the frontmatter edit, not a body edit to the note's substance. On notes that weren't already
prettier-clean this will reflow lines/lists/quotes; it must never change what the note says.

### 9. Journal the change

Append an entry (path, tags added, links added, `updated` value, body SHA-256 taken _after_
prettier) to this run's journal — see the format and the undo mechanism in
`references/frontmatter-bearbeitung.md`.

## Ambiguity handling: mark `🔗` and continue

Never pause the batch to ask about one note. When a note can't be safely and confidently
processed with a category tag or a link:

1. Still append `🔗` to `tags:` and bump `updated` — otherwise the note stays in the pool and is
   redrawn forever, which breaks idempotence.
2. Record it in the report as "geprüft, keine Änderung" with a short reason.
3. Continue to the next note.

Only interrupt the whole batch (not per-note) if a batch-level precondition fails: the
Vorbedingungen check fails, the pool has fewer eligible notes than requested (finish with what's
available and say so), or `prettier`/`python3`/`pyyaml` is unavailable.

## MOC-Modus (`--mode moc`)

Read `references/moc-modus.md` in full before touching any file under `00 Maps of Content/` —
it has the append-only rules, the new-MOC template, the marker-tag policy (`MOC` vs.
`Übersicht`), and the caps (≤3 new MOCs, ≤10 appended links per existing MOC, per run).

## Index-Modus (`--mode index`)

Read `references/index-modus.md` in full before touching `00 - Index.md` — it has the target
two-level structure, the fixed domain list, and the never-lose-a-link algorithm. **The very
first live run of this mode requires an explicit user confirmation before writing**, because it
regroups the whole file; every later run only appends.

## End-of-batch report

After the batch finishes (live or `--dry-run`), report in German:

- Mode, N, scope, seed, live/dry-run.
- Pool size before → after.
- Per note: tags added, links added (or "geprüft, keine Änderung" + reason).
- Registry delta: counts refreshed, new candidates, any promotions (and whether they now need a
  MOC).
- For `moc`/`index` runs: MOCs created, MOCs appended to, MOCs left alone due to prose (see
  `references/moc-modus.md`), Index diff summary.
- `obsidian unresolved` before → after — **this must not increase**; if it does, say so plainly
  and treat the run as failed for that note.
- Journal file path.
- Confirmation that `qmd update` ran (skip under `--dry-run`).

## Re-index

After a live batch completes:

```bash
qmd update
```

Run `qmd embed` too, only if the Vorbedingungen check showed `Pending > 0`; if slow, run it
`run_in_background: true`. Never run `qmd cleanup`.

## Undo

Obsidian Git auto-commits on its own schedule and mixes unrelated changes into one commit — it is
**not** a reliable undo path for this skill (verify with `git log -1` / `git status` if the user
asks: a stale last-commit timestamp with many uncommitted files means the automatic backup is not
current). Rely instead on the run journal and its reverse snippet, both described in
`references/frontmatter-bearbeitung.md`.

## Absolute Verbote

- Never run `git` in the vault.
- Never use `obsidian property:set` / `property:remove` on `tags:` or `related:`.
- Never change what a normale Notiz _says_. `prettier --write` normalization is the only
  permitted body operation on one; no rewording, no additions, no deletions of content.
- Never delete, reorder, or rewrite an existing tag, link, or heading anywhere.
- Never `mv`, `rm`, or rename anything.
- Never enter `pages/`, `06 Daily/`, or any `🔒`-tagged note.
- Never write outside the vault root; never use an absolute path.
- Never invent a tag directly on a note — new tags are born in the registry, where the human
  sees them, never on a note first.
- Never write a wikilink to a title that doesn't resolve.
- Never abort a whole batch over one bad note; never pause a batch to ask about a single note.

## Error handling

- Any single-note failure (parse error, unreadable file, YAML that doesn't round-trip) → treat as
  ambiguous: mark `🔗`, log it, continue with the rest of the batch. Never abort the whole batch
  over one bad note.
- The frontmatter mutator is fail-closed: on any exception, or if a post-write body-hash check
  doesn't match, it rolls the file back from memory and the note is logged as failed, not partly
  written.
- Never overwrite an existing MOC file when creating a new one — check first, and if a
  same-titled file exists anywhere in the vault, skip creating it and report the collision.
