# iA Presenter Syntax Reference

## File Format

iA Presenter opens standard `.md` (Markdown) files. Save as `presentation-name.md`.

---

## Slide Separator

Three dashes on their own line create a new slide:

```
---
```

Pressing Return twice in the editor also creates a slide break.

---

## Text Visibility Rules

iA Presenter uses a single file for both **speaker notes** (what you say) and
**slide content** (what the audience sees). Visibility is controlled by indentation.

| Element              | Written as            | Visible on slide                      |
| -------------------- | --------------------- | ------------------------------------- |
| Heading `#`–`######` | `# Title`             | Yes                                   |
| Indented paragraph   | `⇥ text` (tab prefix) | Yes                                   |
| Regular paragraph    | `text`                | No — speaker notes                    |
| Indented list        | `⇥ - item`            | Yes                                   |
| Regular list         | `- item`              | No — speaker notes                    |
| Indented blockquote  | `⇥ > quote`           | Yes                                   |
| Regular blockquote   | `> quote`             | No                                    |
| Code block           | ` ```lang `           | Yes                                   |
| Table                | `\| col \|`           | Yes                                   |
| Image/video          | `![](file)`           | Yes                                   |
| Comment              | `// text`             | No — author only (not even in export) |

**Rule of thumb:** If it's indented with a tab, it's on the slide. If it's not,
it's a speaker note.

---

## Headings

All six heading levels are supported. Heading level affects layout:

- `#` — Main title; triggers cover or title layout
- `##` — Section header; triggers section layout (good for chapter breaks)
- `###`–`######` — Subheadings within slide content

```markdown
# Main Title

## Section Break Title

### Subsection
```

---

## Kicker (small label above the title)

A tab-indented line immediately before an `#` heading becomes a small "kicker"
label above the title:

```markdown
    Keynote 2024

# The Next Big Thing
```

No `#` on the kicker — just tab + text.

---

## Text Formatting

```markdown
**bold text** **bold text**
_italic text_ _italic text_
~~strikethrough~~
==highlighted text==
text^superscript^ y^(a+b)^
text~subscript~ x~y,z~
```

---

## Lists

```markdown
⇥ - Unordered item (tab makes it appear on slide)
⇥ - Another item
⇥ - Nested item (tab + 4 spaces or another tab)

⇥ 1. Ordered item
⇥ 2. Second item

⇥ - [ ] Task item (unchecked)
⇥ - [x] Task item (checked)
```

---

## Blockquotes

```markdown
⇥ > "Quote text appears on slide"

⇥ — Attribution
```

---

## Horizontal Rule (within a slide, not a slide break)

```markdown
---
```

(Three asterisks; contrast with `---` which creates a new slide)

---

## Images

### Standard Markdown syntax

```markdown
![Alt text description](image-name.jpg)
![Company logo](logo.png "Optional title")
```

For filenames with spaces, use `%20`:

```markdown
![Hero shot](product%20hero.jpg)
```

### Content Blocks syntax (recommended for layout control)

Place the file path on its own line. Options follow on subsequent lines:

```markdown
/assets/image.jpg
```

```markdown
/assets/image.jpg
size: cover
align: center top
layer: background
filter: darken
opacity: 0.6
```

**Size options:**

- `size: cover` — fills the space, may clip
- `size: contain` — letterboxes to preserve aspect ratio

**Align options** (horizontal vertical):

- `align: center center` (default)
- `align: left top`
- `align: right bottom`
- etc. — any combination of left/center/right and top/center/bottom

Alternatively use separate `x:` and `y:` attributes (equivalent, both valid):

- `x: left` / `x: center` / `x: right`
- `y: top` / `y: center` / `y: bottom`

**Layer options:**

- `layer: content` — foreground (default)
- `layer: background` — beneath text and headings

**Filter options:**

- `filter: lighten`
- `filter: darken`
- `filter: grayscale`
- `filter: sepia`
- `filter: blur`

**Opacity:** `opacity: 0.5` (0.0–1.0)

**Title / placeholder label:** `title: "Placeholder"` — marks an image as a placeholder; visible as a label in the editor

**Custom CSS class:** `class: my-custom-class`

### Image with caption

Place an `####` heading next to an image:

```markdown
![Quarterly results](chart.png)

#### Revenue grew 40% YoY
```

### Placeholder images

While writing, use a placeholder rather than hunting for the perfect image.
Mark it with `title: "Placeholder"` so you remember to replace it:

```markdown
/Theme/image2.webp
title: "Placeholder"
```

`/Theme/` is a special path prefix that references images bundled with the
currently active theme. Replace with your real asset path before presenting.

### External URLs

```markdown
https://source.example.com/photo.jpg
x: left
y: top
```

### Unsplash (built-in integration)

Use the Media Manager in the Inspector to search and insert Unsplash photos.
Unsplash images are automatically credited.

---

## Videos

### Local video

```markdown
![](video.mp4)
```

Or with Content Blocks syntax:

```markdown
/assets/demo.mov
size: cover
```

**Supported formats:** `.m4v`, `.mp4`, `.mov`

### YouTube

Add YouTube videos via the Media Manager (Inspector tab). They appear as
`/assets/youtube-id` in the markdown.

**Note:** YouTube videos do not support filters or opacity.

### Video settings

Autoplay and controls visibility are configured in Settings → Presentation.

---

## Tables

Standard Markdown table syntax. Column alignment via colon position:

```markdown
| Column | Left | Center | Right |
| :----- | :--- | :----: | ----: |
| Row 1  | A    |   B    |     C |
| Row 2  | D    |   E    |     F |
```

Any table can be converted to a bar, line, or pie chart via the chart icon
in iA Presenter's contextual toolbar. You can also set the chart type inline
with `Chart:` immediately after the table:

```markdown
|         | Series 1 | Series 2 |
| :------ | :------- | :------- |
| Group A | 10       | 15       |
| Group B | 15       | 20       |
| Group C | 25       | 30       |
Chart: Bar
yLabel: Revenue (€)
```

**Chart types:** `Bar`, `Line`, `Pie`
**Axis labels:** `xLabel: label` / `yLabel: label`

### Importing data

CSV files can be imported: File → Import → CSV.

---

## Code

Inline code: `` `code` ``

Fenced code block with syntax highlighting:

````markdown
```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```
````

---

## Math (LaTeX)

Inline: `$E = mc^2$` or `\(E = mc^2\)`

Block: `$$\sum_{i=0}^{n} x_i$$` or `\[\sum_{i=0}^{n} x_i\]`

---

## Footnotes

Inline: `[^This is the footnote text]`

Reference style:

```markdown
Main text.[^1]

[^1]: Footnote definition.
```

---

## Links

```markdown
[Link text](https://example.com)
[Link with title](https://example.com "Title")
[Reference link][id]

[id]: https://example.com
```

---

## Comments (author-only, never exported)

```markdown
// This note is invisible to the audience and not exported.
// Use for reminders, staging notes, questions to self.
```

---

## Definition Lists

```markdown
Term
: Definition

Another term
: Another definition
```

---

## Layout Patterns

iA Presenter automatically selects from 18 layouts based on slide content.
These patterns reliably trigger specific layouts:

### Cover

```markdown
# Presentation Title

    Subtitle text or tagline
    Author Name · Event · Date
```

### Title + Image (split layout)

```markdown
# Key Point Headline

![](supporting-visual.jpg)
```

### Section Break

```markdown
## Part 3: What We Learned
```

### Side-by-side (two elements)

Separate two elements with a double blank line:

```markdown
# Comparison

![](option-a.jpg)

![](option-b.jpg)
```

Up to 3 elements side by side.

### Grid (4+ elements)

Four or more tab-indented items auto-arrange in a grid:

```markdown
# Four Pillars

    Speed

    Quality

    Trust

    Openness
```

### Two-column split (multiple headings, no separator)

Two `###` headings on the same slide (no `---` between them) trigger a
split/column layout:

```markdown
### Option A
    Pros: fast to implement, low cost.

### Option B
    Pros: more robust, scales better.
```

### Quote slide

```markdown
    > "The best presentations are conversations, not performances."

    — Nancy Duarte
```

### Full-bleed background image

```markdown
/assets/dramatic-photo.jpg
layer: background
size: cover
filter: darken

# Text Over the Image
```

---

## YAML Front Matter (optional)

iA Presenter does not require YAML front matter, but you can include it for
metadata that gets exported to PDF etc.:

```yaml
---
title: Presentation Title
author: Stefan Imhoff
date: 2024-01-15
---
```

---

## Aspect Ratios

Set in Settings → Presentation → Layout:

- `4:3` — Regular (classic projectors)
- `16:9` — Wide (most modern displays)
- `9:16` — Mobile (portrait, social)
- `4:5` — Portrait (social media)
- `1:1` — Square (Instagram)

---

## Import

Import existing Markdown or text files via File → Import → Markdown/Text.
iA Presenter splits on `#` headings: each H1 or H2 becomes a new slide.
Regular paragraphs become speaker notes.
