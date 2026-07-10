# Footnote parsing

## Formats to remove

**Inline marker** — appears in body prose, sometimes preceded by a position marker:

```
...und in herausfordernden Situationen.[^crouch2022jv]
...at [28:55][^crouch2022jv]
```

**Definition line** — always at/near the bottom of the note:

```
[^crouch2022jv]: Andy Crouch and McKay (2022): _The Life We’re Looking For_, <https://the-art-of-manliness.simplecast.com/episodes/the-life-were-looking-for-5zT960zt>. [52:10]
```

General pattern: `[^id]: <author>(YYYY): <title>, <<url>>.`

- `id` — usually `authorlastnameYYYYxx` (two-letter suffix), occasionally `AuthorCamelCaseYYYY`
  with no suffix. Treat whatever string is between `[^` and `]` as the id verbatim.
- `<author>` — usually `[[Wikilink]]`, sometimes a plain name, sometimes two names joined by
  `and`/`und`/`&`/`,` (see multi-author below).
- `(YYYY)` — the year, in parentheses right after the author.
- `<title>` — usually italicized with `_..._`, occasionally plain text.
- `<<url>>` — the URL wrapped in angle brackets, trailing period after the closing `>`.

## Extraction steps

1. Find every `[^id]: ...` line in the body. For each:
   - `id` → append to `reference` frontmatter list (dedupe if already present).
   - author segment → parse into one or more `[[Wikilink]]` names for `authors`.
   - year → `year`.
   - title (strip `_..._` markers) → `sources` (plain string, never wikilinked).
   - url (strip `<...>`) → append to `urls`.
   - if the url's domain maps to a known publication (see table below) → `publication: "[[Name]]"`.
2. Find every inline `[^id]` marker in the body matching one of the ids just parsed and delete it.
   - If a position marker like `[28:55]` (timestamp) or a page number immediately precedes the
     marker, capture it for `position` (Quote template only — Note has no `position` field, so
     just drop the marker text for Note).
3. Delete the `[^id]: ...` definition line(s) entirely, and any now-blank trailing lines they leave.
4. If a `[^id]:` line doesn't match the general pattern closely enough to confidently extract
   author/year/title/url, do NOT guess — leave the note alone and mark `❓` (reason: "malformed
   footnote").

## Multi-author splitting

Split the author segment on `and`, `und`, `&`, or `, ` — but only when what results on
each side looks like a plausible name (avoid splitting a single hyphenated/compound name that
happens to contain "and"). Example: `Andy Crouch and McKay (2022)` → `[[Andy Crouch]]`,
`[[McKay]]`. Wrap each resulting name in `[[...]]` if not already wikilinked.

## Publication inference from URL domain (best-effort, optional)

Only fill `publication` when the domain confidently maps to a known outlet, e.g.
`quillette.com` → `[[Quillette]]`. If the domain is unrecognized or ambiguous, leave
`publication` empty — it's an optional field, not a reason to `❓`.

## `published` date rule

Only set `published` when a full `YYYY-MM-DD` is available (e.g. from an `embed` block's
metadata or explicit date in the source). The footnote's bare `(YYYY)` alone is NOT enough
for `published` — it only supplies `year`. If no day/month is known, omit `published` entirely
(a partial date is invalid and must not be written).

## Things to leave alone

- ` ```embed ``` ` blocks (link preview metadata) — preserve verbatim, don't parse them as
  footnotes even though they duplicate the same title/url/description.
- Callouts (`> [!SUMMARY]`) and regular blockquotes — not footnotes, leave untouched.
- Any `[^id]` reference whose definition line is missing entirely, or vice versa — mark `❓`
  (reason: "footnote id/definition mismatch") rather than partially processing.
