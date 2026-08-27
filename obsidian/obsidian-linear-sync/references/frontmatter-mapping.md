# Frontmatter mapping

Field order is binding and identical to the two templates the skill expects in the vault's
template folder (`Linear Ticket Template.md`, `Linear Project Template.md`). Those templates are
normally excluded from prettier and serve as the authoritative schema documentation.

Examples use a fictional team key `ENG`, project `Website Redesign`, and person `Ada Lovelace`.

## Vault conventions honoured

- Keys lowercase and unquoted; `type:` values in Title Case.
- **Empty fields stay as a bare `key:`** — never `null`, never `[]`.
- Lists as blocks with two-space indentation: `  - item`.
- Wikilinks in values **double-quoted**: `- "[[Ada Lovelace]]"`.
- Multi-word keys use spaces (`status type`, `blocked by`, `linear updated`), following the
  existing project-template convention in this vault family.
- `created`/`updated` as `YYYY-MM-DDTHH:mm`, **unquoted**. Semantic dates (`started`,
  `completed`, `startdate`) as `YYYY-MM-DD`, unquoted.
- Full precision (with seconds/milliseconds/zone) is **also unquoted** — `linear updated`,
  `comments latest`, `synced through`. Quoting looks safer but is wrong here: Obsidian's
  frontmatter serializer strips the quotes as soon as the file is touched in the app. We write
  quoted, Obsidian unquotes, every sync sees a change — an endless flip-flop. Unquoted is
  Obsidian's canonical form and therefore a fixed point.

## Ticket note (`type: Linear Ticket`)

| #   | Key                   | Linear source              | Form                                 | Note                                                                                                                                                              |
| --- | --------------------- | -------------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `type`                | —                          | `Linear Ticket`                      | constant                                                                                                                                                          |
| 2   | `status`              | `status`                   | `Done`                               | free workflow name                                                                                                                                                |
| 3   | `status type`         | `statusType`               | `completed`                          | machine-readable; drives index grouping                                                                                                                           |
| 4   | `priority`            | `priority.name`            | `Medium`                             | **not** `priority.value`: Linear's scale is inverted (1=Urgent … 4=Low, 0=None), so numeric sort is wrong                                                         |
| 5   | `created`             | `createdAt`                | `2026-05-04T16:28`                   | local time, minute precision                                                                                                                                      |
| 6   | `updated`             | — (local)                  | `2026-05-04T16:44`                   | vault edit time; only advances on a real change                                                                                                                   |
| 7   | `aliases`             | `id` + history             | `  - ENG-42`                         | element 0 is always the identifier (quick switcher, autocomplete). **Does not resolve bare wikilinks** — see `write-pipeline.md`. Then up to 4 previous filenames |
| 8   | `tags`                | —                          | `Linear`, `Ticket`                   | union; never removes the user's own tags                                                                                                                          |
| 9   | `urls`                | `url`                      | unquoted                             | union; the Linear URL comes first                                                                                                                                 |
| 10  | `related`             | —                          | empty                                | **user-owned**, never written                                                                                                                                     |
| 11  | `project`             | —                          | `"[[Website Redesign]]"`             | always resolves — the skill creates the index note                                                                                                                |
| 12  | `id`                  | `id`                       | `ENG-42`                             | **the sync key**                                                                                                                                                  |
| 13  | `title`               | `title`                    | verbatim                             | the round-trip-safe copy, since the filename is sanitized                                                                                                         |
| 14  | `team`                | `team`                     | `Engineering`                        | the name, not the key                                                                                                                                             |
| 15  | `assignee`            | `assignee`                 | `"[[Ada Lovelace]]"`                 | via `link_or_text`                                                                                                                                                |
| 16  | `creator`             | `createdBy`                | `"[[Ada Lovelace]]"`                 | not `author` — `authors:` already means "author of a source" in this vault family                                                                                 |
| 17  | `labels`              | `labels[]`                 | block list                           | casefold-sorted                                                                                                                                                   |
| 18  | `estimate`            | `estimate`                 | number or empty                      |                                                                                                                                                                   |
| 19  | `milestone`           | `projectMilestone`         | name or empty                        |                                                                                                                                                                   |
| 20  | `parent`              | `parentId`                 | `"[[ENG-40 Title\|ENG-40]]"` / empty | piped                                                                                                                                                             |
| 21  | `blocks`              | `relations.blocks[].id`    | `  - "[[ENG-51 Title\|ENG-51]]"`     | piped, sorted by identifier                                                                                                                                       |
| 22  | `blocked by`          | `relations.blockedBy[].id` | block list                           |                                                                                                                                                                   |
| 23  | `related to`          | `relations.relatedTo[].id` | block list                           |                                                                                                                                                                   |
| 24  | `duplicate of`        | `relations.duplicateOf`    | wikilink or empty                    |                                                                                                                                                                   |
| 25  | `started`             | `startedAt`                | `2026-05-04`                         | minute precision lives in the history table                                                                                                                       |
| 26  | `completed`           | `completedAt`              | `2026-05-04`                         |                                                                                                                                                                   |
| 27  | `canceled`            | `canceledAt`               | date or empty                        |                                                                                                                                                                   |
| 28  | `archived`            | `archivedAt`               | date or empty                        | archived ≠ disappeared                                                                                                                                            |
| 29  | `due`                 | `dueDate`                  | `YYYY-MM-DD`                         | Linear already returns a plain date                                                                                                                               |
| 30  | `branch`              | `gitBranchName`            | unquoted                             |                                                                                                                                                                   |
| 31  | `linear updated`      | `updatedAt`                | `…171Z` unquoted                     | **the change detector**                                                                                                                                           |
| 32  | `comments count`      | —                          | number or empty                      | sanity check                                                                                                                                                      |
| 33  | `comments latest`     | max `updatedAt`            | unquoted                             |                                                                                                                                                                   |
| 34  | `sync hash`           | —                          | `v2-` + 64 hex                       | body only, after prettier — see `write-pipeline.md`                                                                                                               |
| 35  | `sync missing since`  | —                          | date or empty                        | cleared automatically on reappearance                                                                                                                             |
| 36  | `sync missing reason` | —                          | `deleted` / `moved` / empty          |                                                                                                                                                                   |

**Not mirrored:** attachments other than GitHub PR/commit links, `documents`, `sla*`,
`triageIntel`, `cycleId`, `delegate`, and all pure UUID fields (`assigneeId`, `createdById`,
`teamId`, `projectId`) — no use in the vault.

**No `synced:` on tickets.** A per-run timestamp would produce one git diff per note per run even
when Linear is unchanged. `linear updated` already answers "is this fresh?" and only moves when
Linear moves. `synced` lives on the index note alone.

**Linear labels do not become tags.** A curated vault tag namespace should not absorb Linear's
project-local vocabulary (`bug`, `p0`, a team name) — it would pollute the tag registry and the
graph. Labels stay in `labels:`.

## Index note (`type: Linear Project`)

Order: `type`, `status`, `status type`, `priority`, `created`, `updated`, `aliases`, `tags`,
`urls`, `related`, `title`, `summary`, `initiative`, `team`, `lead`, `members`, `labels`,
`milestones`, `startdate`, `enddate`, `completed`, `canceled`, `tickets total`, `tickets open`,
`tickets done`, `uuid`, `linear updated`, `synced`, `synced through`, `synced census`,
`sync comments`, `sync lang`, `sync pending`.

Specifics:

- `summary` typically contains `: ` and is therefore double-quoted.
- `initiative` stays **plain text** unless a note for it exists — `link_or_text` never invents a
  note, so the mirror cannot add an unresolved link.
- `members` holds **names only**, never `members[].email`.
- `team` is a scalar for one team, a block list for several. `teams[].key` is not stored: the
  team key is not the project discriminator — a ticket in a different project can share it.
- `startdate`/`enddate` ← `startDate`/`targetDate`.
- `uuid` ← `project.id`. Issues have no counterpart (see `sync-algorithm.md`).
- **Dropped:** `icon`, `color`, `resourceCount`, `startDateResolution`, `targetDateResolution`,
  `startedAt` (redundant with `startdate` + `status`). No filler.

## Ownership

| Region                             | Owner           | Sync behaviour                                            |
| ---------------------------------- | --------------- | --------------------------------------------------------- |
| Fields 2–5, 11–36                  | Linear          | overwritten on every run                                  |
| `created`                          | Linear          | set once                                                  |
| `updated`                          | sync + plugin   | local time, only on a real change                         |
| `aliases`, `urls`                  | sync, **union** | guarantees identifier / Linear URL, never removes entries |
| `tags`                             | user, **union** | guarantees the defaults, never removes the user's own     |
| `related`                          | user            | never touched                                             |
| `synced*` (index only)             | sync            | local time                                                |
| Body between the markers           | sync            | fully regenerated                                         |
| Body from `<!-- linear:end -->` on | user            | **never** touched                                         |

The union rules make a tagging/linking skill harmless if it ever touches these notes. Even so,
the mirror folder should be on such a skill's exclusion list so vault category tags do not leak
into machine-generated files.

## Body layout

**Ticket:** frontmatter → `<!-- linear:begin … -->` → description section (headings demoted to
`###`) → pull requests → history table → `---` → comments (`### Author · time`, replies as
`### ↳ …`, inline comments with a quote blockquote) → `<!-- linear:end -->` → notes heading.

**Index:** frontmatter → marker → description → tickets (total line, then one group per
`status type` with a table `Ticket | Title | [Milestone] | Priority | Updated`, pipe escaped as
`\|` inside cells) → marker → notes heading.

Sections with no content are **omitted**, not rendered empty. In the frontmatter the opposite
holds (bare `key:`) — deliberately different rules.

Group order and labels come from `LABELS[lang]["groups"]`: `triage`, `started`, `unstarted`,
`backlog`, `completed`, `canceled`. Empty groups are dropped. Sorting within a group is natural
by identifier (`ENG-42` < `ENG-118`), with sub-issues pulled directly under their parent behind a
`↳ ` prefix.

Grouping is by `status type`, **not** by milestone: a project without milestones would yield a
single "no milestone" bucket. When a project does have milestones, a **column** is added — the
grouping stays the same. One structure, one code path.

History durations are deterministic: the open row shows `–` in both the end and duration columns.
A running "6 h ago" would produce a diff on every run. Duration is the largest unit, floored.

## `type` enum

`Linear Project` and `Linear Ticket` should be added to whatever file documents the vault's
`type:` vocabulary. Nothing validates that enum, but other skills read it as the vault contract.

## Localization

Rendered section headings, group names and duration units come from `LABELS[lang]` in the script
(`en` default, `de` provided). The templates in the vault should match the language configured
via `sync lang`, since the skill regenerates those headings on every run.
