# Write pipeline

Implemented in `scripts/linear_sync.py`. This document explains **why** the order is what it is
— every item below is a failure mode that actually occurred, not theory.

Examples use a fictional workspace `acme`, team key `ENG`, and project `Website Redesign`.

## Rendering order (`render_markdown`)

```
1  normalize: CRLF → LF, trim line ends, NFC
2  mask fenced code         (FENCE_RE)   ← first
3  mask inline code         (INLINE_CODE_RE)
4  resolve Linear tags      (rewrite_tags)
4b issue markdown links     (rewrite_issue_mdlinks)   ← before masking
5  mask links               (LINK_RE)
6  bare identifiers         (rewrite_bare)
7  unmask links
8  repair emphasis          (tidy_emphasis)
9  uploads.linear.app       (fix_uploads)
10 task lists               (downgrade_tasks)
11 demote headings          (demote_headings)
12 strip foreign HTML       (strip_stray_html)
13 unmask inline code
14 unmask fenced code       ← always last
```

**Step 5 is the non-obvious one.** Step 4 emits
`[ENG-9](https://linear.app/acme/issue/ENG-9/…)` — text that contains `ENG-9` twice. Without
masking, step 6 would rewrite inside its own output.

Masking replaces each match with `\x00<tag><n>\x00`. NUL does not occur in Linear markdown,
carries no markdown meaning, and survives every regex in the pipeline.

## Verified regexes

```python
FENCE_RE = re.compile(
    r"(?ms)^(?P<i>[ ]{0,3})(?P<f>`{3,}|~{3,})[^\n]*\n.*?(?:^(?P=i)(?P=f)[^\n]*$|\Z)")
INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
LINK_RE = re.compile(
    r"\[\[[^\]\n]*\]\]|!?\[[^\]\n]*\]\([^)\s]*\)|<https?://[^>\s]+>|https?://\S+")
IDENT_RE = re.compile(
    r"(?<![0-9A-Za-z_\-/])([A-Z][A-Z0-9]{1,9})-([0-9]{1,6})(?![0-9A-Za-z_\-])")
```

`FENCE_RE` properties, all verified: an unclosed fence at end of file is masked to EOF (`\Z`
branch); a ` ````md ` block containing ` ``` ` is masked as **one** block (`(?P=f)` requires an
equal-length fence); 3-space-indented and `~~~` fences are covered. Four-space-indented blocks
are **not** masked — Linear always fences, and in Linear markdown a four-space indent means a
list continuation.

## The team-key gate

`IDENT_RE` alone is **not** sufficient. It matches `UTF-8`, `COVID-19`, `HTTP-2`, `ISO-8601` —
all of which appear in real ticket prose.

```python
def rewrite_bare(text, ctx):
    def sub(m):
        if m.group(1) not in ctx.team_keys:   # ← without this line: data damage
            return m.group(0)
        return resolve_ident(m.group(0), ctx)
    return IDENT_RE.sub(sub, text)
```

`team_keys` is derived from the project's own identifiers plus `project.teams[].key`, so there
is no configuration that can go stale.

## Resolution rule

```python
def resolve_ident(ident, ctx, table=False):
    if ident == ctx.self_id:  return ident                       # never self-link
    entry = ctx.index.get(ident)
    if entry is not None:                                        # in this project
        stem = entry["stem"]                                     # filename without .md
        sep = "\\|" if table else "|"                            # table cell
        return f"[[{stem}{sep}{ident}]]"
    href = ctx.hrefs.get(ident)
    return f"[{ident}]({href})" if href else ident               # foreign / unknown
```

**Safety property:** an identifier is rendered as a wikilink _only_ if it is in the index of the
mirrored project. Foreign identifiers can at most become external markdown links. The mirror
cannot create a dangling wikilink.

`ctx.hrefs` comes from `harvest_refs()`, a pre-pass over **all** descriptions and comments in the
payload. That is the only way tickets from other projects get real URLs, and it must run before
the first file is rendered.

## Why piped `[[ENG-42 Title|ENG-42]]` and not bare `[[ENG-42]]`

**A bare `[[ENG-42]]` link does not resolve in Obsidian.** Verified against a live vault's
metadataCache:

```js
app.metadataCache.getFirstLinkpathDest("ENG-42", src); // -> null
getFileCache(f).frontmatter.aliases; // -> ["ENG-42"]  (alias IS indexed)
app.metadataCache.unresolvedLinks[src]; // -> every ticket identifier
```

Obsidian indexes `aliases:` for the quick switcher and link autocomplete, but does **not** use
them to resolve a wikilink that is already written. A first draft of this skill relied on bare
links plus an alias and produced a folder full of broken links — precisely what the rule "never
emit a dangling wikilink" exists to prevent.

Resolution goes through the **filename**; the identifier is the display text:
`[[ENG-42 Rework the checkout flow|ENG-42]]`.

The usual objection — renames break piped links — does not apply here: **every body containing
such links is regenerated on the next sync.** Rename churn is free in a machine-generated
mirror. It only costs in hand-written notes, and this skill does not write those.

`aliases:` is still set: it makes the ticket findable as `ENG-42` in the quick switcher, and
hand-written references work once inserted through autocomplete (Obsidian then writes the piped
form itself).

**In table cells the pipe must be escaped as `\|`**, or it splits the column.
`resolve_ident(..., table=True)` handles that.

## Two encodings of the same mention

The two fetch paths encode the same mention differently:

| Path    | Encoding in the source text                     |
| ------- | ----------------------------------------------- |
| MCP     | `<issue id="…" href="…">ENG-42</issue>`         |
| GraphQL | `[ENG-42](https://linear.app/…/issue/ENG-42/…)` |

Untreated, the same reference would resolve locally on one path and point back at the web on the
other. `rewrite_issue_mdlinks()` therefore converts the markdown variant into a wikilink too —
but only when the ticket belongs to the mirror. Links to tickets outside it are left alone,
because there is no local target.

## Demoting headings

```python
new_level = min(6, old + max(0, min_level - min(all_levels)))   # min_level: 3 body, 4 comment
```

The **minimum-based** offset is the only one that guarantees no description heading lands on
`##` and collides with the note's own section headings. A first-heading-based offset would map a
document that uses both `#` and `##` as peers onto `##`, a direct collision.

Blockquote prefixes are preserved (`> # x` → `> ### x`). Headings inside fenced code do not move,
because step 11 runs after masking. Non-matches: `#tag`, `#4`, `####### seven hashes`, a `#`
mid-line.

## Emphasis repair

Linear's editor leaks bold markers around inline entities:
`**Extracted as Phase 2 (**<issue …>ENG-51</issue>**)**`.

```python
LEAK_RE = re.compile(r"([(\[{])\*\*(?P<in>[^*]*?(?:\[\[|\]\()[^*]*?)\*\*([)\]}])")
```

It fires **only** when the enclosed span contains a rewritten link, which protects legitimate
`(**bold**)`. Result: `**Extracted as Phase 2 ([[ENG-51 …|ENG-51]])**`.

Deliberate non-goal: Linear's emphasis is sometimes already malformed at the source
(`has been **extracted into **<issue>`). The mirror reproduces that faithfully rather than
guessing.

One bug this avoided: self-references must get **no** emphasis. Combined with the leaked
markers, `**ENG-51**` otherwise produced `(******ENG-51******)`.

## Images

`uploads.linear.app` is **not** downloaded: the fetch needs authentication, attachments are out
of scope, and a text-only mirror is side-effect free. But an unauthenticated `![](…)` would
render as a broken image in Obsidian — worse than a link. So `![alt](url)` becomes
`[Image: alt](url)`. Images on other hosts stay embeds.

## Prettier

```python
prettier(text, target)   # subprocess: prettier --stdin-filepath <target>
```

**The real `.md` target path is mandatory.** A typical vault `.prettierrc.json` sets
`singleQuote: true` at top level with a `*.md` override to `false`. Verified:

| Invocation                         | Result                                        |
| ---------------------------------- | --------------------------------------------- |
| `prettier --parser markdown`       | `project: '[[Website Redesign]]'` — **wrong** |
| `prettier --stdin-filepath …/x.md` | `project: "[[Website Redesign]]"` — correct   |

Relief: `proseWrap` defaults to `"preserve"`, so `printWidth` does **not** rewrap prose.
Prettier only changes list markers, emphasis characters, table padding and fence
normalization. If the generator emits those canonically, prettier becomes an assertion rather
than a transformation.

## `sync hash` — after prettier, and body only

```python
def finalize(candidate, target):
    norm = prettier(candidate, target)
    sp = split_note(norm)
    digest = managed_hash(sp.managed)
    return SYNC_HASH_LINE.sub(f"sync hash: {digest}", norm, count=1)
```

Computing the hash **before** prettier makes every file with a table look hand-edited on the next
read, because prettier realigns the columns — the run then reports `CONFLICT` for everything.
This exact bug occurred during development.

The hash covers **only the managed body**, not the frontmatter. Including frontmatter sounds
stricter but was wrong: Obsidian edits frontmatter routinely and legitimately —
`update-time-on-edit` rewrites `updated:`, and Obsidian's YAML serializer normalizes quoting and
list style whenever a note is opened. That produced a false `CONFLICT` on **every** ticket. The
frontmatter is regenerated on every run anyway; the body is the part worth protecting.

The hash carries a version prefix (`v2-`). If the formula changes, old hashes are not comparable
— without versioning every existing note would land in permanent `CONFLICT`, because an old
digest can never satisfy a new formula. An unrecognized prefix means "no reliable signal":
re-render instead of blocking.

## Quoting date values

Full-precision ISO-8601 values are written **bare**, not quoted. Quoting looks safer but is
actively wrong: Obsidian's frontmatter serializer strips the quotes the moment the file is
touched in the app. Writing them quoted creates a permanent flip-flop — we write quoted,
Obsidian unquotes, every sync sees a change. Bare is Obsidian's canonical form and therefore a
fixed point.

## Two-pass writing

`updated:` and `synced:` are wall-clock values. Set to "now" on every run, every run would
rewrite every file.

```
Pass 1: render with the STORED timestamps → identical to disk? → done, "unchanged"
Pass 2: only if something really differs → advance the timestamps and write
```

That is why a run with no Linear changes writes zero files.

## Protected region

```python
split_note(text) -> Split(fm_text, pre, managed, protected, has_markers, marker_count)
```

`managed` lies between the `linear:begin` and `linear:end` markers, matched by **regex on the
stable token** rather than the full text — the human-readable tail is localized and may be
reworded, and an exact-string match would orphan every existing note the moment it changed.
The first begin and the **last** end are used, which can only widen the protected region, never
narrow it. The end marker line belongs to the **protected** side, so the writer structurally
cannot move the boundary.

The protection check compares **no bytes** but a word multiset:

```python
def protected_intact(old, new):
    a, b = word_bag(old), word_bag(new)
    return all(b.get(w, 0) >= n for w, n in a.items())
```

Byte equality is the wrong test: prettier legitimately reformats whitespace, list markers and
emphasis inside the protected region (it inserts a blank line after the heading, for instance). A
word multiset is invariant under all of that, while a clipped sentence shows up immediately. If
the check fires, the file is **not** written and `PROTECTED_REGION_ALTERED` is reported.

## Filenames

```python
UNSAFE = {':': ' -', '/': '-', '\\': '-', '#': '', '^': '', '[': '(', ']': ')',
          '|': '-', '*': '', '?': '', '"': "'", '<': '(', '>': ')'}
```

`|`, `#`, `^`, `[`, `]` matter beyond the filesystem — they break Obsidian _wikilink targets_,
and Linear titles contain them.

Then NFC, collapse whitespace, collapse `-` runs, strip `. -` at the edges, prefix `"<ID> "`,
truncate on a word boundary. **The length check must run against
`len((base + ".md").encode())`**, not `base` — otherwise a single-word title overshoots by the
extension (measured: 203 bytes against a 200-byte cap).

## NFC

`unicodedata.normalize("NFC", …)` on content **and** every filename. APFS returns filenames
NFD-decomposed; without normalization any title containing `ö` or `—` produces a phantom rename
on every run. The easiest bug to ship and the hardest to diagnose.

## Renaming: pathlib instead of `obsidian rename`

`obsidian rename` would rewrite inbound links, but: it needs the app running, is not atomic, and
triggers `update-time-on-edit` on the file _and every linking file_ — one rename becomes N
timestamp changes and N git diffs.

Instead `os.rename`, plus: the old filename is prepended to the alias history (max 4, newest
first, deduplicated). Hand-written links from elsewhere in the vault keep resolving. This is a
pure function of _Linear plus the previous file_, so it stays idempotent.

Case-only renames need two steps through an intermediate name — APFS is case-insensitive and a
single rename would silently no-op.

## Containment

Every write goes through `write_if_changed()` or `safe_rename()`, and both call
`assert_inside(pdir, path)` as their first statement. There is no other write path — which is
why `Write` and `Edit` are absent from `allowed-tools`.

`project_dir()` additionally rejects project names containing `..` or a path separator and
asserts the parent chain equals `<vault>/01 Projects/Linear`. A Linear project named
`../../04 Permanent` cannot escape.

Writes are atomic: into `.<name>.tmp` in the **same** directory, then `os.replace`. The leading
dot keeps Obsidian from indexing the temporary file.

## Localization

Rendered note content is localized through `LABELS[lang]` (`en` default, `de` provided): section
headings, status group names, duration units, comment byline extras, entity fallback labels.
Operator messages, report keys and verdict names are **always English** so logs stay greppable.

The choice is stored as `sync lang` on the index note and, on a bare re-run, beats the default —
otherwise a vault would flip language the first time someone omitted the flag.
