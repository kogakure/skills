# Tagging-Richtlinien

## Geschlossenes Vokabular

The **only** strings this skill may write into a note's `tags:` are:

1. A value from the registry's `Tag` column (`99 Meta/Kategorien.md`, `## Kategorien`), and
2. `🔗` (the processed marker, on every note the skill finishes), and
3. `🤖` (only on files the AI *created* — a new MOC or the registry itself, never on an ordinary
   note).

Nothing else. Not an English alias, not a freshly invented German word, not a sentinel from
`## Keine Kategorien`.

> **The governance invariant:** a new tag is never born on a note. It is born in the registry,
> where a human sees it before it ever spreads. This is the only thing standing between the
> vault's current 786 tags and a much larger, messier number after a few hundred runs.

If a note's topic doesn't fit any existing `Kategorie` row:

- Add (or bump `Runs` on) the candidate in the registry's `## Kandidaten` table.
- Then either tag the note with the nearest fitting *ancestor* category that already exists, or
  add no category tag to this note at all this run. Never invent the tag on the note itself.

## Wie viele Tags

**1–3 category tags per note**, chosen by genuine topical fit — not by maximizing coverage. A
note that clearly fits one category should get one tag, not three for safety.

## Was NICHT getaggt wird

- Never add a value from `## Keine Kategorien` (type/status/sentinel tags — `Zitat`, `Buch`,
  `MOC`, `🔒`, `⭐`, `BOAT`, …) — these already exist for other reasons and aren't this skill's to
  manage.
- Never remove, rename, or reorder an existing tag on a note, for any reason. Consolidating a
  synonym cluster (e.g. `Corona` → `COVID-19`) is out of scope for a batch run — it's a distinct,
  explicitly requested operation, never a side effect.
- Never add an `Absorbiert` synonym tag when the canonical `Tag` (or another `Absorbiert`
  synonym) is already present — the category is already covered.

## Deutsch-Regel

Every tag and every piece of new prose or link text this skill writes is **German**. English
terms are recorded only as `aliases:` (on new MOCs — see `references/moc-modus.md`) or in the
registry's `Aliase` column, never as a tag and never as body text on an ordinary note.

Existing English MOC titles already in the vault (`Accessibility`, `CSS`, `Development`,
`Note-Taking`, `Critical Theory`, `Blockchain`, …) are linked to verbatim when they're the right
target — the German-only rule governs what this skill *creates*, not what already exists.

## `related:` — Anzahl und Ziel-Regeln

- 0–5 additions per note per run; hard cap **3 additions per note**, and the field may never
  exceed **6 entries total** after the edit. The field currently holds roughly one entry on a
  typical note (usually the parent MOC) — treat that as the norm to extend gently, not replace.
- At least one addition should be the note's category MOC (from the registry's `MOC` column),
  when one exists.
- The remaining additions should be sibling notes — other individual notes on a related topic —
  not more hub/MOC links. Piling up MOC links on one note doesn't build connective tissue, it
  just duplicates the registry.
- **Anti-hub cap: at most 3 notes per run may gain a link to the same target.** Enforce this by
  tracking target counts within the run, not just per note. Without it, a long-running campaign
  of small batches turns the vault's link graph into a star around a handful of mega-hubs
  (`[[Politik]]`, `[[Wirtschaft & Ökonomie]]`, …), which is the opposite of what connecting the
  Zettelkasten is supposed to achieve.
- **Verify every target before writing.** A link target must resolve to an existing file by exact
  basename or a known alias (`obsidian aliases` or the file inventory built during batch
  selection) — never write a wikilink on faith. A target that is one of the vault's duplicated
  basenames is never used, regardless of how good the semantic match looks (see
  `references/kandidaten-auswahl.md`).
- Never remove or reorder an existing `related:` entry.
