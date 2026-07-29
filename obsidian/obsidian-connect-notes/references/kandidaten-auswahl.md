# Batch selection

## Processed marker

`🔗` **in frontmatter `tags:`**, not anywhere in the body. Do not use `grep -rl "🔗"` to find
processed notes — the sibling marker `🤖` already appears inside 16 note *bodies* in this vault
(as literal text, not a tag), and the same trap applies here once notes start carrying `🔗`. Some
notes also use inline-flow `tags: [a, b]` rather than block style; a correct selector has to parse
both shapes. The python selector below does, and the whole-vault walk costs well under a second,
so there's no reason to reach for grep at all.

## Scope

`--scope wide` (default): `04 Permanent/`, `02 Areas/`, `01 Projects/`,
`03 Resources/Literatur Notes/`, `03 Resources/Personen/`.

`--scope core`: `04 Permanent/` only.

## Exclusions and why

| Excluded | Reason |
| --- | --- |
| `pages/` | owned by `obsidian-process-pages` — two skills must never contend for one folder |
| `00 Maps of Content/` | owned by `--mode moc` |
| `06 Daily/` | journal entries; categorising a diary entry is noise, and it's owned by the daily/weekly skills |
| `99 Meta/`, `05 Fleeting/`, `07 Archives/` | system files / transient by definition / frozen |
| `03 Resources/Zitate/` | excluded unless `--include-quotes`: quotes already carry `Zitat`, and their topical home is arguably their source note; including ~2,000 of them by default would swamp every category count |
| `03 Resources/Clippings/` | raw web captures, not the user's own thinking |
| tag `🔒` | **hard exclude, no override flag, ever** — private content must never be sent to a remote model |
| tag `❓` | `obsidian-process-pages`'s triage marker — respect it, don't reprocess |
| tag `MOC` or `Übersicht` | these are Maps of Content; `--mode moc` owns them, even the ones living outside the folder |
| tag `🔗` | already processed by this skill |
| `type: Daily Note` / `Quote` / `Outline` | belt-and-braces on top of the folder exclusions |
| unparseable frontmatter (invalid YAML, or no frontmatter at all) | report as skipped, never attempt to "fix" it — that's a job for a human or for `obsidian-process-pages`, not for silent repair here |
| duplicated basenames | excluded only as *link targets* (see below) — `[[Title]]` resolution is undefined when two files share a basename; the note can still be a subject of the batch |

## Selector

```python
import os, re, random, sys, json, yaml

SCOPE_WIDE = ("04 Permanent", "02 Areas", "01 Projects",
              "03 Resources/Literatur Notes", "03 Resources/Personen")
SCOPE_CORE = ("04 Permanent",)
BLOCK_TAGS = {"🔒", "❓", "🔗", "MOC", "Übersicht"}
BLOCK_TYPES = {"Daily Note", "Quote", "Outline"}

def eligible(path):
    try:
        t = open(path, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        return "nicht-lesbar"
    if not t.startswith("---\n"): return "kein-frontmatter"
    lines = t.split("\n")
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    if end is None: return "frontmatter-offen"
    fm = "\n".join(lines[1:end])
    try:
        d = yaml.safe_load(fm)
    except Exception:
        return "yaml-fehler"
    if d is not None and not isinstance(d, dict): return "yaml-keine-map"
    d = d or {}
    tags = d.get("tags") or []
    if isinstance(tags, str): tags = [tags]
    if BLOCK_TAGS & {str(x) for x in tags}: return "marker-tag"
    if str(d.get("type", "")) in BLOCK_TYPES: return "typ"
    return None            # eligible

def has_gaps(path):
    t = open(path, encoding="utf-8").read()
    no_tags = not re.search(r"^tags:\s*\n\s+- ", t, re.M) and not re.search(r"^tags:\s*\[.+\]", t, re.M)
    no_related = not re.search(r"^related:\s*\n\s+- ", t, re.M)
    return no_tags or no_related

scope = SCOPE_WIDE if len(sys.argv) < 4 or sys.argv[3] != "core" else SCOPE_CORE
include_quotes = "--include-quotes" in sys.argv
if include_quotes:
    scope = scope + ("03 Resources/Zitate",)

pool, skipped = [], {}
for root, dirs, fs in os.walk("."):
    dirs[:] = [x for x in dirs if not x.startswith(".")]
    r = root[2:] if root.startswith("./") else root
    if not any(r == s or r.startswith(s + "/") for s in scope): continue
    for f in fs:
        if not f.endswith(".md") or f == ".md": continue
        p = os.path.join(r, f)
        why = eligible(p)
        (pool.append(p) if why is None
         else skipped.setdefault(why, []).append(p))

N        = int(sys.argv[1])
seed     = int(sys.argv[2])
pure     = "--pure-random" in sys.argv
rng      = random.Random(seed)

if pure:
    batch = rng.sample(pool, min(N, len(pool)))
else:
    primary = [p for p in pool if has_gaps(p)]
    batch = rng.sample(primary, min(N, len(primary)))
    if len(batch) < N:
        rest = [p for p in pool if p not in set(batch)]
        batch += rng.sample(rest, min(N - len(batch), len(rest)))

print(json.dumps({"pool": len(pool), "seed": seed, "batch": batch,
                  "skipped_counts": {k: len(v) for k, v in skipped.items()}},
                 ensure_ascii=False, indent=1))
```

Usage: `python3 <script> <N> <seed> [core] [--pure-random] [--include-quotes]`

## Duplicated basenames — exclude as link targets

Before picking `related:` targets, build the set of basenames that occur more than once anywhere
in the vault (a single `os.walk` collecting `f[:-3]` per `.md` file, counting duplicates). Never
write a `[[Title]]` for a title in that set — wikilink resolution is undefined between the
duplicates, and a link could silently point at the wrong note. The note can still be *read* and
*tagged* if it's one of the duplicates; it just can't be a link *target* chosen by this skill.

## Idempotence, stated explicitly

1. `eligible()` is a pure function of a file's current bytes.
2. Every note this skill finishes processing gains `🔗` in `tags:`, which makes `eligible()`
   return `"marker-tag"` for it from then on — permanently, until a human removes the tag.
3. Therefore the eligible pool strictly shrinks across runs; no note is ever drawn twice by this
   skill on its own.
4. Each note is written to disk (frontmatter edit → prettier → journal entry) before the next one
   is read. There is no cross-note state, so an interrupted run leaves a consistent vault: the
   notes already finished are marked and won't be redrawn, the rest are untouched.
5. `--seed` is therefore a **provenance record**, not a promise that re-running with the same seed
   reproduces the same batch — the pool it samples from is smaller every time a live run
   completes. Say this plainly in the report if a user asks to "redo" a seed.
