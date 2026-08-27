---
name: obsidian-linear-sync
description: >
  Mirror a Linear project one-way (Linear → Markdown, never back) into an Obsidian vault:
  one Markdown file per ticket under `01 Projects/Linear/<Project>/`, plus an index note with
  a linked ticket table, ticket references rewritten as wikilinks, comments below a divider,
  and a protected notes section that syncing never touches. Re-running updates the files in
  place (idempotent upsert) — a run with no Linear changes writes nothing at all.
  Trigger on "sync Linear", "mirror Linear project", "Linear to Obsidian", "back up Linear",
  "import Linear tickets", "update the Linear notes", "Linear synchronisieren",
  "Linear-Projekt spiegeln", or a pasted linear.app project URL.
  This is NOT obsidian-vault-add (adds books/films/people from the web), NOT
  obsidian-connect-notes (tags and cross-links existing notes), NOT obsidian-process-pages
  (sorts a legacy `pages/` folder), NOT obsidian-search-vault (read-only search).
  Writes only inside `01 Projects/Linear/<Project>/` and never writes back to Linear.
allowed-tools: Bash(python3*), Bash(prettier*), Bash(qmd*), Bash(ls*), Bash(test*), Bash(grep*), Bash(mkdir*), Bash(obsidian backlinks*), Bash(obsidian unresolved*), ToolSearch, Read, mcp__claude_ai_Linear__list_projects, mcp__claude_ai_Linear__get_project, mcp__claude_ai_Linear__list_issues, mcp__claude_ai_Linear__get_issue, mcp__claude_ai_Linear__list_comments
---

# obsidian-linear-sync

Mirror a Linear project into an Obsidian vault as Markdown. **One-way: Linear → Markdown.**
Nothing is ever written back — no mutating Linear tool, under any circumstances.

Division of labour you must respect:

- **You** resolve the project and fetch the data (or let the script fetch it, see below).
- **The script** (`scripts/linear_sync.py`, relative to this skill directory) makes every
  reproducible decision and writes every byte. You do not render Markdown yourself, do not
  compute filenames, and do not edit a note with `Edit`/`Write`. That is exactly why `Edit`
  and `Write` are absent from `allowed-tools`.

Result per project:

```
01 Projects/Linear/Website Redesign/
  Website Redesign.md                       ← index note
  ENG-42 Rework the checkout flow.md        ← one file per ticket
  ENG-51 Ship the new nav.md
```

## Argument parsing

Arguments: `<linear-project-url | project name | project UUID> [flags]`

- **Positional** (required): the project URL, name, or UUID. From
  `https://linear.app/acme/project/website-redesign-a1b2c3d4e5f6/` the slug
  `website-redesign-a1b2c3d4e5f6` is enough. If it is missing, list the user's projects
  (`list_projects`) and ask which one.
- `--dry-run`: full run, but no writes, no folder creation, no watermark advance.
  **Recommend this for a first run on any project.**
- `--force`: ignore all watermarks and refetch every ticket. Implies `--census`.
- `--census`: force the reconciliation pass (which tickets disappeared) even if the TTL has
  not elapsed.
- `--no-comments`: do not mirror comments. The choice is stored on the index note as
  `sync comments`, so a later bare run reuses it instead of churning every file.
- `--only ENG-42,ENG-51`: just these tickets, skipping the delta pass.
- `--max-fetch <n>` (default **40**): if the fetch plan exceeds this, state the estimated
  number of calls and **ask before continuing**.
- `--lang en|de` (default `en`): language of the *rendered note content* — section headings,
  status group names, durations. Stored as `sync lang` on the index note; a bare run reuses
  it, so a vault never flips language by accident. Operator messages are always English.
- `--timezone <IANA>` (default: system zone): timezone for rendered timestamps.
- `--keep-checkboxes`: keep `- [ ]` instead of converting to `- ☐` (see below).
- `--mcp`: force path B (MCP) even when an API key is available.

Examples:

- `/obsidian-linear-sync https://linear.app/acme/project/website-redesign-a1b2c3d4e5f6/ --dry-run`
- `/obsidian-linear-sync "Website Redesign"`
- `/obsidian-linear-sync "Website Redesign" --only ENG-42`
- `/obsidian-linear-sync "Website Redesign" --force --lang de`

## Preconditions

Run from the vault root. All paths below are relative to it.

```bash
test -d "00 Maps of Content" && test -d "04 Permanent" && test -f ".prettierrc.json" \
  || echo "NOT AT VAULT ROOT — abort"
command -v prettier >/dev/null || echo "prettier missing — abort"
python3 -c "import sys; assert sys.version_info >= (3,9)" || echo "Python too old — abort"
test -f "$SC" || echo "scripts/linear_sync.py not found next to SKILL.md — abort"
```

**If the script is missing**, this skill was installed by a tool that copies only `SKILL.md`.
The skill cannot work without `scripts/linear_sync.py` — do not attempt to reimplement it
inline. Tell the user to copy the `scripts/` directory alongside `SKILL.md`, or to point `SC` at
a checkout of the skill repository.

No PyYAML and no `requests` are needed — the script is pure standard library. Do not copy an
`import yaml` precheck from another skill; this one deliberately has no such dependency.

## Loading the tool schemas

The Linear MCP tools are deferred. Load them first:

> ToolSearch with `select:mcp__claude_ai_Linear__list_projects,mcp__claude_ai_Linear__get_project,mcp__claude_ai_Linear__list_issues,mcp__claude_ai_Linear__get_issue,mcp__claude_ai_Linear__list_comments`

`list_milestones` is not needed — `get_project(includeMilestones=true)` returns milestones
inline.

## Two fetch paths

Set `SC="<this skill directory>/scripts/linear_sync.py"`.

**Path A — GraphQL (preferred when an API key exists).** One command fetches and writes
everything; **no ticket content passes through your context** and there is no transcription
risk:

```bash
python3 "$SC" sync <<'JSON'
{"opts": {"dry_run": true}, "project": "website-redesign-a1b2c3d4e5f6"}
JSON
```

The key is looked up in this order: `LINEAR_API_KEY`, `LINEAR_API_KEY_FILE`,
`~/.config/linear/api-key`. It is never printed and never interpolated into an error message.
A **read** scope is sufficient; the script issues three GraphQL queries and zero mutations. If
no key is found the script aborts with a hint — **then ask the user** whether to create one or
use path B. Never guess a key and never search the keychain for one.

`fetch` prints the same payload without writing, which is useful for debugging.

**Path B — MCP (no key needed).** You fetch through the Linear MCP tools and hand over the
payload. This always works, but every changed ticket description must pass through your context
and into the payload; a single `get_issue` result can be tens of kilobytes. Use
`details_dir`/`comments_dir` for that (see step 4).

Both paths end in the same `apply` code, produce byte-identical files, and hold the same
guarantees. The steps below describe path B; on path A, `sync` covers steps 1–5.

## Sync algorithm (path B)

### 1. Cheap project probe (1 call, ~100 tokens)

```
list_projects(query=<argument>, fields=["id","name","url","updatedAt"], limit=5)
```

Exactly one match must remain; on several, show the candidates and ask. Do **not** call
`get_project` directly — its `description` costs several kilobytes.

### 2. Cheap issue pass

Build the `plan` payload and let the script hand you the watermark:

```bash
python3 "$SC" plan <<'JSON'
{"opts": {...}, "project_probe": {"id": "...", "name": "...", "updatedAt": "..."}, "issues": []}
JSON
```

A first `plan` call with an empty `issues` list returns `watermark`, `census_due`,
`index_exists` and `need_project_detail`. Then:

**Delta pass** (default) — one call that returns **zero rows** in the steady state:

```
list_issues(project=<id>, includeArchived=true, limit=250, orderBy="updatedAt",
            updatedAt=<watermark minus 60 seconds>,
            fields=["id","title","updatedAt","createdAt","completedAt","startedAt","dueDate",
                    "archivedAt","status","statusType","priority","labels","assignee","createdBy",
                    "team","url","gitBranchName","projectMilestone","parentId","estimate"])
```

**Census pass** (when `census_due`): the same call **without** `updatedAt`, plus the slim roster
`list_issues(project=<id>, includeArchived=true, limit=250, fields=["id","archivedAt"])`
passed as `roster`.

Details on `includeArchived`, the 60-second skew and pagination: `references/sync-algorithm.md`.

### 3. Fetch plan

Call `plan` again, now with the real `issues`. You get `verdicts` and `fetch`. Only for
identifiers in `fetch` do you pull details:

```
get_issue(id="ENG-42", includeRelations=true)
list_comments(issueId="ENG-42", limit=250, orderBy="createdAt")
```

If `len(fetch)` exceeds `--max-fetch`, state the cost and ask.

### 4. Apply

```bash
python3 "$SC" apply < payload.json
```

Payload fields: `opts`, `project` (from `get_project`, only when `need_project_detail`,
otherwise the probe fields), `issues` (all rows from step 2), `details`, `comments`, and
optionally `roster`, `missing_reasons`, `watermark_new`.

**For long descriptions use `details_dir` / `comments_dir` instead of `details` / `comments`.**
Write one `<IDENT>.json` file per ticket containing the **raw MCP result verbatim**, and pass
only the directory paths. The script reads them and produces byte-identical output. Copy the
description text **unchanged** — do not shorten, reformat, or translate it.

The script runs prettier itself via `prettier --stdin-filepath`. **Do not call prettier
separately**, and never with `--parser markdown`: the `*.md` override in `.prettierrc.json` sets
`singleQuote: false`, and without it every frontmatter wikilink is rewritten to single quotes.

### 5. Classify disappeared tickets

For each identifier in `missing_candidates` (census only), one targeted `get_issue(id)`:

| Result | `missing_reasons` value |
| -- | -- |
| succeeds, `projectId` ≠ our project | `moved` (name the new project in the report) |
| error / not found | `deleted` |

Files are **never** deleted and **never** moved — only `sync missing since` and
`sync missing reason` are set.

### 6. Re-index

```bash
qmd update && qmd embed
```

Skip on `--dry-run`. If `qmd embed` runs long, start it in the background.

## Determinism axiom

**The managed region of every file is a pure function of the Linear payload.** The script
guarantees this; do not undermine it:

- A second run with no Linear changes writes **zero files**. That is the acceptance criterion:
  `git status` stays clean for the project folder.
- `created:` and `linear updated:` come from Linear. `updated:` and `synced:` are local
  timestamps that only advance when something actually changed.
- `sync hash:` covers the managed **body** only and is computed **after** prettier. It carries a
  version prefix so changing the formula cannot strand notes in permanent conflict.
- Filenames and content are NFC-normalized. Without that, any title containing `ö` or `—`
  produces a phantom rename on every run on APFS.

## Ticket references as wikilinks

Linear encodes ticket mentions in three shapes, all of which occur in real data: inline tags
(`<issue id="…" href="…">ENG-42</issue>`), plain markdown links
(`[ENG-42](https://linear.app/…/issue/ENG-42/…)`), and **bare identifier text** in comments
(`→ ENG-42:`).

- Identifier **in this project** → `[[ENG-42 Full Title|ENG-42]]`. **Piped, not bare:** Obsidian
  indexes `aliases:` for the quick switcher but does **not** resolve an already-written
  `[[ENG-42]]` through them. Inside a table cell the pipe is escaped as `\|`.
- Identifier **in another project** → `[ENG-9](https://linear.app/…)`.
- Unknown identifier → plain text. A wikilink that would dangle is **never** emitted.
- The prefix must be a known team key of the workspace. Without that gate `UTF-8`, `COVID-19`,
  `HTTP-2` and `ISO-8601` would all become links.
- Nothing is rewritten inside fenced code blocks or inline code.
- People and initiatives are linked only when a note for them actually exists in the vault.

Verified regexes and the full pipeline: `references/write-pipeline.md`.

## Protected section

The managed region lies between `<!-- linear:begin … -->` and `<!-- linear:end -->`.
**Everything from `<!-- linear:end -->` to end of file belongs to the user and is never
overwritten.** Markers are matched by their `linear:begin`/`linear:end` token, so the localized
wording can change without orphaning existing notes.

| Situation | Behaviour |
| -- | -- |
| New file | Markers plus the notes heading are created from the start |
| Marker missing in an existing note | **Do not write.** Report `MARKER_MISSING`, continue the batch. Even `--force` refuses — a guessed boundary can destroy prose |
| Prose **above** the marker | `sync hash` mismatch → `CONFLICT`. File untouched, reported |
| Ticket renamed | File is renamed, the old filename moves into `aliases` (max 4), notes survive |

## Renames

Renaming uses `os.rename` in the script, **not** `obsidian rename`: the latter needs the app
running and triggers `update-time-on-edit` on the file *and every linking file*, turning one
rename into N timestamp changes and N git diffs. Internal links point at filenames but are
regenerated on the next sync anyway, so churn costs nothing in a machine-generated mirror. The
previous filename is additionally kept as an alias so hand-written links elsewhere still resolve.

## Task lists

`- [ ]` becomes `- ☐` and `- [x]` becomes `- ☑` (disable with `--keep-checkboxes`). A mirrored
checkbox is a lie — ticking it does nothing and the next sync resets it — and dozens of
acceptance criteria would flood any vault-wide task query.

## Report

After the run, report concisely:

- Project, folder, mode (live/dry-run, delta/census), effective options
- Number of MCP calls (path B) or that the GraphQL path was used
- Counts: `created` / `updated` / `unchanged` / `renamed` / `skipped` / `missing` / `archived` /
  `failures`
- Per non-unchanged ticket: identifier, verdict, old → new on rename, one line of reasoning on
  conflict or failure
- Every `warnings` entry from the script
- Whether `qmd update` ran

Report `MARKER_MISSING`, `CONFLICT` and orphaned tickets loudly, with paths. A mirror that
silently accumulates problems is a mirror nobody trusts.

## Error handling

- One broken ticket never aborts the run — report it and continue.
- Ask only at batch level: failed precondition, ambiguous project, `--max-fetch`.
- Two files claiming the same `id` → error for that identifier only, name both paths.
- If `prettier` fails, the script aborts. Do not work around it.
- `synced through` advances only when the run had no failures; otherwise the affected
  identifiers land in `sync pending` and are refetched next time.

## Absolute prohibitions

- Never write to Linear. No `save_issue`, `save_comment`, `create_attachment` or any other
  mutating Linear tool — they are deliberately absent from `allowed-tools`.
- Never write, rename, or delete anything outside `01 Projects/Linear/<Project>/`.
- Never delete a note.
- Never change bytes at or after `<!-- linear:end -->`.
- Never run `git` in the vault.
- Never edit notes with `Edit`/`Write` — every write goes through the script.
- Never guess a marker boundary.
- Never use `prettier --parser markdown`.
- Never mirror attachments other than GitHub PR/commit links.
- Never print an API key, and never search the keychain for one.
