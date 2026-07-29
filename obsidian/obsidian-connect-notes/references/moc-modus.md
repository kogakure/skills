# MOC-Modus

The AI becomes the maintainer of the **link inventory** of `00 Maps of Content/` and the author
of *new* MOCs there. It never becomes the editor of a human's prose.

## Append-only inside existing MOCs

- Never delete a line, never reorder, never rewrite a heading, never touch a prose paragraph or
  a callout. The only permitted operation on an existing MOC is *adding* new bullet lines.
- New links go under the best-matching existing `##`/`###` heading if one obviously fits the
  topic. If nothing fits, append under a `## Unsortiert` heading — a bucket this vault already
  uses in several MOCs — creating that heading (at the end of the file) if it doesn't exist yet.
- Some MOCs contain a prose paragraph or an annotated link (e.g. a definition, a `(gehört unter
  anderem bei [[Person]])` aside). **Leave these entirely alone.** Distinguishing "prose worth
  preserving" from "a stray line" is not a judgment call this skill should make by deleting
  anything — list such MOCs in the report under "MOCs mit Prosa (menschliche Bereinigung nötig)"
  and move on. This still satisfies the spirit of "MOCs contain only links" for the ~90% of MOCs
  that already are pure link lists — enforcing it on the rest by deletion would trade a small
  cosmetic win for irreversible risk.

## Marker-Tag-Politik

- Add the `MOC` tag to any file in `00 Maps of Content/` that lacks it.
- **Never remove `Übersicht`** from a file that has it, even though the registry treats
  `Übersicht` as absorbed by `MOC`. It may be referenced by a `.base` view or simply be a human
  habit — removing an existing tag is a destructive change with no upside here.
- Never add a sentinel tag (`⭐`, `BOAT`, …) to a MOC on your own initiative.

## Never move, never rename

Some `MOC`-tagged notes live outside `00 Maps of Content/`, and some notes linked from
`00 - Index.md` live in `04 Permanent/` rather than the MOC folder. Leave every one of them where
it is — report them as items for the human to decide on, never move or rename a file. The same
goes for any filename you notice is misspelled: report it, never fix it.

## Caps, every run

- **At most 3 new MOCs created per run.**
- **At most 10 links appended to any single existing MOC per run.**

These exist so `moc` mode stays reviewable in one sitting, the same way `notes` mode is capped at
50.

## Deutsch-Regel

Newly created MOC titles, their `aliases`, and any text this skill writes are German; the
English term goes in `aliases`, never in the title or a tag. Existing MOCs with English titles
(`CSS`, `Development`, `Note-Taking`, `Accessibility`, `Critical Theory`, `Blockchain`, …) are
linked to and appended to exactly as they are — this rule governs what gets *created*, not
what already exists.

## When a new MOC is warranted

All of the following must hold:

1. A `## Kategorien` row in the registry has an empty `MOC` column.
2. That row's `Notizen` count is **≥ 12**.
3. At least 8 concrete notes for it can actually be listed — verified by exact basename
   existence, not guessed from the count.
4. No existing note anywhere in the vault already has that title or an alias matching it (check
   with an exact match against the file inventory and `obsidian aliases` — never a fuzzy match).

## New-MOC template

Path: `00 Maps of Content/<Deutscher Titel>.md`

```markdown
---
type: Note
created: <YYYY-MM-DDTHH:MM>
updated: <YYYY-MM-DDTHH:MM>
aliases:
  - <Englischer Begriff>
tags:
  - 🤖
  - MOC
  - <Kategorie-Tag>
urls:
related:
  - "[[<übergeordnete MOC oder 00 - Index>]]"
reference:
---

- [[<Notiz 1>]]
- [[<Notiz 2>]]
- [[<Notiz 3>]]
```

- `type: Note` — deliberate, not `type: MOC`. **All 130 existing MOCs use `type: Note`**, and
  `99 Meta/bases/Maps of Content.base` filters on `file.tags.contains("MOC")`; inventing a new
  type would silently break that view and be inconsistent with every MOC already in the vault.
- `tags:` = `🤖` (this file was AI-created) + `MOC` + the category's own `Tag` value, so the MOC
  is discoverable both as a MOC and under its own topic.
- `aliases:` carries the English equivalent term — the escape hatch for the German-only rule.
- `related:` points to the parent MOC if the category has one in `Domäne`/an existing hierarchy,
  otherwise to `[[00 - Index]]`.
- Body: a flat, alphabetically sorted bullet list of wikilinks only. No prose, no headings, at
  least while the list is short (roughly under 15 entries — headings can be introduced by a human
  later if the MOC grows).

Before writing, check no file already exists at that path (or under an alias with that title
anywhere in the vault) — if one does, skip creating it, report the collision, and don't overwrite.

After creating it: fill the registry's `MOC` column for that row, and note that it's now eligible
for `--mode index` to place into `00 - Index.md`.
