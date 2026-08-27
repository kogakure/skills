#!/usr/bin/env python3
"""Deterministic renderer/writer for the Linear -> Obsidian one-way mirror.

This script owns every decision that must be reproducible and every byte that touches
the vault. Data either arrives from the caller (MCP path) or is fetched here (GraphQL
path); the rendering and writing code is identical either way.

Modes:

  plan   stdin {opts, project_probe, issues[]}
         stdout {project_dir, verdicts, fetch[], census_due, need_project_detail, warnings}
  apply  stdin {opts, project, issues[], details{}, comments{}}  -> stdout {report}
  fetch  stdin {opts, project}  -> stdout an apply-ready payload, read from the Linear API
  sync   fetch + apply in one step  -> stdout {report}

`plan`/`apply` take data the caller fetched (e.g. via MCP tools); `fetch`/`sync` read the
Linear GraphQL API directly with an API key, so no issue text passes through the caller.

Rendered note content is localized via `opts.lang` (default "en"); operator messages and
report keys are always English. Timezone follows the system unless `opts.timezone` is set.

Stdlib only: no PyYAML, no requests. See references/ for the contracts.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

MIRROR_ROOT = ("01 Projects", "Linear")
CENSUS_TTL_DAYS = 7
NAME_MAX_BYTES = 200
HASH_VERSION = "v2-"
PR_RE = re.compile(r"^https://github\.com/[^/]+/[^/]+/(pull|commit)/", re.I)

# Markers are matched by REGEX on the stable `linear:begin` / `linear:end` token, never
# by their full text. The human-readable tail is localized and may be reworded, and an
# exact-string match would orphan every existing note the moment it changed.
BEGIN_RE = re.compile(r"<!--\s*linear:begin\b[^>]*-->")
END_RE = re.compile(r"<!--\s*linear:end\b[^>]*-->")
END = "<!-- linear:end -->"

# Rendered vault content is localized; operator-facing messages and report keys are
# always English. Default is English so a shared install produces English notes; set
# `opts.lang` (persisted as `sync lang` on the index note) to keep a vault consistent.
LABELS = {
    "en": {
        "begin": "<!-- linear:begin — generated; everything between the markers is "
                 "overwritten on every sync -->",
        "notes": "## Notes",
        "description": "## Description",
        "prs": "## Pull requests",
        "history": "## History",
        "hist_cols": ["Status", "From", "To", "Duration"],
        "comments": "## Comments",
        "tickets": "## Tickets",
        "ticket_cols": ["Ticket", "Title", "Priority", "Updated"],
        "milestone_col": "Milestone",
        "summary": "**{total} tickets** — {open} open, {done} closed",
        "empty": "_(empty)_",
        "unknown": "Unknown",
        "inline": "inline comment",
        "resolved": "resolved {date}",
        "on_behalf": "for",
        "orphan": "> [!NOTE] Reply to a deleted comment",
        "groups": {"triage": "Triage", "started": "In progress", "unstarted": "Todo",
                   "backlog": "Backlog", "completed": "Done",
                   "canceled": "Canceled"},
        "dur": {"lt_min": "< 1 min", "min": "{n} min", "hour": "{n} h",
                "day": "1 day", "days": "{n} days"},
        "fallback": {"comment": "Comment", "document": "Document",
                     "initiative": "Initiative", "milestone": "Milestone",
                     "team": "Team", "cycle": "Cycle", "issue": "Issue",
                     "project": "Project", "user": ""},
        "image": "Image",
    },
    "de": {
        "begin": "<!-- linear:begin — automatisch erzeugt, alles zwischen den Markern "
                 "wird bei jeder Synchronisation überschrieben -->",
        "notes": "## Notizen",
        "description": "## Beschreibung",
        "prs": "## Pull-Requests",
        "history": "## Verlauf",
        "hist_cols": ["Status", "Von", "Bis", "Dauer"],
        "comments": "## Kommentare",
        "tickets": "## Tickets",
        "ticket_cols": ["Ticket", "Titel", "Priorität", "Aktualisiert"],
        "milestone_col": "Meilenstein",
        "summary": "**{total} Tickets** — {open} offen, {done} abgeschlossen",
        "empty": "_(leer)_",
        "unknown": "Unbekannt",
        "inline": "Inline-Kommentar",
        "resolved": "erledigt {date}",
        "on_behalf": "für",
        "orphan": "> [!NOTE] Antwort auf einen gelöschten Kommentar",
        "groups": {"triage": "Triage", "started": "In Arbeit", "unstarted": "Geplant",
                   "backlog": "Backlog", "completed": "Fertig",
                   "canceled": "Abgebrochen"},
        "dur": {"lt_min": "< 1 Min.", "min": "{n} Min.", "hour": "{n} Std.",
                "day": "1 Tag", "days": "{n} Tage"},
        "fallback": {"comment": "Kommentar", "document": "Dokument",
                     "initiative": "Initiative", "milestone": "Meilenstein",
                     "team": "Team", "cycle": "Cycle", "issue": "Ticket",
                     "project": "Projekt", "user": ""},
        "image": "Bild",
    },
}
GROUP_ORDER = ["triage", "started", "unstarted", "backlog", "completed", "canceled"]

L = LABELS["en"]
TZ = datetime.now().astimezone().tzinfo    # system local zone unless overridden


def configure(opts: dict) -> None:
    """Apply per-run output language and timezone. Called once, before rendering."""
    global L, TZ
    L = LABELS.get(str(opts.get("lang") or "en").lower(), LABELS["en"])
    tz = opts.get("timezone")
    if tz:
        try:
            TZ = ZoneInfo(str(tz))
        except Exception:                                   # noqa: BLE001
            die(f"Unknown timezone: {tz!r}")


# --------------------------------------------------------------------------- #
# paths & containment
# --------------------------------------------------------------------------- #

def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def vault_root() -> Path:
    p = Path.cwd()
    for probe in ("00 Maps of Content", "04 Permanent", ".prettierrc.json"):
        if not (p / probe).exists():
            die(f"NOT AT VAULT ROOT: '{probe}' missing in {p}")
    return p


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    json.dump({"error": msg}, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.exit(1)


UNSAFE = str.maketrans({c: "-" for c in ':/\\|#^[]*?"<>'})


def sanitize_component(name: str) -> str:
    """Filesystem- and Obsidian-safe single path component (no extension)."""
    s = nfc(name).translate(UNSAFE)
    s = "".join(ch for ch in s if ch.isprintable())
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.strip(" .-")


def ticket_filename(identifier: str, title: str) -> str:
    """'<ID> <Title>.md', truncated on a word boundary to fit NAME_MAX_BYTES."""
    t = sanitize_component(title)
    base = f"{identifier} {t}".strip() if t else identifier
    while len((base + ".md").encode()) > NAME_MAX_BYTES:
        cut = base.rfind(" ")
        base = base[:cut] if cut > len(identifier) else base[:-1]
        base = base.rstrip(" .-")
    return base + ".md"


def project_dir(vault: Path, project_name: str) -> Path:
    comp = sanitize_component(project_name)
    if not comp or comp in (".", ".."):
        die(f"Project name yields no valid folder name: {project_name!r}")
    d = vault.joinpath(*MIRROR_ROOT, comp)
    if d.parent != vault.joinpath(*MIRROR_ROOT):
        die(f"Project folder escapes the mirror root: {d}")
    return d


def assert_inside(base: Path, target: Path) -> None:
    b = base.resolve(strict=False)
    t = target.resolve(strict=False)
    if not (t == b or b in t.parents):
        die(f"REFUSED: {t} lies outside {b}")


# --------------------------------------------------------------------------- #
# time
# --------------------------------------------------------------------------- #

def _parse(iso: str | None) -> datetime | None:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        return None


def dt_min(iso: str | None) -> str:
    d = _parse(iso)
    return d.astimezone(TZ).strftime("%Y-%m-%dT%H:%M") if d else ""


def dt_disp(iso: str | None) -> str:
    d = _parse(iso)
    return d.astimezone(TZ).strftime("%Y-%m-%d %H:%M") if d else ""


def d_only(iso: str | None) -> str:
    if not iso:
        return ""
    s = str(iso)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s
    d = _parse(s)
    return d.astimezone(TZ).strftime("%Y-%m-%d") if d else ""


def now_min() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%dT%H:%M")


def duration(a: str | None, b: str | None) -> str:
    da, db = _parse(a), _parse(b)
    if not da or not db:
        return "–"
    secs = int((db - da).total_seconds())
    d = L["dur"]
    if secs < 60:
        return d["lt_min"]
    if secs < 3600:
        return d["min"].format(n=secs // 60)
    if secs < 86400:
        return d["hour"].format(n=secs // 3600)
    days = secs // 86400
    return d["day"] if days == 1 else d["days"].format(n=days)


# --------------------------------------------------------------------------- #
# YAML emit / parse (restricted to this vault's shape)
# --------------------------------------------------------------------------- #

_NEEDS_Q = re.compile(r"^(-|\?|:|,|\[|\]|\{|\}|#|&|\*|!|\||>|'|\"|%|@|`)|^\s|\s$|: | #")
_SCALARISH = re.compile(
    r"^(true|false|yes|no|on|off|null|~|-?\d+(\.\d+)?|\d{4}-\d{2}-\d{2}.*)$", re.I)
# Date-like values are written BARE, including full-precision ISO-8601.
#
# Quoting them looks safer but is actively wrong here: Obsidian's own frontmatter
# serializer rewrites `linear updated: "…171Z"` to the unquoted form the moment the
# file is touched in the app. Emitting quotes therefore creates a permanent
# flip-flop — we write quoted, Obsidian unquotes, every sync sees a change. Bare is
# Obsidian's canonical form, so bare is a fixed point.
_VAULT_DATE = re.compile(
    r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?$")


def y_scalar(value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = nfc(str(value)).replace("\n", " ").strip()
    if not s:
        return ""
    if _VAULT_DATE.match(s):
        return s
    if s.startswith("[[") or _NEEDS_Q.search(s) or _SCALARISH.match(s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def y_emit(key: str, value) -> list[str]:
    """One frontmatter entry. Empty -> bare 'key:'. Lists -> two-space block."""
    if isinstance(value, (list, tuple)):
        items = [y_scalar(v) for v in value]
        items = [i for i in items if i]
        if not items:
            return [f"{key}:"]
        return [f"{key}:"] + [f"  - {i}" for i in items]
    s = y_scalar(value)
    return [f"{key}: {s}" if s else f"{key}:"]


FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.S)


def parse_fm(text: str) -> dict:
    """Read the known-shape frontmatter. Preserves order; keeps bare keys as ''."""
    m = FM_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    key = None
    for line in m.group(1).split("\n"):
        if re.match(r"^\s+-\s", line):
            if key is not None:
                v = line.strip()[1:].strip()
                if not isinstance(out.get(key), list):
                    out[key] = []
                out[key].append(_unquote(v))
            continue
        km = re.match(r"^([^:\s#][^:]*):\s*(.*?)\s*$", line)
        if km:
            key = km.group(1)
            raw = km.group(2)
            out[key] = _unquote(raw) if raw else ""
    return out


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        inner = v[1:-1]
        return inner.replace('\\"', '"').replace("\\\\", "\\") if v[0] == '"' else inner
    return v


def as_bool(v, default: bool = True) -> bool:
    """Coerce a frontmatter value back to a real bool.

    The parser returns strings, so a stored `true` comes back as "true". Feeding that
    straight into the emitter yields `"true"` (quoted, because it looks scalar-ish),
    which differs from `true` and makes the file change on every other run.
    """
    if isinstance(v, bool):
        return v
    s = str(v).strip().strip('"').lower()
    if s in ("true", "yes", "on", "1"):
        return True
    if s in ("false", "no", "off", "0"):
        return False
    return default


def as_list(v) -> list[str]:
    if isinstance(v, list):
        return [x for x in v if x]
    return [v] if v else []


def union(existing, *additions) -> list[str]:
    """Order-stable union: additions first (guaranteed present), then user extras."""
    out: list[str] = []
    for group in (list(additions), as_list(existing)):
        for item in group:
            if isinstance(item, (list, tuple)):
                seq = item
            else:
                seq = [item]
            for v in seq:
                if v and v not in out:
                    out.append(v)
    return out


# --------------------------------------------------------------------------- #
# note structure: frontmatter | managed | protected
# --------------------------------------------------------------------------- #

@dataclass
class Split:
    fm_text: str
    pre: str            # between frontmatter and BEGIN (must be blank)
    managed: str        # between the markers
    protected: str      # from END to EOF, verbatim (marker line included)
    has_markers: bool
    marker_count: int


def split_note(text: str) -> Split:
    m = FM_RE.match(text)
    fm_text, body = (m.group(1), text[m.end():]) if m else ("", text)
    begins = list(BEGIN_RE.finditer(body))
    ends = list(END_RE.finditer(body))
    if not begins or not ends or ends[-1].start() < begins[0].end():
        return Split(fm_text, "", body, "", False, len(begins))
    b, e = begins[0], ends[-1]          # first begin, last end: widens, never narrows
    return Split(
        fm_text=fm_text,
        pre=body[:b.start()],
        managed=body[b.end():e.start()],
        protected=body[e.start():],
        has_markers=True,
        marker_count=len(begins),
    )


def compose(fm_lines: list[str], managed: str, protected: str) -> str:
    body = f"{L['begin']}\n{managed.strip()}\n\n{protected.strip()}\n"
    return "---\n" + "\n".join(fm_lines) + "\n---\n\n" + body


def managed_hash(managed: str) -> str:
    """Fingerprint of the machine-managed BODY only — deliberately not the frontmatter.

    Hashing the frontmatter as well would catch hand-edited fields, but in this vault
    Obsidian edits frontmatter routinely and legitimately: `update-time-on-edit`
    rewrites `updated:`, and Obsidian's YAML serializer normalizes quoting and list
    style whenever a note is opened. Including it produced a false CONFLICT on every
    ticket. Frontmatter is regenerated from Linear on every run anyway, so its
    ownership is already unambiguous; the body is the part worth protecting.
    """
    return HASH_VERSION + hashlib.sha256(managed.strip().encode()).hexdigest()


def hash_comparable(stored: str) -> bool:
    """Only a hash written by THIS formula carries a conflict signal.

    Versioning matters: changing what the hash covers would otherwise strand every
    existing note in permanent CONFLICT, because an old digest can never match the
    new formula. An unrecognised prefix means "no reliable signal" — re-render
    instead of blocking.
    """
    return str(stored or "").startswith(HASH_VERSION)


# --------------------------------------------------------------------------- #
# markdown rendering pipeline
# --------------------------------------------------------------------------- #

FENCE_RE = re.compile(
    r"(?ms)^(?P<i>[ ]{0,3})(?P<f>`{3,}|~{3,})[^\n]*\n.*?(?:^(?P=i)(?P=f)[^\n]*$|\Z)")
INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
LINK_RE = re.compile(
    r"\[\[[^\]\n]*\]\]|!?\[[^\]\n]*\]\([^)\s]*\)|<https?://[^>\s]+>|https?://\S+")
TAG_RE = re.compile(
    r"<(?P<n>[a-zA-Z][\w-]*)(?P<a>\s[^>]*?)?>(?P<t>.*?)</(?P=n)>", re.S)
VOID_RE = re.compile(r"<(?P<n>[a-zA-Z][\w-]*)(?P<a>\s[^>]*?)?/>")
ATTR_RE = re.compile(r'(?P<k>[\w-]+)\s*=\s*"(?P<v>[^"]*)"')
HEADING_RE = re.compile(r"(?m)^(?P<q>(?:[ ]{0,3}>[ ]?)*)(?P<h>#{1,6})(?P<rest>\s)")
LEAK_RE = re.compile(r"([(\[{])\*\*(?P<in>[^*]*?(?:\[\[|\]\()[^*]*?)\*\*([)\]}])")
UPLOAD_IMG_RE = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\((?P<url>https://uploads\.linear\.app/[^)\s]*)\)")
TASK_RE = re.compile(r"(?m)^(?P<p>\s*[-*+]\s+)\[(?P<c>[ xX])\]\s")
PASSTHROUGH_HTML = frozenset(
    "br sub sup kbd mark u img a details summary code strong em b i del s".split())


def _mask(text: str, pattern: re.Pattern, tag: str) -> tuple[str, list[str]]:
    store: list[str] = []

    def keep(m: re.Match) -> str:
        store.append(m.group(0))
        return f"\x00{tag}{len(store) - 1}\x00"

    return pattern.sub(keep, text), store


def _unmask(text: str, tag: str, store: list[str]) -> str:
    if not store:
        return text
    return re.sub(rf"\x00{tag}(\d+)\x00", lambda m: store[int(m.group(1))], text)


@dataclass
class Ctx:
    index: dict           # identifier -> {"title","url"}
    hrefs: dict           # identifier -> href (harvested, incl. foreign projects)
    team_keys: frozenset
    vault_titles: dict    # lowercased title/alias -> canonical
    project_name: str
    project_uuid: str
    self_id: str = ""
    keep_checkboxes: bool = False


def link_or_text(name: str, ctx: Ctx) -> str:
    n = nfc((name or "").strip())
    if not n:
        return ""
    canon = ctx.vault_titles.get(n.lower())
    return f"[[{canon}]]" if canon else n


def ident_key(ident: str) -> tuple[str, int]:
    m = re.fullmatch(r"([A-Za-z]+)-(\d+)", ident or "")
    return (m.group(1), int(m.group(2))) if m else (ident or "", 0)


def resolve_ident(ident: str, ctx: Ctx, table: bool = False) -> str:
    """Ticket reference -> a link that actually resolves.

    Piped, not bare. Obsidian indexes `aliases:` for the quick switcher but does
    NOT resolve a bare `[[ENG-42]]` through them — verified against a live vault's
    metadataCache, where `getFirstLinkpathDest` returned null and every identifier sat
    in `unresolvedLinks` despite the alias being present. Linking by filename with the
    identifier as display text is the form that resolves.

    Rename churn, the usual argument against piped links, costs nothing here: every
    body carrying these links is regenerated from Linear on the next sync.
    """
    if ident == ctx.self_id:
        return ident
    entry = ctx.index.get(ident)
    if entry is not None:
        stem = entry.get("stem")
        if stem and stem != ident:
            # Inside a table cell the pipe must be escaped or it splits the column.
            return f"[[{stem}\\|{ident}]]" if table else f"[[{stem}|{ident}]]"
        return f"[[{ident}]]"
    href = ctx.hrefs.get(ident)
    return f"[{ident}]({href})" if href else ident


IDENT_RE = re.compile(
    r"(?<![0-9A-Za-z_\-/])([A-Z][A-Z0-9]{1,9})-([0-9]{1,6})(?![0-9A-Za-z_\-])")


def rewrite_bare(text: str, ctx: Ctx) -> str:
    def sub(m: re.Match) -> str:
        if m.group(1) not in ctx.team_keys:
            return m.group(0)          # UTF-8, COVID-19, HTTP-2, ISO-8601 ...
        return resolve_ident(m.group(0), ctx)

    return IDENT_RE.sub(sub, text)


def rewrite_tags(text: str, ctx: Ctx, depth: int = 0) -> str:
    if depth > 4:
        return text

    def one(m: re.Match) -> str:
        name = m.group("n").lower()
        attrs = {a.group("k").lower(): html.unescape(a.group("v"))
                 for a in ATTR_RE.finditer(m.group("a") or "")}
        inner = rewrite_tags(m.group("t") or "", ctx, depth + 1).strip()
        href = attrs.get("href", "")
        if name in PASSTHROUGH_HTML:
            return m.group(0)
        if name == "issue":
            ident = inner if IDENT_RE.fullmatch(inner) else ""
            if not ident and href:
                hm = re.search(r"/issue/([A-Z][A-Z0-9]{1,9}-\d+)", href)
                ident = hm.group(1) if hm else ""
            if ident:
                if ident not in ctx.index and href:
                    ctx.hrefs.setdefault(ident, href)
                return resolve_ident(ident, ctx)
            return f"[{inner}]({href})" if href and inner else inner
        if name == "project":
            if attrs.get("id") and attrs["id"] == ctx.project_uuid:
                return f"[[{ctx.project_name}]]"
            return f"[{inner}]({href})" if href and inner else inner
        if name == "user":
            return link_or_text(inner, ctx)
        label = inner or L["fallback"].get(name, "")
        if href and label:
            return f"[{label}]({href})"
        return label

    return TAG_RE.sub(one, text)


ISSUE_MDLINK_RE = re.compile(
    r"\[([^\]\n]*)\]\(https://linear\.app/[^/)\s]+/issue/"
    r"(?P<id>[A-Z][A-Z0-9]{1,9}-\d+)[^)\s]*\)")


def rewrite_issue_mdlinks(text: str, ctx: Ctx) -> str:
    """Turn an explicit Linear issue markdown link into a wikilink when the ticket
    is part of this mirror.

    Needed because the two fetch paths encode the same mention differently: MCP
    returns an `<issue …>` tag, GraphQL returns a plain `[ENG-42](https://…)` link.
    Without this, the same reference resolves locally on one path and points back at
    the web on the other. Links to tickets outside the mirror are left untouched —
    there is nothing local to point at.
    """
    def sub(m: re.Match) -> str:
        ident = m.group("id")
        if ident == ctx.self_id or ident not in ctx.index:
            return m.group(0)
        label = (m.group(1) or "").strip()
        stem = (ctx.index[ident] or {}).get("stem")
        if not stem:
            return m.group(0)
        return f"[[{stem}|{label or ident}]]"

    return ISSUE_MDLINK_RE.sub(sub, text)


def strip_stray_html(text: str) -> str:
    def kill(m: re.Match) -> str:
        return m.group(0) if m.group(1).lower() in PASSTHROUGH_HTML else ""

    text = re.sub(r"</?([a-zA-Z][\w-]*)(?:\s[^>]*?)?/?>", kill, text)
    return text


def tidy_emphasis(text: str) -> str:
    return LEAK_RE.sub(lambda m: f"{m.group(1)}{m.group('in')}{m.group(3)}", text)


def downgrade_tasks(text: str, keep: bool) -> str:
    if keep:
        return text
    return TASK_RE.sub(
        lambda m: f"{m.group('p')}{'☑' if m.group('c').lower() == 'x' else '☐'} ", text)


def demote_headings(text: str, min_level: int) -> str:
    levels = [len(m.group("h")) for m in HEADING_RE.finditer(text)]
    if not levels:
        return text
    off = max(0, min_level - min(levels))
    if not off:
        return text
    return HEADING_RE.sub(
        lambda m: m.group("q") + "#" * min(6, len(m.group("h")) + off) + m.group("rest"),
        text)


def fix_uploads(text: str) -> str:
    def sub(m: re.Match) -> str:
        alt = m.group("alt").strip()
        lbl = L["image"]
        return f"[{lbl}: {alt}]({m.group('url')})" if alt else f"[{lbl}]({m.group('url')})"

    return UPLOAD_IMG_RE.sub(sub, text)


def render_markdown(src: str, ctx: Ctx, min_heading: int) -> str:
    """Linear markdown -> vault markdown. Step order is load-bearing."""
    if not src:
        return ""
    t = nfc(src).replace("\r\n", "\n").replace("\r", "\n")
    t = "\n".join(ln.rstrip() for ln in t.split("\n"))
    t, code = _mask(t, FENCE_RE, "C")
    t, spans = _mask(t, INLINE_CODE_RE, "S")
    t = rewrite_tags(t, ctx)
    t = rewrite_issue_mdlinks(t, ctx)   # before masking, while the links are still text
    t, links = _mask(t, LINK_RE, "L")
    t = rewrite_bare(t, ctx)
    t = _unmask(t, "L", links)
    t = tidy_emphasis(t)
    t = fix_uploads(t)
    t = downgrade_tasks(t, ctx.keep_checkboxes)
    t = demote_headings(t, min_heading)
    t = strip_stray_html(t)
    t = _unmask(t, "S", spans)
    t = _unmask(t, "C", code)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def harvest_refs(blobs: list[str]) -> dict[str, str]:
    """identifier -> href, from every <issue ... href=...>IDENT</issue> in the payload."""
    out: dict[str, str] = {}
    for blob in blobs:
        if not blob:
            continue
        for m in TAG_RE.finditer(blob):
            if m.group("n").lower() != "issue":
                continue
            attrs = {a.group("k").lower(): html.unescape(a.group("v"))
                     for a in ATTR_RE.finditer(m.group("a") or "")}
            href = attrs.get("href", "")
            label = (m.group("t") or "").strip()
            ident = label if IDENT_RE.fullmatch(label) else ""
            if not ident and href:
                hm = re.search(r"/issue/([A-Z][A-Z0-9]{1,9}-\d+)", href)
                ident = hm.group(1) if hm else ""
            if ident and href:
                out.setdefault(ident, href)
    return out


def build_vault_titles(vault: Path, exclude: Path) -> dict[str, str]:
    """lowercased stem/alias -> canonical link text, for the whole vault."""
    titles: dict[str, str] = {}
    ex = exclude.resolve(strict=False)
    for p in vault.rglob("*.md"):
        rp = p.resolve(strict=False)
        if ex == rp or ex in rp.parents:
            continue
        parts = p.relative_to(vault).parts
        if parts and parts[0] in (".obsidian", ".git", ".agents", ".claude"):
            continue
        stem = nfc(p.stem)
        titles.setdefault(stem.lower(), stem)
        for alias in _aliases_of(p):
            titles.setdefault(alias.lower(), alias)
    return titles


def _aliases_of(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            first = fh.readline()
            if first.strip() != "---":
                return []
            out: list[str] = []
            in_alias = False
            for _ in range(200):
                line = fh.readline()
                if not line or line.strip() == "---":
                    break
                if re.match(r"^aliases:", line):
                    in_alias = True
                    rest = line.split(":", 1)[1].strip()
                    if rest.startswith("["):
                        out += [_unquote(x) for x in rest.strip("[]").split(",")]
                        in_alias = False
                    continue
                if in_alias:
                    if re.match(r"^\s+-\s", line):
                        out.append(_unquote(line.strip()[1:].strip()))
                        continue
                    in_alias = False
            return [nfc(a) for a in out if a]
    except OSError:
        return []


# --------------------------------------------------------------------------- #
# prettier
# --------------------------------------------------------------------------- #

def prettier(text: str, target: Path) -> str:
    """Pure str->str. The real .md path is required so the *.md override applies
    (top-level singleQuote:true would otherwise mangle frontmatter wikilinks)."""
    try:
        r = subprocess.run(
            ["prettier", "--stdin-filepath", str(target)],
            input=text, capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return text if os.environ.get("LINEAR_SYNC_NO_PRETTIER") else die(
            f"prettier fehlgeschlagen: {exc}")
    if r.returncode != 0:
        die(f"prettier failed for {target.name}: {r.stderr.strip()[:400]}")
    return r.stdout


# --------------------------------------------------------------------------- #
# local scan / write / rename
# --------------------------------------------------------------------------- #

@dataclass
class Local:
    path: Path
    fm: dict
    split: Split


def scan_local(pdir: Path) -> tuple[dict[str, Local], list[str], list[Local]]:
    """-> ({identifier: Local}, duplicate-identifier warnings, index-note candidates)"""
    found: dict[str, list[Local]] = {}
    others: list[Local] = []
    if not pdir.is_dir():
        return {}, [], []
    for p in sorted(pdir.glob("*.md")):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = parse_fm(text)
        loc = Local(p, fm, split_note(text))
        ident = str(fm.get("id") or "").strip()
        if fm.get("type") == "Linear Ticket" and ident:
            found.setdefault(ident, []).append(loc)
        else:
            others.append(loc)
    dupes = [f"{i}: " + ", ".join(l.path.name for l in v)
             for i, v in found.items() if len(v) > 1]
    return {i: v[0] for i, v in found.items() if len(v) == 1}, dupes, others


SYNC_HASH_LINE = re.compile(r"(?m)^sync hash:.*$")
WORD_RE = re.compile(r"\w+", re.UNICODE)


def word_bag(s: str) -> dict[str, int]:
    bag: dict[str, int] = {}
    for w in WORD_RE.findall(s):
        bag[w] = bag.get(w, 0) + 1
    return bag


def protected_intact(old: str, new: str) -> bool:
    """True when nothing was clipped from the user's region.

    Byte equality is the wrong test: prettier legitimately reformats whitespace,
    list markers and emphasis inside the protected region. A word multiset is
    invariant under all of those, but any dropped sentence shows up immediately.
    """
    a, b = word_bag(old), word_bag(new)
    return all(b.get(w, 0) >= n for w, n in a.items())


def finalize(candidate: str, target: Path) -> str:
    """Normalize through prettier, then stamp `sync hash:` computed FROM the
    normalized text. The hash must be taken after normalization, otherwise
    prettier's table repadding makes every file look hand-edited on re-read.
    Stamping a 64-hex scalar into an existing key is itself prettier-stable."""
    norm = prettier(candidate, target)
    sp = split_note(norm)
    digest = managed_hash(sp.managed)
    return SYNC_HASH_LINE.sub(f"sync hash: {digest}", norm, count=1)


def write_if_changed(path: Path, final: str, pdir: Path, dry: bool) -> str:
    """`final` must already be prettier-normalized (see finalize())."""
    assert_inside(pdir, path)
    on_disk = path.read_bytes() if path.exists() else None
    raw = final.encode()
    if raw == on_disk:
        return "unchanged"
    if dry:
        return "would-write"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name("." + path.name + ".tmp")
    tmp.write_bytes(raw)
    os.replace(tmp, path)
    return "created" if on_disk is None else "updated"


def safe_rename(old: Path, new: Path, pdir: Path, dry: bool) -> str:
    assert_inside(pdir, old)
    assert_inside(pdir, new)
    if nfc(old.name) == nfc(new.name):
        return "noop"
    if new.exists():
        return "collision"
    if dry:
        return "would-rename"
    if old.name.lower() == new.name.lower():
        mid = old.with_name("." + old.name + ".case")
        os.rename(old, mid)
        os.rename(mid, new)
    else:
        os.rename(old, new)
    return "renamed"


# --------------------------------------------------------------------------- #
# body rendering
# --------------------------------------------------------------------------- #

def cell(s: str) -> str:
    return re.sub(r"\s+", " ", nfc(str(s or "")).replace("|", r"\|")).strip()


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    if not rows:
        return []
    out = ["| " + " | ".join(headers) + " |",
           "| " + " | ".join("---" for _ in headers) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out


def render_history(hist: list[dict]) -> list[str]:
    if not hist:
        return []
    rows = []
    ordered = sorted(enumerate(hist),
                     key=lambda t: (str(t[1].get("startedAt") or ""), t[0]))
    for _, h in ordered:
        st = (h.get("state") or {}).get("name") or ""
        a, b = h.get("startedAt"), h.get("endedAt")
        rows.append([cell(st), dt_disp(a) or "–", dt_disp(b) or "–", duration(a, b)])
    return [L["history"], ""] + md_table(L["hist_cols"], rows)


def render_prs(attachments: list[dict]) -> list[str]:
    prs = [a for a in (attachments or []) if PR_RE.match(str(a.get("url") or ""))]
    if not prs:
        return []
    prs.sort(key=lambda a: str(a.get("url")))
    out = [L["prs"], ""]
    for a in prs:
        title = cell(a.get("title") or a.get("url"))
        out.append(f"- [{title}]({a['url']})")
    return out


def render_comments(comments: list[dict], ctx: Ctx) -> list[str]:
    if not comments:
        return []
    by_parent: dict[str, list[dict]] = {}
    for c in comments:
        by_parent.setdefault(str(c.get("parentId") or ""), []).append(c)
    for v in by_parent.values():
        v.sort(key=lambda c: (str(c.get("createdAt") or ""), str(c.get("id") or "")))
    known = {str(c.get("id")) for c in comments}
    out = ["---", "", L["comments"]]

    def emit(c: dict, reply: bool) -> None:
        author = ((c.get("author") or {}).get("name") or L["unknown"])
        on_behalf = (c.get("onBehalfOf") or {}).get("name")
        who = f"{author} {L['on_behalf']} {on_behalf}" if on_behalf else author
        bits = [cell(who), dt_disp(c.get("createdAt"))]
        if c.get("quotedText"):
            bits.append(L["inline"])
        if c.get("resolvedAt"):
            bits.append(L["resolved"].format(date=d_only(c["resolvedAt"])))
        prefix = "### ↳ " if reply else "### "
        out.extend(["", prefix + " · ".join(b for b in bits if b), ""])
        orphan = c.get("parentId") and str(c["parentId"]) not in known
        if orphan:
            out.extend([L["orphan"], ""])
        if c.get("quotedText"):
            q = render_markdown(str(c["quotedText"]), ctx, 6).replace("\n", " ")
            out.extend([f"> „{q.strip()}“", ""])
        body = render_markdown(str(c.get("body") or ""), ctx, 4)
        out.append(body if body else L["empty"])
        for child in by_parent.get(str(c.get("id")), []):
            emit(child, True)

    roots = list(by_parent.get("", []))
    for pid, group in by_parent.items():
        if pid and pid not in known:
            roots.extend(group)
    roots.sort(key=lambda c: (str(c.get("createdAt") or ""), str(c.get("id") or "")))
    for c in roots:
        emit(c, False)
    return out


def render_ticket_managed(row: dict, detail: dict, comments: list[dict],
                          ctx: Ctx) -> str:
    parts: list[str] = []
    desc = render_markdown(str(detail.get("description") or ""), ctx, 3)
    if desc:
        parts += [L["description"], "", desc]
    prs = render_prs(detail.get("attachments") or [])
    if prs:
        parts += ([""] if parts else []) + prs
    hist = render_history(detail.get("stateHistory") or [])
    if hist:
        parts += ([""] if parts else []) + hist
    com = render_comments(comments, ctx)
    if com:
        parts += ([""] if parts else []) + com
    return "\n".join(parts).strip()


def render_index_managed(project: dict, rows: list[dict], ctx: Ctx) -> str:
    parts: list[str] = []
    desc = render_markdown(str(project.get("description") or ""), ctx, 3)
    if desc:
        parts += [L["description"], "", desc, ""]
    has_ms = any(r.get("projectMilestone") for r in rows)
    total = len(rows)
    done = sum(1 for r in rows if r.get("statusType") in ("completed", "canceled"))
    parts += [L["tickets"], "",
              L["summary"].format(total=total, open=total - done, done=done)]
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(str(r.get("statusType") or "backlog"), []).append(r)
    tc = L["ticket_cols"]
    headers = tc[:2] + ([L["milestone_col"]] if has_ms else []) + tc[2:]
    for key in GROUP_ORDER:
        label = L["groups"][key]
        grp = groups.get(key)
        if not grp:
            continue
        grp = _nest(grp)
        trows = []
        for r, depth in grp:
            ident = str(r.get("id"))
            title = ("↳ " * depth) + cell(r.get("title"))
            line = [resolve_ident(ident, ctx, table=True), title]
            if has_ms:
                line.append(cell(r.get("projectMilestone") or "–"))
            line += [cell((r.get("priority") or {}).get("name") or "–"),
                     d_only(r.get("updatedAt"))]
            trows.append(line)
        parts += ["", f"### {label} ({len(grp)})", ""] + md_table(headers, trows)
    for key in sorted(set(groups) - set(GROUP_ORDER)):
        grp = _nest(groups[key])
        trows = [[resolve_ident(str(r.get("id")), ctx, table=True),
                  ("↳ " * d) + cell(r.get("title"))] +
                 ([cell(r.get("projectMilestone") or "–")] if has_ms else []) +
                 [cell((r.get("priority") or {}).get("name") or "–"),
                  d_only(r.get("updatedAt"))] for r, d in grp]
        parts += ["", f"### {key} ({len(grp)})", ""] + md_table(headers, trows)
    return "\n".join(parts).strip()


def _nest(rows: list[dict]) -> list[tuple[dict, int]]:
    """Sort by identifier, pulling sub-issues directly under their parent."""
    rows = sorted(rows, key=lambda r: ident_key(str(r.get("id"))))
    by_id = {str(r.get("id")): r for r in rows}
    children: dict[str, list[dict]] = {}
    roots = []
    for r in rows:
        pid = str(r.get("parentId") or "")
        if pid and pid in by_id:
            children.setdefault(pid, []).append(r)
        else:
            roots.append(r)
    out: list[tuple[dict, int]] = []

    def walk(r: dict, depth: int) -> None:
        out.append((r, depth))
        for c in sorted(children.get(str(r.get("id")), []),
                        key=lambda x: ident_key(str(x.get("id")))):
            walk(c, depth + 1)

    for r in roots:
        walk(r, 0)
    return out


# --------------------------------------------------------------------------- #
# frontmatter assembly
# --------------------------------------------------------------------------- #

def ticket_fm(row: dict, detail: dict, comments: list[dict], ctx: Ctx,
              prev: dict, prev_stem: str | None, new_stem: str,
              updated: str) -> list[str]:
    rel = detail.get("relations") or {}

    def links(key: str) -> list[str]:
        return [resolve_ident(str(x.get("id")), ctx)
                for x in sorted(rel.get(key) or [],
                                key=lambda x: ident_key(str(x.get("id"))))]

    dup = rel.get("duplicateOf")
    ident = str(row.get("id"))
    hist_aliases = [a for a in as_list(prev.get("aliases")) if a != ident]
    if prev_stem and prev_stem != new_stem and prev_stem not in hist_aliases:
        hist_aliases.insert(0, prev_stem)
    latest = max((str(c.get("updatedAt") or c.get("createdAt") or "")
                  for c in comments), default="")
    parent = str(detail.get("parentId") or row.get("parentId") or "")
    fields: list[tuple[str, object]] = [
        ("type", "Linear Ticket"),
        ("status", row.get("status") or detail.get("status")),
        ("status type", row.get("statusType") or detail.get("statusType")),
        ("priority", ((row.get("priority") or {}).get("name") or "")),
        ("created", dt_min(row.get("createdAt")) or prev.get("created")),
        ("updated", updated),
        ("aliases", union(None, [ident], hist_aliases[:4])),
        ("tags", union(prev.get("tags"), ["Linear", "Ticket", "🔒"])),
        ("urls", union(prev.get("urls"), [row.get("url") or ""])),
        ("related", as_list(prev.get("related"))),
        ("project", f"[[{ctx.project_name}]]"),
        ("id", ident),
        ("title", row.get("title") or ""),
        ("team", row.get("team") or ""),
        ("assignee", link_or_text(str(row.get("assignee") or ""), ctx)),
        ("creator", link_or_text(str(row.get("createdBy") or ""), ctx)),
        ("labels", sorted([str(x) for x in (row.get("labels") or [])],
                          key=str.casefold)),
        ("estimate", row.get("estimate")),
        ("milestone", row.get("projectMilestone") or detail.get("projectMilestone")),
        ("parent", resolve_ident(parent, ctx) if parent else ""),
        ("blocks", links("blocks")),
        ("blocked by", links("blockedBy")),
        ("related to", links("relatedTo")),
        ("duplicate of", resolve_ident(str(dup.get("id")), ctx)
         if isinstance(dup, dict) and dup.get("id") else ""),
        ("started", d_only(row.get("startedAt"))),
        ("completed", d_only(row.get("completedAt"))),
        ("canceled", d_only(row.get("canceledAt"))),
        ("archived", d_only(row.get("archivedAt"))),
        ("due", d_only(row.get("dueDate"))),
        ("branch", row.get("gitBranchName") or ""),
        ("linear updated", str(row.get("updatedAt") or "")),
        ("comments count", len(comments) if comments else ""),
        ("comments latest", latest),
        ("sync hash", ""),
        # Reaching here means Linear returned this ticket, so it is not missing.
        # Clearing unconditionally is what makes a reappearance self-healing.
        ("sync missing since", ""),
        ("sync missing reason", ""),
    ]
    lines: list[str] = []
    for k, v in fields:
        lines += y_emit(k, v)
    return lines


def index_fm(project: dict, rows: list[dict], ctx: Ctx, prev: dict,
             state: dict, updated: str) -> list[str]:
    teams = [str(t.get("name")) for t in (project.get("teams") or []) if t.get("name")]
    inits = [str(i.get("name")) for i in (project.get("initiatives") or [])
             if i.get("name")]
    total = len(rows)
    done = sum(1 for r in rows if r.get("statusType") in ("completed", "canceled"))
    fields: list[tuple[str, object]] = [
        ("type", "Linear Project"),
        ("status", (project.get("status") or {}).get("name") or ""),
        ("status type", (project.get("status") or {}).get("type") or ""),
        ("priority", (project.get("priority") or {}).get("name") or ""),
        ("created", dt_min(project.get("createdAt")) or prev.get("created")),
        ("updated", updated),
        ("aliases", as_list(prev.get("aliases"))),
        ("tags", union(prev.get("tags"), ["Linear", "Projekt", "🔒"])),
        ("urls", union(prev.get("urls"), [project.get("url") or ""])),
        ("related", as_list(prev.get("related"))),
        ("title", project.get("name") or ""),
        ("summary", project.get("summary") or ""),
        ("initiative", inits[0] if len(inits) == 1 else inits),
        ("team", teams[0] if len(teams) == 1 else teams),
        ("lead", link_or_text(str((project.get("lead") or {}).get("name") or ""), ctx)),
        ("members", [link_or_text(str(m.get("name") or ""), ctx)
                     for m in (project.get("members") or [])]),
        ("labels", sorted([str(x) for x in (project.get("labels") or [])],
                          key=str.casefold)),
        ("milestones", [str(m.get("name")) for m in (project.get("milestones") or [])
                        if m.get("name")]),
        ("startdate", d_only(project.get("startDate"))),
        ("enddate", d_only(project.get("targetDate"))),
        ("completed", d_only(project.get("completedAt"))),
        ("canceled", d_only(project.get("canceledAt"))),
        ("tickets total", total),
        ("tickets open", total - done),
        ("tickets done", done),
        ("uuid", project.get("id") or ""),
        ("linear updated", str(project.get("updatedAt") or "")),
        ("synced", state.get("synced") or now_min()),
        ("synced through", state.get("synced_through") or ""),
        ("synced census", state.get("synced_census") or ""),
        ("sync comments", state.get("sync_comments")),
        ("sync lang", state.get("sync_lang")),
        ("sync pending", state.get("sync_pending") or []),
    ]
    lines: list[str] = []
    for k, v in fields:
        lines += y_emit(k, v)
    return lines


# --------------------------------------------------------------------------- #
# modes
# --------------------------------------------------------------------------- #

def _load() -> dict:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        die(f"Invalid JSON on stdin: {exc}")
    _expand_dirs(payload)
    return payload


def _expand_dirs(payload: dict) -> None:
    """Allow `details_dir` / `comments_dir` instead of inline dicts.

    Each `<IDENT>.json` in the directory holds one raw MCP result verbatim, so the
    agent writes one small file per ticket instead of assembling a single huge
    payload — far less transcription risk on long descriptions.
    """
    for key, target in (("details_dir", "details"), ("comments_dir", "comments")):
        d = payload.pop(key, None)
        if not d:
            continue
        base = Path(str(d)).expanduser()
        if not base.is_dir():
            die(f"{key} is not a directory: {base}")
        merged = dict(payload.get(target) or {})
        for f in sorted(base.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                die(f"{f.name} not readable: {exc}")
            ident = f.stem
            if target == "comments":
                merged[ident] = data.get("comments", data) if isinstance(data, dict) \
                    else data
            else:
                merged[ident] = data
        payload[target] = merged


def _index_path(pdir: Path, project_name: str) -> Path:
    return pdir / (sanitize_component(project_name) + ".md")


def _plugin_warnings(vault: Path) -> list[str]:
    """`update-time-on-edit` fires on externally written files too, so if it does
    not ignore the mirror folder it overwrites our deterministic `updated:` with
    wall-clock and dirties every note the next time Obsidian touches it."""
    plug = vault / ".obsidian/plugins/update-time-on-edit/data.json"
    if not plug.exists():
        return []
    try:
        ig = json.loads(plug.read_text(encoding="utf-8")).get(
            "ignoreGlobalFolder", []) or []
    except (OSError, json.JSONDecodeError):
        return []
    if any("01 Projects/Linear" in str(x) for x in ig):
        return []
    return ["'update-time-on-edit' does not ignore the mirror folder — add it to that "
            "plugin's excluded folders once, or it will overwrite the deterministic "
            "`updated:` timestamps."]


def mode_plan(payload: dict) -> dict:
    opts = payload.get("opts") or {}
    configure(opts)
    probe = payload.get("project_probe") or {}
    rows = payload.get("issues") or []
    vault = vault_root()
    name = str(probe.get("name") or "")
    if not name:
        die("project_probe.name is missing")
    pdir = project_dir(vault, name)
    local, dupes, others = scan_local(pdir)
    ipath = _index_path(pdir, name)
    istate = parse_fm(ipath.read_text(encoding="utf-8")) if ipath.exists() else {}

    warnings: list[str] = [f"Duplicate id in several files — {d}" for d in dupes]
    warnings += _plugin_warnings(vault)

    census_due = bool(opts.get("census") or opts.get("force") or not ipath.exists())
    if not census_due:
        last = _parse((istate.get("synced census") or "") + ":00+02:00") \
            if istate.get("synced census") else None
        if not last:
            census_due = True
        else:
            census_due = (datetime.now(TZ) - last).days >= CENSUS_TTL_DAYS

    only = {s.strip() for s in (opts.get("only") or []) if s.strip()}
    pending = set(as_list(istate.get("sync pending")))
    verdicts: dict[str, str] = {}
    fetch: list[str] = []
    for r in rows:
        ident = str(r.get("id") or "")
        if not ident:
            continue
        if only and ident not in only:
            continue
        loc = local.get(ident)
        if loc is None:
            v = "NEW"
        elif not loc.split.has_markers:
            v = "MARKER_MISSING"
        elif hash_comparable(loc.fm.get("sync hash")) and \
                loc.fm["sync hash"] != managed_hash(loc.split.managed):
            v = "CONFLICT"
        elif opts.get("force") or ident in pending:
            v = "CHANGED"
        elif str(loc.fm.get("linear updated") or "") != str(r.get("updatedAt") or ""):
            v = "CHANGED"
        else:
            v = "UNCHANGED"
        verdicts[ident] = v
        if v in ("NEW", "CHANGED"):
            fetch.append(ident)
    fetch.sort(key=ident_key)

    missing = sorted(set(local) - {str(r.get("id")) for r in rows}, key=ident_key)
    return {
        "vault": str(vault),
        "project_dir": str(pdir),
        "index_path": str(ipath),
        "project_name": name,
        "index_exists": ipath.exists(),
        "local_count": len(local),
        "need_project_detail": bool(
            opts.get("force") or not ipath.exists()
            or str(istate.get("linear updated") or "") != str(probe.get("updatedAt") or "")),
        "census_due": census_due,
        "watermark": _watermark(istate, local),
        "verdicts": verdicts,
        "fetch": fetch,
        "missing_candidates": missing if census_due else [],
        "extra_files": [o.path.name for o in others if o.path != ipath],
        "warnings": warnings,
    }


def _watermark(istate: dict, local: dict[str, Local]) -> str:
    cached = str(istate.get("synced through") or "")
    derived = max((str(l.fm.get("linear updated") or "") for l in local.values()),
                  default="")
    cands = [c for c in (cached, derived) if c]
    return min(cands) if len(cands) == 2 else (cands[0] if cands else "")


def mode_apply(payload: dict) -> dict:
    opts = payload.get("opts") or {}
    configure(opts)
    dry = bool(opts.get("dry_run"))
    project = payload.get("project") or {}
    rows = payload.get("issues") or []
    details = payload.get("details") or {}
    comments = payload.get("comments") or {}
    roster = payload.get("roster")
    vault = vault_root()
    name = str(project.get("name") or "")
    if not name:
        die("project.name is missing")
    pdir = project_dir(vault, name)
    ipath = _index_path(pdir, name)

    local, dupes, others = scan_local(pdir)
    istate_fm = parse_fm(ipath.read_text(encoding="utf-8")) if ipath.exists() else {}
    # A bare re-run must not switch a vault's language: the value stored on the index
    # note wins over the "en" default whenever the caller did not ask for one.
    if not opts.get("lang") and istate_fm.get("sync lang"):
        configure(dict(opts, lang=istate_fm["sync lang"]))

    by_id = {str(r.get("id")): r for r in rows if r.get("id")}
    blobs = [str(project.get("description") or "")]
    for d in details.values():
        blobs.append(str(d.get("description") or ""))
    for lst in comments.values():
        for c in lst or []:
            blobs.append(str(c.get("body") or ""))
            blobs.append(str(c.get("quotedText") or ""))
    hrefs = harvest_refs(blobs)

    team_keys = {ident_key(i)[0] for i in by_id} | {ident_key(i)[0] for i in local}
    team_keys |= {str(t.get("key")) for t in (project.get("teams") or []) if t.get("key")}
    team_keys = frozenset(k for k in team_keys if k)

    ctx = Ctx(
        # `stem` is the link target: the sanitized filename without .md. Taken from
        # the incoming title when Linear returned the ticket, otherwise from the file
        # already on disk, so references to unchanged tickets still resolve.
        index={i: {"title": r.get("title"), "url": r.get("url"),
                   "stem": ticket_filename(i, str(r.get("title") or ""))
                   .removesuffix(".md")}
               for i, r in by_id.items()}
              | {i: {"stem": l.path.stem} for i, l in local.items()
                 if i not in by_id},
        hrefs=hrefs,
        team_keys=team_keys,
        vault_titles=build_vault_titles(vault, pdir),
        project_name=sanitize_component(name),
        project_uuid=str(project.get("id") or ""),
        keep_checkboxes=bool(opts.get("keep_checkboxes")),
    )

    report: dict = {
        "project": name, "project_dir": str(pdir), "dry_run": dry,
        "created": [], "updated": [], "unchanged": [], "renamed": [],
        "skipped": [], "missing": [], "archived": [], "failures": [],
        "warnings": [f"Duplicate id in several files — {d}" for d in dupes]
                    + _plugin_warnings(vault),
        "extra_files": [o.path.name for o in others if o.path != ipath],
    }

    if not dry:
        pdir.mkdir(parents=True, exist_ok=True)

    for ident in sorted(details, key=ident_key):
        row = by_id.get(ident)
        detail = details[ident] or {}
        if not row:
            row = dict(detail)
            row.setdefault("id", ident)
        try:
            _write_ticket(ident, row, detail, comments.get(ident) or [], ctx,
                          local.get(ident), pdir, dry, report)
        except SystemExit:
            raise
        except Exception as exc:                       # noqa: BLE001
            report["failures"].append({"id": ident, "reason": repr(exc)[:300]})

    # census bookkeeping: mark absent, clear reappeared
    if roster is not None:
        present = {str(x.get("id")) for x in roster if x.get("id")}
        reasons = payload.get("missing_reasons") or {}
        today = datetime.now(TZ).strftime("%Y-%m-%d")
        for ident, loc in sorted(local.items(), key=lambda kv: ident_key(kv[0])):
            if ident in present or ident in details:
                continue
            if loc.fm.get("sync missing since"):
                report["missing"].append({"id": ident, "state": "already flagged",
                                          "path": loc.path.name})
                continue
            res = _patch_fm(loc, {"sync missing since": today,
                                  "sync missing reason": str(reasons.get(ident)
                                                             or "unknown")},
                            pdir, dry)
            report["missing"].append({"id": ident, "state": "newly flagged",
                                      "path": loc.path.name, "write": res})
        for ident in sorted(present & set(local), key=ident_key):
            loc = local[ident]
            if not loc.fm.get("sync missing since") or ident in details:
                continue
            _patch_fm(loc, {"sync missing since": "", "sync missing reason": ""},
                      pdir, dry)
            report["warnings"].append(f"{ident} reappeared — missing marker cleared.")

    for ident, loc in local.items():
        if loc.fm.get("archived"):
            report["archived"].append(ident)

    all_rows = list(by_id.values())
    if not all_rows:
        all_rows = [dict(l.fm, id=i, statusType=l.fm.get("status type"),
                         title=l.fm.get("title"), updatedAt=l.fm.get("linear updated"),
                         priority={"name": l.fm.get("priority")})
                    for i, l in sorted(local.items(), key=lambda kv: ident_key(kv[0]))]

    state = {
        "synced": now_min(),
        "synced_through": payload.get("watermark_new") or
                          istate_fm.get("synced through") or "",
        "synced_census": now_min() if roster is not None
                         else (istate_fm.get("synced census") or ""),
        "sync_comments": as_bool(opts.get("comments",
                                  istate_fm.get("sync comments", True))),
        "sync_lang": opts.get("lang") or istate_fm.get("sync lang") or "en",
        "sync_pending": [f["id"] for f in report["failures"]],
    }
    if report["failures"]:
        state["synced_through"] = istate_fm.get("synced through") or ""

    try:
        _write_index(project, all_rows, ctx, istate_fm, state, ipath, pdir, dry, report)
    except SystemExit:
        raise
    except Exception as exc:                           # noqa: BLE001
        report["failures"].append({"id": "<index>", "reason": repr(exc)[:300]})

    report["counts"] = {k: len(report[k]) for k in
                        ("created", "updated", "unchanged", "renamed", "skipped",
                         "missing", "archived", "failures")}
    return report


def _patch_fm(loc: "Local", changes: dict[str, str], pdir: Path, dry: bool) -> str:
    """Set a few frontmatter keys on an existing note, touching nothing else.

    Used for census bookkeeping, where there is no Linear payload to re-render
    from: the ticket is gone. Keys must already exist in the file.
    """
    text = loc.path.read_text(encoding="utf-8")
    out = text
    for key, val in changes.items():
        line = f"{key}: {y_scalar(val)}".rstrip() if val else f"{key}:"
        pat = re.compile(rf"(?m)^{re.escape(key)}:.*$")
        if pat.search(out):
            out = pat.sub(lambda _m, l=line: l, out, count=1)
    if out == text:
        return "unchanged"
    return write_if_changed(loc.path, finalize(out, loc.path), pdir, dry)


def _write_ticket(ident, row, detail, cmts, ctx, loc, pdir, dry, report) -> None:
    prev_fm = loc.fm if loc else {}
    prev_split = loc.split if loc else None
    if loc and not prev_split.has_markers:
        report["skipped"].append({"id": ident, "reason": "MARKER_MISSING",
                                  "path": loc.path.name})
        return
    if loc and hash_comparable(prev_fm.get("sync hash")):
        actual = managed_hash(prev_split.managed)
        if actual != prev_fm["sync hash"] and not report.get("_allow_conflict"):
            report["skipped"].append({"id": ident, "reason": "CONFLICT",
                                      "path": loc.path.name})
            return

    ctx.self_id = ident
    new_stem = ticket_filename(ident, str(row.get("title") or "")).removesuffix(".md")
    prev_stem = loc.path.stem if loc else None
    managed = render_ticket_managed(row, detail, cmts, ctx)
    protected = prev_split.protected if (prev_split and prev_split.protected) \
        else f"{END}\n\n{L['notes']}\n"

    def build(updated: str, target: Path) -> str:
        fm = ticket_fm(row, detail, cmts, ctx, prev_fm, prev_stem, new_stem, updated)
        return finalize(compose(fm, managed, protected), target)

    target = pdir / (new_stem + ".md")
    if loc and nfc(loc.path.name) != nfc(target.name):
        res = safe_rename(loc.path, target, pdir, dry)
        if res == "collision":
            report["failures"].append(
                {"id": ident, "reason": f"Target name already exists: {target.name}"})
            return
        report["renamed"].append({"id": ident, "from": loc.path.name,
                                  "to": target.name, "result": res})
        if dry:
            target = loc.path

    # Pass 1: keep the stored `updated:` so an otherwise-identical file stays byte-equal.
    keep = str(prev_fm.get("updated") or "") or now_min()
    candidate = build(keep, target)
    verify = split_note(candidate)
    if prev_split and prev_split.protected and \
            not protected_intact(prev_split.protected, verify.protected):
        report["failures"].append({"id": ident, "reason": "PROTECTED_REGION_ALTERED"})
        return
    existed = target.exists()
    if existed and write_if_changed(target, candidate, pdir, True) == "unchanged":
        report["unchanged"].append(ident)
        return
    # Pass 2: something really changed, so the vault edit time may advance.
    candidate = build(now_min(), target)
    res = write_if_changed(target, candidate, pdir, dry)
    if res == "unchanged":
        report["unchanged"].append(ident)
    elif res == "would-write":
        report["updated" if existed else "created"].append(target.name + " (dry-run)")
    else:
        report["created" if res == "created" else "updated"].append(target.name)


def _write_index(project, rows, ctx, prev_fm, state, ipath, pdir, dry, report) -> None:
    prev = split_note(ipath.read_text(encoding="utf-8")) if ipath.exists() else None
    if prev and not prev.has_markers and ipath.exists():
        report["skipped"].append({"id": "<index>", "reason": "MARKER_MISSING",
                                  "path": ipath.name})
        return
    ctx.self_id = ""
    managed = render_index_managed(project, rows, ctx)
    protected = prev.protected if (prev and prev.protected) \
        else f"{END}\n\n{L['notes']}\n"
    existed = ipath.exists()

    def build(updated: str, synced: str, census: str) -> str:
        st = dict(state, synced=synced, synced_census=census)
        return finalize(compose(index_fm(project, rows, ctx, prev_fm, st, updated),
                                managed, protected), ipath)

    # Pass 1: reuse every stored wall-clock value, so a no-op run stays byte-equal.
    if existed:
        candidate = build(str(prev_fm.get("updated") or ""),
                          str(prev_fm.get("synced") or ""),
                          str(prev_fm.get("synced census") or ""))
        if write_if_changed(ipath, candidate, pdir, True) == "unchanged":
            report["unchanged"].append(ipath.name)
            return
    # Pass 2: real change -> advance the wall-clock fields.
    stamp = now_min()
    candidate = build(stamp, stamp,
                      stamp if state.get("synced_census") else "")
    res = write_if_changed(ipath, candidate, pdir, dry)
    if res == "unchanged":
        report["unchanged"].append(ipath.name)
    elif res == "would-write":
        report["updated" if existed else "created"].append(ipath.name + " (dry-run)")
    else:
        report["created" if res == "created" else "updated"].append(ipath.name)


# --------------------------------------------------------------------------- #
# optional GraphQL fetch (no content passes through the agent's context)
# --------------------------------------------------------------------------- #

GQL_URL = "https://api.linear.app/graphql"

Q_PROJECTS = """
query { projects(first: 250) { nodes {
  id name slugId url updatedAt } } }
"""

Q_PROJECT = """
query($id: String!) { project(id: $id) {
  id name description content url createdAt updatedAt startedAt completedAt
  canceledAt startDate targetDate priority priorityLabel
  status { id name type }
  lead { name }
  labels(first: 50) { nodes { name } }
  teams(first: 20) { nodes { id name key } }
  members(first: 50) { nodes { name } }
  projectMilestones(first: 50) { nodes { id name targetDate } }
  initiatives(first: 20) { nodes { id name } }
} }
"""

Q_ISSUES = """
query($pid: ID!, $after: String) {
  issues(first: 100, after: $after,
         filter: { project: { id: { eq: $pid } } },
         includeArchived: true) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id identifier title description url branchName estimate
      createdAt updatedAt archivedAt completedAt startedAt canceledAt dueDate
      priority priorityLabel
      state { name type }
      labels(first: 50) { nodes { name } }
      creator { name }
      assignee { name }
      team { name key }
      project { id }
      projectMilestone { name }
      parent { identifier }
      relations(first: 50) { nodes {
        type
        relatedIssue { identifier title }
      } }
      inverseRelations(first: 50) { nodes {
        type
        issue { identifier title }
      } }
      attachments(first: 50) { nodes { id title subtitle url } }
      comments(first: 100) { nodes {
        id body createdAt updatedAt resolvedAt
        parent { id }
        user { name }
      } }
      history(first: 100) { nodes {
        createdAt
        fromState { name type }
        toState { name type }
      } }
    }
  }
}
"""


def _api_key() -> str:
    key = os.environ.get("LINEAR_API_KEY", "").strip()
    if key:
        return key
    for var in ("LINEAR_API_KEY_FILE",):
        p = os.environ.get(var)
        if p and Path(p).expanduser().is_file():
            return Path(p).expanduser().read_text(encoding="utf-8").strip()
    default = Path.home() / ".config/linear/api-key"
    if default.is_file():
        return default.read_text(encoding="utf-8").strip()
    die("No Linear API key found. Set LINEAR_API_KEY or LINEAR_API_KEY_FILE, or create "
        "~/.config/linear/api-key. The key is never logged.")


def gql(query: str, variables: dict, key: str) -> dict:
    import urllib.error
    import urllib.request
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        GQL_URL, data=body,
        headers={"Content-Type": "application/json", "Authorization": key,
                 "User-Agent": "obsidian-linear-sync/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read()[:300].decode("utf-8", "replace")
        die(f"Linear API HTTP {exc.code}: {detail}")     # never echo the key
    except OSError as exc:
        die(f"Linear API unreachable: {exc}")
    if data.get("errors"):
        msgs = "; ".join(str(e.get("message")) for e in data["errors"])[:400]
        die(f"Linear API error: {msgs}")
    return data.get("data") or {}


def _names(container) -> list[str]:
    return [str(n.get("name")) for n in ((container or {}).get("nodes") or [])
            if n.get("name")]


def _state_history(hist_nodes: list[dict], created_at: str) -> list[dict]:
    """Rebuild the MCP-shaped stateHistory from history transitions.

    Each transition's `toState` starts then and ends at the next transition. The
    very first `fromState` is the state the issue was created in.
    """
    trans = sorted(
        (h for h in (hist_nodes or []) if h.get("toState")),
        key=lambda h: str(h.get("createdAt") or ""))
    out: list[dict] = []
    if trans and trans[0].get("fromState"):
        out.append({"state": trans[0]["fromState"], "startedAt": created_at,
                    "endedAt": trans[0].get("createdAt")})
    for i, h in enumerate(trans):
        nxt = trans[i + 1].get("createdAt") if i + 1 < len(trans) else None
        out.append({"state": h["toState"], "startedAt": h.get("createdAt"),
                    "endedAt": nxt})
    return out


def _relations(node: dict, rel_nodes: list[dict], inv_nodes: list[dict]) -> dict:
    """GraphQL relations/inverseRelations -> the MCP relations shape."""
    rel: dict = {"blocks": [], "blockedBy": [], "relatedTo": [], "duplicateOf": None}

    def entry(other: dict) -> dict:
        return {"id": other.get("identifier"), "title": other.get("title")}

    for r in rel_nodes or []:
        other, kind = r.get("relatedIssue") or {}, str(r.get("type") or "")
        if not other:
            continue
        if kind == "blocks":
            rel["blocks"].append(entry(other))
        elif kind == "duplicate":
            rel["duplicateOf"] = entry(other)
        else:
            rel["relatedTo"].append(entry(other))
    for r in inv_nodes or []:
        other, kind = r.get("issue") or {}, str(r.get("type") or "")
        if not other:
            continue
        if kind == "blocks":
            rel["blockedBy"].append(entry(other))
        elif kind != "duplicate":
            rel["relatedTo"].append(entry(other))
    return rel


def mode_fetch(payload: dict) -> dict:
    """Build an apply-ready payload straight from the Linear API."""
    opts = payload.get("opts") or {}
    configure(opts)
    target = str(payload.get("project") or payload.get("query") or "").strip()
    if not target:
        die("No project given (payload.project)")
    key = _api_key()

    slug = target.rstrip("/").split("/")[-1] if "linear.app" in target else target
    nodes = (gql(Q_PROJECTS, {}, key).get("projects") or {}).get("nodes") or []
    lower = slug.lower()
    hits = [n for n in nodes if lower in (str(n.get("slugId") or "").lower(),
                                          str(n.get("name") or "").lower())]
    if not hits:
        hits = [n for n in nodes if lower in str(n.get("url") or "").lower()
                or lower in str(n.get("name") or "").lower()]
    if len(hits) != 1:
        die(f"Project is ambiguous ({len(hits)} matches) for {slug!r}: "
            + ", ".join(str(n.get("name")) for n in hits[:8]))
    pid = hits[0]["id"]

    proj = gql(Q_PROJECT, {"id": pid}, key).get("project") or {}
    project = {
        "id": proj.get("id"),
        "name": proj.get("name"),
        # GraphQL swaps these relative to the MCP shape: `description` is the short
        # summary, `content` is the long markdown body.
        "summary": proj.get("description") or "",
        "description": proj.get("content") or "",
        "url": proj.get("url"),
        "createdAt": proj.get("createdAt"), "updatedAt": proj.get("updatedAt"),
        "startedAt": proj.get("startedAt"), "completedAt": proj.get("completedAt"),
        "canceledAt": proj.get("canceledAt"),
        "startDate": proj.get("startDate"), "targetDate": proj.get("targetDate"),
        "priority": {"value": proj.get("priority"),
                     "name": proj.get("priorityLabel") or ""},
        "status": proj.get("status") or {},
        "lead": proj.get("lead") or {},
        "labels": _names(proj.get("labels")),
        "teams": [{"id": t.get("id"), "name": t.get("name"), "key": t.get("key")}
                  for t in ((proj.get("teams") or {}).get("nodes") or [])],
        "members": [{"name": m.get("name")}
                    for m in ((proj.get("members") or {}).get("nodes") or [])],
        "milestones": [{"id": m.get("id"), "name": m.get("name")}
                       for m in ((proj.get("projectMilestones") or {}).get("nodes") or [])],
        "initiatives": [{"id": i.get("id"), "name": i.get("name")}
                        for i in ((proj.get("initiatives") or {}).get("nodes") or [])],
    }

    issues: list[dict] = []
    details: dict = {}
    comments: dict = {}
    after = None
    for _ in range(50):
        page = (gql(Q_ISSUES, {"pid": pid, "after": after}, key).get("issues") or {})
        for n in page.get("nodes") or []:
            ident = str(n.get("identifier"))
            row = {
                "id": ident, "title": n.get("title"),
                "url": n.get("url"), "gitBranchName": n.get("branchName"),
                "estimate": n.get("estimate"),
                "createdAt": n.get("createdAt"), "updatedAt": n.get("updatedAt"),
                "archivedAt": n.get("archivedAt"),
                "completedAt": n.get("completedAt"),
                "startedAt": n.get("startedAt"), "canceledAt": n.get("canceledAt"),
                "dueDate": n.get("dueDate"),
                "priority": {"value": n.get("priority"),
                             "name": n.get("priorityLabel") or ""},
                "status": (n.get("state") or {}).get("name"),
                "statusType": (n.get("state") or {}).get("type"),
                "labels": _names(n.get("labels")),
                "createdBy": (n.get("creator") or {}).get("name"),
                "assignee": (n.get("assignee") or {}).get("name"),
                "team": (n.get("team") or {}).get("name"),
                "projectMilestone": (n.get("projectMilestone") or {}).get("name"),
                "parentId": (n.get("parent") or {}).get("identifier"),
            }
            issues.append(row)
            details[ident] = dict(row, **{
                "description": n.get("description") or "",
                "attachments": (n.get("attachments") or {}).get("nodes") or [],
                "stateHistory": _state_history(
                    (n.get("history") or {}).get("nodes") or [],
                    str(n.get("createdAt") or "")),
                "relations": _relations(
                    n,
                    (n.get("relations") or {}).get("nodes") or [],
                    (n.get("inverseRelations") or {}).get("nodes") or []),
                "projectId": ((n.get("project") or {}).get("id")),
            })
            cs = []
            for c in ((n.get("comments") or {}).get("nodes") or []):
                cs.append({
                    "id": c.get("id"), "body": c.get("body") or "",
                    "createdAt": c.get("createdAt"), "updatedAt": c.get("updatedAt"),
                    "resolvedAt": c.get("resolvedAt"),
                    "parentId": (c.get("parent") or {}).get("id"),
                    "quotedText": None,
                    "author": {"name": (c.get("user") or {}).get("name")},
                    "onBehalfOf": None,
                })
            if cs:
                comments[ident] = cs
        if not (page.get("pageInfo") or {}).get("hasNextPage"):
            break
        after = (page.get("pageInfo") or {}).get("endCursor")
    else:
        die("Project too large: more than 50 pages of issues")

    return {
        "opts": opts, "project": project, "issues": issues,
        "details": details, "comments": comments,
        "roster": [{"id": r["id"], "archivedAt": r.get("archivedAt")} for r in issues],
        "watermark_new": max((str(r.get("updatedAt") or "") for r in issues),
                             default=""),
    }


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ("plan", "apply", "fetch", "sync"):
        die("Usage: linear_sync.py {plan|apply|fetch|sync} < payload.json")
    mode = sys.argv[1]
    payload = _load()
    if mode == "fetch":
        out = mode_fetch(payload)
    elif mode == "sync":
        # fetch + apply in one step: nothing but the report crosses the boundary
        out = mode_apply(mode_fetch(payload))
    else:
        out = mode_plan(payload) if mode == "plan" else mode_apply(payload)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
