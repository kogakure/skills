# Frontmatter-only editing

## Method choice

Three ways to append to a note's `tags:`/`related:` were considered; only one is used as the
primary mechanism.

**`obsidian property:set` — forbidden for this.** Its usage is
`property:set name=<name> value=<value> [type=text|list|number|checkbox|date|datetime] [file=<name>] [path=<path>]`
— a single-value **set**, not a list append. Appending a value would require reading the current
list, computing the union, and setting the whole thing back through Obsidian's frontmatter
writer, which normalizes empty keys to `null` (e.g. `aliases:` → `aliases: null`) — a change that
touches roughly 1,481 notes' worth of formatting convention as a side effect. It also requires
Obsidian to be running. Retained only for read-only verification (`obsidian tags`, `obsidian
unresolved`, `obsidian backlinks`, `obsidian aliases`).

**`Edit` tool directly on the YAML block — documented fallback only.** Requires the agent to
retype a frontmatter block byte-exactly (indentation, quote style, emoji) once per note; the
failure mode is a hand-mangled block on one note in ten that goes unnoticed. Use this only if the
mutator below refuses on a note for a reason the user wants overridden by hand.

**Inline `python3` fence-split mutator — primary, used for every note.** It slices the file into
`[frontmatter lines] + [body lines]` exactly once, edits only the first slice, and rejoins. No
code path in it can touch the body slice. This has been verified by round-tripping split-and-
rebuild over the whole vault with zero body differences.

## The mutator

```python
import os, re, sys, hashlib, tempfile, yaml

ORDER = ["type", "created", "updated", "aliases", "tags", "urls", "related",
         "authors", "sources", "year", "reference"]

def parse(path):
    raw = open(path, "rb").read()
    text = raw.decode("utf-8")                        # strict: raises on bad bytes
    if not text.startswith("---\n"):
        raise ValueError("kein Frontmatter")
    lines = text.split("\n")
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    if end is None:
        raise ValueError("Frontmatter nicht geschlossen")
    fm = lines[1:end]
    data = yaml.safe_load("\n".join(fm))
    if data is not None and not isinstance(data, dict):
        raise ValueError("Frontmatter ist keine Map")
    return raw, lines, end, fm

def span(fm, key):
    for i, l in enumerate(fm):
        if re.match(r"^%s:" % re.escape(key), l):
            j = i + 1
            while j < len(fm) and fm[j][:1] in (" ", "\t"):
                j += 1
            return i, j
    return None

def items(fm, s):
    i, j = s
    head = fm[i].split(":", 1)[1].strip()
    if head.startswith("["):                           # inline-flow shape
        return [x.strip().strip("\"'") for x in head[1:-1].split(",") if x.strip()]
    return [re.sub(r"^-\s*", "", l.strip()).strip("\"'")
            for l in fm[i+1:j] if l.strip().startswith("- ")]

def render(key, vals, quote):
    fmt = '  - "%s"' if quote else "  - %s"
    return ["%s:" % key] + [fmt % v for v in vals]

def set_list(fm, key, add, quote):
    s = span(fm, key)
    have = items(fm, s) if s else []
    new = have + [a for a in add if a not in have]      # append-only, deduped
    if new == have:
        return fm, []
    block = render(key, new, quote)
    if s:
        return fm[:s[0]] + block + fm[s[1]:], [a for a in new if a not in have]
    after = ORDER[:ORDER.index(key)]                    # key missing: insert at canonical spot
    pos = 0
    for i, l in enumerate(fm):
        k = l.split(":", 1)[0]
        if k in after:
            pos = i + 1
    return fm[:pos] + block + fm[pos:], new

def body_of(lines, end):
    return lines[end:]                                  # from the closing fence onward, untouched

def commit(path, raw, lines, end, new_fm):
    body = body_of(lines, end)
    new_text = "\n".join(["---"] + new_fm + body)
    old_body_sha = hashlib.sha256("\n".join(body).encode()).hexdigest()
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)
    os.replace(tmp, path)                               # atomic, same volume
    _, l2, e2, _ = parse(path)                           # re-read and verify
    if hashlib.sha256("\n".join(body_of(l2, e2)).encode()).hexdigest() != old_body_sha:
        open(path, "wb").write(raw)                      # rollback from memory
        raise AssertionError("Body verändert — zurückgerollt, Notiz übersprungen")
    return old_body_sha

# Beispiel für eine Notiz:
# raw, lines, end, fm = parse(path)
# fm, _ = set_list(fm, "tags", ["Ökonomie", "🔗"], quote=False)
# fm, _ = set_list(fm, "related", ['[[Wirtschaft & Ökonomie]]'], quote=True)
# fm, _ = set_list(fm, "updated", ["2026-07-29T14:31"], quote=False)  # single-value keys: replace, see below
# commit(path, raw, lines, end, fm)
```

## Invariants

- **Append-only.** No code path in `set_list`/`render` removes an existing list item.
- **Deduplicated** against existing values (and, per the tagging rules, against `Absorbiert`
  synonyms already present — that check happens before calling `set_list`, not inside it).
- **Canonical insertion point.** A missing key is inserted at the position the `Note Template.md`
  field order implies (`type, created, updated, aliases, tags, urls, related, authors, sources,
  year, reference`), not appended at the end of the block.
- **Fail-closed.** `parse()` raises on any structural anomaly (bad bytes, no frontmatter,
  unclosed frontmatter, invalid YAML, frontmatter that isn't a map) — catch it at the call site,
  mark the note ambiguous, log, and move on. Never guess a repair.
- **Atomic write.** `os.replace` on a temp file created in the same directory (so it's on the
  same filesystem, guaranteeing atomicity) — Obsidian never observes a half-written file.
- **Post-write body verification with in-memory rollback.** After writing, the file is re-parsed
  and its body hash is compared against the pre-write body hash. Any mismatch triggers an
  immediate rewrite from the original `raw` bytes still held in memory, and the note is reported
  as failed rather than silently left in a mutated state.
- **Rendering matches the vault's existing convention exactly**: plain tags unquoted
  (`  - Ökonomie`), wikilinks double-quoted (`  - "[[Politik]]"`). Inline-flow `tags: [a, b]`
  (a minority shape, ~21 notes) is normalized to block style on write — a frontmatter-only change
  that moves the note onto the vault's dominant convention.

## `updated` and single-value keys

`updated` is a single scalar, not a list — replace it directly rather than through `set_list`:

```python
def set_scalar(fm, key, value):
    s = span(fm, key)
    line = "%s: %s" % (key, value)
    if s:
        return fm[:s[0]] + [line] + fm[s[1]:]
    after = ORDER[:ORDER.index(key)]
    pos = 0
    for i, l in enumerate(fm):
        if l.split(":", 1)[0] in after:
            pos = i + 1
    return fm[:pos] + [line] + fm[pos:]
```

Always bump `updated` to `YYYY-MM-DDTHH:MM` (now) on every note the skill finishes — matching the
`update-time-on-edit` Obsidian plugin's own format, so the two never fight each other, and
matching the convention already used by `obsidian-process-pages`.

## Formatting, after the mutator

```bash
prettier --write "<pfad zur notiz>"
```

Run this after the frontmatter commit, on every note the skill touches — not conditionally.
Take the journal's `body_sha256` (see below) **after** this step, so the undo path's guard
compares against what the run actually left on disk.

## Journal and undo

Format, one file per run, following the existing precedent
`99 Meta/references/obsidian-process-pages-2026-07-16-700.json`:

`99 Meta/references/connect-notes-<YYYY-MM-DD>-<HHMM>.json`

```json
{
  "skill": "obsidian-connect-notes",
  "mode": "notes",
  "started": "2026-07-29T14:30",
  "seed": 202607291430,
  "scope": "wide",
  "pool_before": 4385,
  "notes": [
    {
      "path": "04 Permanent/Nudge und Verhaltensökonomie.md",
      "tags_added": ["Ökonomie", "🔗"],
      "related_added": ["[[Wirtschaft & Ökonomie]]"],
      "updated_set": "2026-07-29T14:31",
      "body_sha256": "a3f1…"
    }
  ],
  "registry_delta": { "kandidaten_neu": ["Verhaltensökonomie"] },
  "unresolved_before": 412,
  "unresolved_after": 412
}
```

Every entry records an *addition*, so undo is exact and mechanical — never relies on `git`
(see the "why not" in `SKILL.md`'s Undo section):

```python
def undo(entry):
    raw, lines, end, fm = parse(entry["path"])
    current = hashlib.sha256("\n".join(body_of(lines, end)).encode()).hexdigest()
    if current != entry["body_sha256"]:
        return "übersprungen: Notiz wurde seither verändert"
    for key, added in (("tags", entry["tags_added"]), ("related", entry["related_added"])):
        s = span(fm, key)
        if not s: continue
        have = items(fm, s)
        remaining = [v for v in have if v not in added]
        fm = fm[:s[0]] + (render(key, remaining, key == "related") if remaining else []) + fm[s[1]:]
    commit(entry["path"], raw, lines, end, fm)
    return "zurückgenommen"
```

This is strictly better than a git revert for this use case: it only ever removes the exact
strings this run added, guarded by the recorded body hash, so it can never clobber a human edit
made to the note after the run.
