# Index-Modus

Target for `00 Maps of Content/00 - Index.md`: two levels — fixed `##` domain headings, a flat
alphabetical `- [[MOC]]` bullet list under each. Only MOCs with a row in the registry's
`## Kategorien` table are eligible for a place in the Index; the long tail of every other MOC
stays reachable through the existing `99 Meta/bases/Maps of Content.base` view. A hundred-plus
entry index is a worse navigation page than an 80-entry one — the Index is a curated hub, not a
complete directory.

## Die 8 Domänen (fixed, never re-derived per run)

```
## Denken & Wissen        ## Wirtschaft & Geld     ## Kultur & Kunst
## Mensch & Psyche         ## Gesundheit & Körper   ## Leben & Alltag
## Gesellschaft & Politik  ## Technik & Handwerk    ## Unsortiert
```

These come from the registry's `Domäne` column, not invented fresh each run — that's what makes
repeated `index` runs group things the same way every time instead of reshuffling. `## Unsortiert`
holds any link with no registry row.

## Nie-einen-Link-verlieren-Algorithmus

Run this exact sequence, and abort rather than write if step 3 fails:

1. **Parse the current body** into `L0` = the ordered list of every `[[…]]` occurrence, keeping
   the display text exactly as written — `[[Künstliche Intelligenz|Artificial Intelligence]]`
   stays exactly that string. Never normalize `[[X|X]]` down to `[[X]]`, and never reorder or
   drop anything at this stage.
2. **Build `L1`** from the registry: under each `Domäne` heading, one bullet per `## Kategorien`
   row whose `MOC` column is non-empty and whose domain matches; then, under `## Unsortiert`,
   every entry from `L0` whose target has no matching registry row at all.
3. **Assert `targets(L0) ⊆ targets(L1)`.** Every link target present in the current file must
   still be present in the new version. If this assertion fails for any target: **write
   nothing**, abort `index` mode for this run, and report exactly which targets would have been
   dropped and why.
4. **Assert every bullet in `L1` resolves** to an existing file (exact basename or a known
   alias). If a bullet from the registry doesn't resolve, drop only that bullet from `L1` and
   report it. If a bullet that was already in `L0` doesn't resolve (a pre-existing broken link),
   **keep it anyway** — never remove a human link just because this skill can't verify it — and
   report it as broken.
5. Write the result, then:
   ```bash
   prettier --write "00 Maps of Content/00 - Index.md"
   ```

## Incrementality across runs

- **The first-ever live run of `--mode index` is regroup-only**: introduce the 8 headings and
  move the existing 28 (or however many are current) links underneath them by domain, adding
  nothing new. Because this rewrites a human-authored file's whole structure in one pass, **this
  specific run requires an explicit confirmation from the user before writing**, even outside
  `--dry-run`. Every later run only adds — never removes, never reorders what's already grouped.
- Every run after the first adds at most **10 new bullets** total (spread across whichever
  domains have newly-MOC'd categories) and removes nothing.
- `00 - Index.md`'s frontmatter also gains `tags:\n  - 🤖\n  - MOC` if it's still `tags: []` —
  fixing the fact that the Index itself isn't currently discoverable as a Map of Content. This is
  a frontmatter-only change and follows the same mutator as ordinary notes (see
  `references/frontmatter-bearbeitung.md`), just applied to this one file.

## Reporting

After any `index` run (dry or live), report: which domain each newly-added MOC landed in, the
count of links carried over unchanged, any targets flagged as pre-existing broken links, and
whether this was the first (regroup) run or an incremental one.
