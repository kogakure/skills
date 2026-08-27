# Sync algorithm

Everything here was verified live against a real Linear project. Examples use a fictional
workspace `acme`, team key `ENG`, and project `Website Redesign`.

## Verified API properties

These four points determine the design. Do not re-derive them.

**1. `list_issues` accepts a server-side `updatedAt` filter with strictly-after semantics.**

```
list_issues(project=<id>, fields=["id","updatedAt"], updatedAt="2026-05-04T11:14:00.000Z")
→ only issues updated after that instant; one at 11:13:56 is correctly absent
```

That is why a re-sync in the steady state is **not** "fetch everything and diff" but a single
call returning **zero rows**.

**2. The MCP `id` of an issue is the identifier (`"ENG-42"`), not a UUID.** `get_issue` returns
`createdById`, `assigneeId`, `projectId`, `teamId` as UUIDs, but no issue UUID. The identifier is
therefore the only available sync key.

**3. `list_projects(query=…, fields=[…])` costs ~100 tokens; `get_project` costs several
kilobytes** because of `description`. Always probe first, then call `get_project` only when
`updatedAt` changed.

**4. An unset field is absent, not `null`** (`parentId`, `projectMilestone`, `estimate`).
Missing must be treated like `null`, not as an error.

Also: `fields` rejects `identifier`. `statusType` is one of
`backlog | unstarted | started | completed | canceled`. Timestamps are UTC with milliseconds.
`get_project(includeMilestones=true)` returns milestones inline, so `list_milestones` is
unnecessary.

## Phases

### Phase 0 — Preconditions; no API calls, no writes

Check the vault root, check `prettier`, then call `plan` with an empty `issues` list. The script
returns:

- `watermark` — `min(index.synced through, max(linear updated across local notes))`. The `min()`
  is the self-healing step: a watermark that has run ahead of what is on disk (an aborted
  previous run) is pulled back, never trusted forward.
- `census_due`, `index_exists`, `need_project_detail`, `local_count`
- `warnings` — including the `update-time-on-edit` hint

### Phase 1 — Project probe

`list_projects(query, fields=["id","name","url","updatedAt"], limit=5)`. Exactly one match.
Only on a differing `updatedAt` or `--force`: `get_project(query=<id>, includeMilestones=true)`.

The **project name from Linear** determines the folder name — not the user's argument.

### Phase 2 — Cheap issue pass

Delta (default) with `updatedAt=<watermark − 60 s>` and the full `fields` array from SKILL.md.

Three things that are easy to get wrong:

- **`includeArchived=true` on the delta pass too.** Archiving is a mutation and bumps
  `updatedAt`, but with `includeArchived:false` the archived issue drops out of the result and
  the event goes unnoticed until the next census. One boolean buys correctness.
- **A 60-second negative skew** on the watermark absorbs clock drift and same-second writes.
  Cost: an occasional redundant `get_issue`.
- **Pagination:** `while hasNextPage: cursor = resp["cursor"]`, hard cap 20 pages (5 000
  tickets), then abort with a clear message rather than looping forever.

Census additionally: `list_issues(project, includeArchived=true, limit=250,
fields=["id","archivedAt"])` as `roster`.

### Phase 3 — Fetch plan

`plan` with the real `issues` returns one verdict per identifier:

| Verdict          | Condition                                                    | Consequence                   |
| ---------------- | ------------------------------------------------------------ | ----------------------------- |
| `NEW`            | not present locally                                          | `get_issue` + `list_comments` |
| `CHANGED`        | `linear updated` differs, or `--force`, or in `sync pending` | `get_issue` + `list_comments` |
| `UNCHANGED`      | equal and `sync hash` matches                                | nothing                       |
| `CONFLICT`       | `sync hash` differs → managed region hand-edited             | nothing, report               |
| `MARKER_MISSING` | marker absent from the file                                  | nothing, report               |

`missing_candidates` appears only when `census_due`.

### Phase 4 — Detail fetch

Only for `fetch`: `get_issue(id, includeRelations=true)` and
`list_comments(issueId, limit=250, orderBy="createdAt")`, both paginated.

Not fetched: `includeCustomerNeeds`, `includeReleases`. Attachments arrive with `get_issue` but
are filtered to GitHub PR/commit links.

### Phase 5 — Apply

`apply` with the full payload. The script renders, normalizes, compares and writes.

### Phase 6 — Reconciliation (census only)

Only a census can see **absence** — a delta pass with no rows is indistinguishable from "no
changes". It therefore runs automatically on first import, on `--census`, on `--force`, and when
`now − synced census > 7 days`.

Because archived issues are in the `roster`: **archived ≠ disappeared.** Archived tickets get
`archived:` set and stay where they are.

For each genuinely missing identifier, one `get_issue(id)` classifies it → `moved` (with the new
project named in the report) or `deleted`. Passed back as `missing_reasons`.

Behaviour: **never delete, never move.** `sync missing since` is set once (a second census does
not rewrite it → no diff). If the ticket reappears, both markers are cleared automatically.

### Phase 7 — Advance state, report, re-index

`synced through` advances to `max(row.updatedAt)` — **only if there were no failures.**
Otherwise it stays put and the affected identifiers land in `sync pending`. On `--dry-run`
nothing advances. Then `qmd update && qmd embed`.

## Call budget

| Scenario                                | MCP calls                                |
| --------------------------------------- | ---------------------------------------- |
| Re-sync, nothing changed, no census due | **2**                                    |
| Re-sync, 3 tickets changed              | 2 + 6 (+1 if the project itself changed) |
| Census, nothing changed                 | 4                                        |
| First import, 100 tickets               | 3 + 200 → hits `--max-fetch`, asks first |

## Open assumption: does a comment bump `updatedAt`?

`list_comments` has no `updatedAt` filter and there is no project-wide comment listing, so there
is no cheap probe. If the assumption does not hold, a new comment on an otherwise unchanged
ticket would be missed until the next `--force`.

**Test recipe (once):** note the watermark, add a comment to a ticket in Linear, then call
`list_issues(project, fields=["id","updatedAt"], updatedAt=<watermark>)`.

- The ticket comes back → the assumption holds, nothing to do.
- It does not → add a `COMMENTS_ONLY` verdict: re-poll comments on a 24 h TTL, restricted to
  tickets whose `statusType` is not `completed`/`canceled`.

**Result:** _(not yet tested — record it here)_

## Path A: GraphQL fetch

`linear_sync.py fetch` / `sync` reads the same data straight from
`https://api.linear.app/graphql` (standard library only, `urllib`). One run yields the project,
all tickets, relations, state history and comments; afterwards the identical `apply` code runs.
Advantage: nothing passes through the agent's context, there are no transcription errors, and it
is cron-capable.

**Key resolution** in this order: `LINEAR_API_KEY`, `LINEAR_API_KEY_FILE`,
`~/.config/linear/api-key`. The key appears only in the `Authorization` header, is never logged,
and is never interpolated into an error message. If it is missing the script aborts and the user
is asked.

**Required scope: `read`.** The script issues three queries (`projects`, `project`, `issues`) and
zero mutations — a one-way mirror needs nothing else. Note that Linear personal API keys are not
scopable per project: `read` covers everything the account can see.

### Two schema traps

**1. `Project.description` and `Project.content` are swapped relative to the MCP shape.**
In GraphQL, `description` is the _short_ summary and `content` is the long markdown body. The MCP
layer serves them the other way round. The normalizer flips them back:

```python
"summary":     proj["description"]   # short
"description": proj["content"]       # long markdown body
```

Confusing these mirrors a one-line summary as the project description.

**2. `stateHistory` does not exist in GraphQL.** It must be reconstructed from
`history { fromState toState createdAt }`: each `toState` starts at the transition and ends at
the next one; the first `fromState` is the state the ticket was created in.

Both were verified against real MCP output — state history (all timestamps identical) and
relations (`blocks`, `blockedBy`, `relatedTo`) match exactly. `relations` **and**
`inverseRelations` must both be queried: `blocks` in `relations` means "blocks", the same type in
`inverseRelations` means "is blocked by".

### What GraphQL does not provide

`quotedText` on comments (the snippet an inline comment is anchored to) is not in the public
schema and is set to `null`. Inline comments then render without their quote block, otherwise
identically. If those quotes matter for a given project, use path B for it.
