# Die Kategorien-Registry

Path: `99 Meta/Kategorien.md`. This is the single artifact that keeps every run of this skill
O(1) in vault size instead of O(vault size) — no run ever re-derives topic clusters by reading
thousands of notes. It is also the **veto channel**: a human opens it in Obsidian, renames a
category, edits its `Tag`, or sets a candidate's `Status` to `abgelehnt`, and every future run
honours that permanently.

Format is markdown + YAML frontmatter + tables — deliberately not JSON. The registry must be
readable and editable natively in Obsidian, and its wikilinked `MOC` column gives every curated
MOC a backlink to the registry for free.

## Frontmatter

```yaml
---
type: Note
created: <YYYY-MM-DD>
updated: <YYYY-MM-DDTHH:MM>
aliases:
  - Kategorien
  - Categories
  - Kategorie-Registry
tags:
  - 🤖
  - MOC
urls:
related:
  - "[[00 - Index]]"
---
```

## Body structure

```markdown
Kanonische Liste der breiten Kategorien dieses Zettelkastens. Von
`obsidian-connect-notes` gepflegt. **Menschliche Änderungen sind verbindlich:**
umbenannte Kategorien, geänderte Tags und auf `abgelehnt` gesetzte Kandidaten
werden nie überschrieben.

Schwellenwerte: Kategorie ab **25** Notizen, Kandidat ab **3** Notizen (darunter
wird der Tag ignoriert). Bei Bedarf hier anpassen.

## Kategorien

| Kategorie | Tag | MOC | Domäne | Aliase | Absorbiert | Notizen | Stand |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Wirtschaft & Ökonomie | Ökonomie | [[Wirtschaft & Ökonomie]] | Wirtschaft & Geld | Economics | Wirtschaft, Ökonomik | 74 | 2026-07-29 |
| COVID-19 | COVID-19 | [[COVID-19]] | Gesundheit & Körper | Corona, Pandemic | Corona, Coronavirus, SARS-CoV-2 | 389 | 2026-07-29 |

## Kandidaten

| Kandidat | Tag | Notizen | Zuerst gesehen | Runs | Status |
| --- | --- | --- | --- | --- | --- |
| Verhaltensökonomie | Verhaltensökonomie | 11 | 2026-07-29 | 1 | neu |

## Keine Kategorien

Sentinel-, Typ- und Status-Tags. Nie als Kategorie behandeln, nie einer Notiz durch
die KI hinzufügen (Ausnahme: `🤖` auf KI-erzeugten Dateien, `🔗` als
Bearbeitungs-Marker):

`🔒` `⭐` `❓` `🤖` `🔗` `MOC` `Übersicht` `BOAT` `Zitat` `Buch` `Podcast` `Person`
`Serie` `TV-Show` `Film` `Prompt` `Tagebuch` `XING` `Skill` `Lyrics` `Outline`
```

## Column semantics

- **`Kategorie`** — human-facing label, may contain `&`, commas, spaces. Matches an existing MOC
  title where one exists.
- **`Tag`** — the *only* string ever written into a note's `tags:` for this category. Must be a
  single German token: no `&`, no comma, no space. **This split is load-bearing**: five of the 28
  seed entries from `00 - Index.md` (`Beruf & Karriere`, `Wirtschaft & Ökonomie`, `Note-Taking`,
  `Development`, `Umwelt, Klimawandel & Nachhaltigkeit`) have a matching tag count of zero — a
  good MOC title is often an unusable tag.
- **`MOC`** — a `[[Wikilink]]` to the category's Map of Content, or empty. A row with `Notizen ≥
  12` and an empty `MOC` is exactly the trigger `--mode moc` looks for (see
  `references/moc-modus.md`).
- **`Domäne`** — one of the 8 fixed top-level domains listed in `references/index-modus.md`.
  Stored here, not re-derived per run, so `--mode index`'s grouping is stable across runs.
- **`Aliase`** — English/alternative terms. Feeds a new MOC's `aliases:` list. **Never written
  into any note's `tags:`** — this is the mechanical enforcement of the vault's German-only
  tagging rule; English terms live only as aliases, never as tags.
- **`Absorbiert`** — synonym/narrow tags subsumed by this category (e.g. `COVID-19` absorbs
  `Corona`, `Coronavirus`, `SARS-CoV-2`). Two effects: a note already carrying an absorbed tag is
  treated as already covered by that category and doesn't get the canonical tag added too; and
  `Notizen` counts the union of the `Tag` and all `Absorbiert` values. **v1 never removes or
  rewrites an absorbed tag on a note** — consolidating `Corona` → `COVID-19` across every note
  that has it is a separate, explicitly requested operation, never an automatic side effect of a
  batch run.
- **`Notizen`** — a derived count, regenerated every run. Never hand-author this.
- **`Stand`** — the date the count was last refreshed.

`## Kandidaten`'s `Status` column: `neu` (just seen), `beobachten` (seen ≥2 runs, not yet over
threshold), `abgelehnt` (human veto — **permanent**, never re-proposed, never re-counted, never
promoted).

## Bootstrap (once, only if the file does not exist yet)

**Guard: if `99 Meta/Kategorien.md` already exists, never run this again.** There is no
`--rebootstrap` flag on purpose — a flag that can silently wipe a human's `abgelehnt` decisions
and renamed categories has no business existing. To redo the bootstrap the user deletes the file
themselves, on purpose.

Cheap tally, no note bodies read — measured at well under a second for the whole vault:

```python
import os, re, collections, json

INDEX = "00 Maps of Content/00 - Index.md"
SENTINEL = {"🔒","⭐","❓","🤖","🔗","MOC","Übersicht","BOAT","Zitat","Buch","Podcast",
            "Person","Serie","TV-Show","Film","Prompt","Tagebuch","XING","Skill",
            "Lyrics","Outline"}

def frontmatter(path):
    try:
        t = open(path, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        return None
    if not t.startswith("---\n"): return None
    lines = t.split("\n")
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    return None if end is None else "\n".join(lines[1:end])

def listvals(fm, key):
    m = re.search(r"^%s:(.*?)(?=^[A-Za-z_][\w -]*:|\Z)" % re.escape(key), fm + "\n", re.S | re.M)
    if not m: return []
    blk = m.group(1)
    if blk.strip().startswith("["):
        return [x.strip().strip("\"'") for x in blk.strip()[1:-1].split(",") if x.strip()]
    return [x.strip().strip("\"'") for x in re.findall(r"^\s*-\s*(.+?)\s*$", blk, re.M)]

tags = collections.Counter()
for root, dirs, fs in os.walk("."):
    dirs[:] = [d for d in dirs if not d.startswith(".")]
    for f in fs:
        if not f.endswith(".md") or f == ".md": continue
        fm = frontmatter(os.path.join(root, f))
        if fm is None: continue
        for t in listvals(fm, "tags"):
            if t not in SENTINEL: tags[t] += 1

idx = open(INDEX, encoding="utf-8").read()
seeds = [re.sub(r"\|.*", "", m).strip() for m in re.findall(r"\[\[([^\]]+)\]\]", idx)]
mocs = sorted(f[:-3] for f in os.listdir("00 Maps of Content") if f.endswith(".md"))

print(json.dumps({
    "seeds": seeds,
    "mocs": mocs,
    "kategorien": [[t, n] for t, n in tags.most_common() if n >= 25],
    "kandidaten": [[t, n] for t, n in tags.items() if 3 <= n < 25],
    "ignoriert": sum(1 for n in tags.values() if n <= 2),
}, ensure_ascii=False, indent=1))
```

Then, in **one** reasoning pass over that JSON — never by reading note bodies:

1. Every one of the `seeds` becomes a `Kategorie` row with `MOC` prefilled from `mocs`, even the
   ones whose matching tag count is zero — invent a sensible `Tag` for those.
2. Tags with count ≥25 not already covered by a seed row become new rows or get folded into an
   existing row's `Absorbiert`.
3. Write obvious synonym clusters into `Absorbiert` (e.g. `Corona`/`Coronavirus`/`SARS-CoV-2` →
   `COVID-19`; `Genozid` → `Völkermord`; `Habit`/`Gewohnheitsbildung` → `Gewohnheit`;
   `Wirtschaft` → `Ökonomie`; `Massenpsychose` → `Massenhysterie`; `TV-Show` → `Serie`;
   `Gesetz` → `Recht`).
4. Give each row an `Aliase` (English term) and a `Domäne` from the fixed 8.
5. Tags with count 3–24 → `## Kandidaten`, `Status: neu`. Tags with count ≤2 → dropped entirely,
   mentioned in the report only as a count.

Target size: **60–90 categories.** If the pass produces more than ~100, topic and category have
been conflated — merge, don't split further.

## Incremental update, every run

Strictly monotone — nothing is ever deleted, reordered, or demoted:

1. Re-run the tally (same snippet as above). Refresh `Notizen` and `Stand` for every existing
   row. Counts can go down if the user removed a tag manually — that's fine, they're derived.
2. Any tag seen on a processed note that matches neither a `Kategorie` row's `Tag`/`Absorbiert`
   nor an existing `Kandidaten` row, and isn't in `## Keine Kategorien` → append to
   `## Kandidaten`, `Status: neu`, `Runs: 1`.
3. An existing candidate seen again → `Runs += 1`. Never reset this counter.
4. **Promotion**: `Notizen ≥ 25 ∧ Runs ≥ 2 ∧ Status ≠ abgelehnt` → move the row from
   `## Kandidaten` to `## Kategorien`, `MOC` left empty (which is exactly what queues it for
   `--mode moc`).
5. Any value a human has written into `Kategorie`, `Tag`, `Aliase`, `Absorbiert`, or `Domäne` is
   never overwritten by this update — only `Notizen` and `Stand` are agent-maintained columns.
6. Finish with `prettier --write "99 Meta/Kategorien.md"` so the generated tables produce clean,
   one-line diffs.
