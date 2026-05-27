---
name: ia-presenter
description: >
  Creates high-quality, well-designed presentations for iA Presenter (Mac app).
  Generates complete Markdown files with proper iA Presenter syntax: slide
  structure, speaker notes separated from slide content, layout control through
  content organization, images, tables, charts, and theme recommendations.
  Use this skill whenever the user wants to create a presentation, build a deck,
  structure a talk, or create slides — even if they don't say "iA Presenter"
  explicitly but are working on a .md presentation file. Also trigger when the
  user pastes an outline, essay, or document and asks to "turn this into slides"
  or "make a presentation from this". This skill knows the full iA Presenter
  syntax and best practices, so always use it rather than writing generic markdown.
---

# iA Presenter Skill

iA Presenter is a Mac presentation app that uses Markdown files (`.md`). The
core philosophy: **write your story first, then let iA Presenter render it as
slides**. Speaker notes and slide content live in the same file but are
distinguished by indentation.

## Workflow

### Step 1 — Gather Requirements

Ask or infer before writing. What you need:

- **Topic and goal** — What is the presentation about? Inform, persuade, pitch, teach?
- **Audience** — Technical, executive, general public?
- **Duration** — How long? (~1.5–2 min/slide is typical)
- **Content** — Outline, draft, or just a topic?
- **Tone** — Formal, casual, technical?
- **Theme preference** — See theme guide in `references/themes.md`

If the user provides content, adapt it. If they give only a topic, generate the full narrative.

### Step 2 — Structure the Narrative Arc

Every presentation follows a shape:

1. **Cover** — Title, subtitle, presenter name
2. **Hook** — First slide surprises or provokes a question; never start with an agenda
3. **Setup** — Establish the problem, situation, or context
4. **Body** — 3–5 main points; each point gets 2–4 slides
5. **Resolution** — What the audience should now believe or understand
6. **Call to action** — Specific, concrete next step

Agenda slides are optional; only include for presentations over 20 slides.

### Step 3 — Write the Markdown

See the complete syntax reference in `references/syntax.md`. Core rules:

- Slides are separated by `---`
- **Headings always appear on the slide**
- **Regular paragraphs are speaker notes** (invisible to the audience)
- **Tab-indented paragraphs appear on the slide**

### Step 4 — Output

Deliver a complete, ready-to-use `.md` file. Add a brief header comment
with theme recommendation and estimated duration. Name the file clearly
(e.g., `product-launch.md`).

---

## Design Principles

Apply these — they make the difference between a mediocre and a great deck:

**One idea per slide.** If you find yourself writing "and also..." on a slide,
split it into two slides. Slides are cheap; clarity is not.

**Headlines carry the message.** Every slide title should be a complete
statement that makes sense on its own: "Revenue grew 40% YoY" beats "Revenue".
If the audience remembers only the titles, they should still understand your talk.

**Show, don't list.** Bullet lists are the enemy of attention. Prefer a single
strong image + headline, a quote, or a chart over a bulleted list of four
things. If you must list, put items on separate slides.

**Sparse slide content.** The audience reads at 250 wpm and you speak at 150 wpm.
If your slide has 50 words, they stop listening while they read. Put the detail
in speaker notes; put the anchor in the slide content.

**Vary the rhythm.** Alternate heavy text slides with full-image slides, quote
slides, and chart slides. A uniform presentation is a boring presentation.

**Section breaks signal transitions.** Use an `##` slide to give the audience
a breath and signal a new chapter.

**End with energy.** Close with a strong call to action or a memorable image.
Never end on "Questions?" — that's a dead stop.

---

## Quick Syntax Reference

### Slide separator

```
---
```

### Text visibility

```markdown
# This heading appears on the slide

This paragraph is speaker notes — not visible to the audience.
Write what you'll say aloud here.

    This indented paragraph appears on the slide.

    - This indented list appears on the slide
    - Item two
```

### Kicker (small text above the title)

```markdown
    Product Launch 2024

# The Future of Payments
```

(Tab before the kicker line — no `#`)

### Section header slide

```markdown
## Part 2: The Solution
```

H2 headings alone trigger the section layout.

### Image

```markdown
![A person using the app](demo.jpg)
```

With Content Blocks syntax (preferred for layout control):

```markdown
/assets/hero.jpg
size: cover
layer: background
```

### Side-by-side layout (two elements, double blank line between them)

```markdown
# Before vs. After

![](before.jpg)

![](after.jpg)
```

### Grid layout (four or more elements)

```markdown
# Four Core Values

    Speed

    Quality

    Trust

    Openness
```

### Quote slide

```markdown
    > "Move fast and break things was never about moving fast."

    — Sheryl Sandberg
```

### Table / Chart

```markdown
| Metric  |    Q3 |     Q4 |
| :------ | ----: | -----: |
| Revenue | $2.1M |  $2.9M |
| Users   | 8,400 | 12,200 |
```

Any table can become a bar, line, or pie chart inside iA Presenter.

### Speaker notes with private comment

```markdown
# Key Insight

Audience sees only the heading. This sentence is your spoken narrative.
Tell the story behind the data. Give the anecdote. Make the connection.

// Remind yourself to pause here for questions.
```

---

## Output Template

```markdown
// Recommended theme: [theme name] ([light|dark])
// Estimated duration: ~[X] minutes ([N] slides × ~[Y] min each)

# [Presentation Title]

    [Subtitle or tagline]
    [Presenter name] · [Date or event]

---

# [Hook slide — surprising statement, provocative question, or striking fact]

[Speaker note: Why does this matter? What problem does this introduce?]

---
```

Continue from there, following the narrative arc.

---

## Quality Checklist

Before delivering the output, verify each:

- Every slide has a heading (exception: full-bleed image slides)
- Speaker notes written for every slide — what exactly you'd say
- No slide has more visible text than the audience can absorb in 5 seconds
- `##` section break slides mark major transitions
- Opening slide uses a hook, not a list of topics
- Closing slide has a concrete call to action
- All `---` separators present between slides
- Theme recommendation included in header comment

---

## Reference Files

- `references/syntax.md` — Full iA Presenter syntax with all options
- `references/themes.md` — Theme guide with visual characteristics and best uses
