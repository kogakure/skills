# Type detection

The overwhelming majority of `pages/` notes are **Note** or **Quote** — check those first.
Only fall through to the resource types below when the note is clearly *about* that kind
of resource (a dedicated record), not merely mentioning one in passing.

## Note vs Quote (the hot path)

Classify as **Quote** when any of these hold:

- The title matches the pattern `Author Name - Statement...` (a person's name, a space-hyphen-space,
  then a claim/quote).
- The note already carries the `Zitat` tag (very common: ~810 notes are `type: Note` +
  `Zitat` tag and should become `type: Quote`).
- The body's main content is a `>` blockquote of someone else's words, presented as the point
  of the note (not illustrative).

Otherwise classify as **Note** — including when the body *contains* a blockquote but:

- It's a callout (`> [!SUMMARY]`, `> [!EXAMPLE]`, `> [!INFO]`, etc.) — callouts are not quotes.
- It's a joke/dialogue snippet illustrating a concept (e.g. a SpongeBob exchange demonstrating
  "Anecdotal Evidence") rather than a citation of a real external source.
- It's a definitional/atomic note, a list, an index/MOC, or reference material (e.g. ARIA
  attribute list) — even if tagged with a topic like `Buch` for "this note is about a book I read."

**Book-tagged study notes are a trap**: a note titled "Animal Farm" with tag `Buch` that
contains a bulleted analysis is a **Note** (a permanent note *about* the book), not a
**Book** resource record. Only classify as `type: Book` when the note itself is the book's
resource record (has/should have book metadata: authors, published year, pages, genres) —
this essentially never happens in `pages/`, since Book records live in `03 Resources/Bücher/`.
When genuinely unsure whether a note is a study-note-about-X vs a resource-record-for-X → `❓`.

## Other resource types (rare in `pages/`, check only if Note/Quote clearly don't fit)

- **Person / Movie / TV Show / Podcast / Country / City / Place / Company / Product /
  Trip / Lyrics**: the note's *entire subject* is that single resource, and its content
  matches the resource's template fields (e.g. a Person note listing birthday, nationality;
  a Company note listing address/opening hours). A passing mention or wikilink to a person
  inside a Note does not make the Note a Person record.
- **Literature Note**: a structured note with `## Zusammenfassung` / `## Notizen` sections
  synthesizing a source, when it exists.

## MOC / index notes → always `❓`

If a note's body is essentially a list of `[[wikilinks]]` or `[text](url)` links with little
or no original prose (a hub/index), don't guess a type — tag `❓` and skip. These need manual
judgment on whether they belong in `00 Maps of Content/` or should be merged elsewhere.

## When to mark `UNSURE` (→ `❓` + skip)

- Can't tell Note vs Quote from title/tags/body shape.
- Content looks like a resource type but is missing the defining metadata for that type.
- The note is an index/MOC/structural hub.
- Any genuine coin-flip — prefer `❓` over guessing. False negatives (skipping a note that
  could have been processed) are cheap; false positives (wrongly reclassifying/moving) are not.
