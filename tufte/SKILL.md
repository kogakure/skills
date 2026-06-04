---
name: tufte
description: >
  Apply Edward Tufte's information design principles to create, improve,
  or critique any chart, graph, infographic, dashboard, table, or data
  visualization. Use this skill whenever the user wants to design a new
  chart, graph, or visualization from data; asks how to show data more
  clearly; wants to review or critique an existing graphic, report,
  dashboard, or infographic; asks about chartjunk, data-ink ratio, lie
  factor, small multiples, sparklines, or visual integrity; is choosing
  between chart types; wants to make a visualization honest, dense, or
  clear; mentions "compared to what?"; or asks about visual storytelling
  with data. Do NOT wait for the user to say "Tufte" — intervene
  proactively any time data needs to be shown visually.
---

# Tufte: Information Design

The central tenet: **"Above all else, show the data."** — VDQI, p. 92

Every design decision flows from this. If a mark, color, grid line, or
label helps the viewer understand the data, it earns its place. If it
doesn't, it should be erased.

---

## Two Entry Workflows

Read the user's intent and enter the right workflow:

- **Design from scratch** — user has data and wants to make a graphic
- **Critique existing** — user has a graphic and wants it improved

Both workflows end at the same ship checklist in `references/checklists.md`.

---

## Workflow A: Design from Scratch

### Step 1 — Clarify the question

Before selecting any form, ask:

- **"Compared to what?"** Every graphic implies a comparison. Make it
  explicit. What baseline, alternative, or change over time matters?
- What is the single most important thing the viewer should see?
- Who is the audience, and what can they take action on?
- How many variables are in the data, and how many dimensions of
  variation matter?

If the user can't answer "compared to what?" in one sentence, the
data question isn't formed yet. Clarify before designing.

### Step 2 — Choose the form

Use this decision tree to pick the right chart type. When in doubt,
default to the simpler, more honest form.

| Goal                                          | Recommended form                        | Avoid                           |
| --------------------------------------------- | --------------------------------------- | ------------------------------- |
| Relationship between 2 continuous variables   | Scatterplot (range-frame axes)          | Pie chart                       |
| Change over time, one series                  | Line chart (no fill, labeled endpoints) | Bar chart with 3D               |
| Change over time, many series (compare shape) | Small multiples                         | Spaghetti overlay               |
| Change over time, very many series            | Sparkline table                         | Single overloaded chart         |
| Distribution, n < 50                          | Dot plot or strip plot                  | Histogram (too coarse)          |
| Distribution, n ≥ 50                          | Histogram or density curve              | 3D bar chart                    |
| Ranking / comparing magnitudes                | Horizontal sorted bar chart             | Pie chart, 3D bar               |
| Part-to-whole                                 | Sorted bar or dot plot showing shares   | Pie or donut                    |
| Geographic distribution                       | Map with proportional symbols or dots   | Choropleth (use only for rates) |
| Many variables, same subjects over time       | Parallel coordinates or slopegraph      | Radar chart                     |
| Exact values across categories                | Table                                   | Any chart when n < 20           |
| Compare many time-series simultaneously       | Image quilt / sparkline matrix          | —                               |

**When to use a table instead of a graph:**

- Readers need exact values (lookup task)
- Multiple heterogeneous quantities per row
- Single measurement per item
- n < 20 rows

**When to use small multiples:**
The instant you ask "how does this pattern change across conditions,
time periods, or categories?" — and you can't answer it in one panel
without overlapping lines or a legend — switch to small multiples.
Same design, same scale, same encoding across all panels. Differences
encode data, not format.

For deeper decision-tree rationale and Tufte exemplar per branch, see
`references/chart-decision-tree.md`.

### Step 3 — Encode honestly

Graphical integrity is not optional. A graphic that lies wastes the
viewer's time and destroys trust.

**Lie factor target: 0.95–1.05**

```
Lie Factor = (size of effect shown in graphic) / (size of effect in data)
```

Check:

- Physical size (area, length, height) of every mark must be
  proportional to the numerical quantity it represents.
- Baseline zero unless the data range makes a cut-in clearly labeled.
- Avoid perspective distortion — roads receding into distance, 3D
  depth cues on 2D data.
- For monetary time series: adjust for inflation before displaying.
  Nominal units in a multi-year chart almost always mislead.
- Number of visual dimensions must not exceed number of data
  dimensions. A 2D shape to encode a 1D quantity inflates by the
  square (area ∝ value²); a 3D icon inflates by the cube.

### Step 4 — Maximize data-ink

```
Data-Ink Ratio = data-ink / total ink = 1 − (proportion erasable without data loss)
```

Target: maximize toward 1.0, within reason.

**Five data-ink heuristics:**

1. Maximize data-ink ratio.
2. Erase non-data-ink.
3. Erase redundant data-ink.
4. Revise and edit.
5. Every mark must earn its place.

**Erasing principles in practice:**

- Remove background grid lines that don't add new information.
  Grid lines should be muted, lighter than any data element.
- Remove tick marks that duplicate what axis labels already say.
- Remove data frame boxes unless they encode information.
- Remove legends when data can be labeled directly.
- Halve bars: bar height + shaded area both encode the same value.
  A dot plot encodes it once. Prefer dots.
- Range-frame axes: instead of full box axes, draw axis lines only
  across the actual data range. Removes ink that implies data that
  doesn't exist.

**Chartjunk — the three species to eliminate:**

| Species         | Description                                  | Example                                                      |
| --------------- | -------------------------------------------- | ------------------------------------------------------------ |
| Moiré vibration | Hatching, cross-hatching, fine fill patterns | Diagonal-stripe bars                                         |
| Heavy grids     | Grid lines dominating over data              | Grid thicker than data lines                                 |
| Graphical ducks | Decoration overriding data; design > signal  | 3D bars, novelty shapes, pictograms sized to encode quantity |

Never fill bars, areas, or backgrounds with patterns (stripes,
hatching, cross-hatching). Zero chartjunk is almost always better
than a graphic with even small amounts.

### Step 5 — Layer and separate

Every graphic has visual strata. Assign weight to reflect informational
importance:

- **Background / structural** — light gray, muted, low saturation.
  Grid lines (if any), axes, borders.
- **Data** — full weight. The most prominent visual element on the
  page should be the data itself.
- **Annotation** — labels, callouts, leaders. Subordinate to data,
  but clearly legible. Annotate directly on the graphic; never force
  the viewer to cross-reference a legend.

**The 1+1=3 effect (Albers):** When two visual elements share a
surface, they generate not just themselves but also an incidental third
element — the interaction between them. This interaction is almost
always noise. Manage it through contrast of weight and saturation.

**Table design:** avoid ruled grids where possible. "Tables should
not look like nets." Use white space to separate columns; use thin
rules only when columns are too narrow to separate by space alone.

---

## Workflow B: Critique an Existing Graphic

Work through these five checks in order. Produce findings for each.

### Check 1 — Graphical integrity

- Calculate lie factor if the graphic uses physical size to represent
  quantity. LF > 1.05 or LF < 0.95 = substantial distortion.
- Is the baseline zero or is it cut-in without labeling?
- Are scales consistent across panels?
- Does the number of visual dimensions match the number of data
  dimensions?
- Is money adjusted for inflation?
- Is any data quoted out of context?

### Check 2 — Chartjunk audit

Name every species present:

- Moiré / hatching fills
- Heavy grid (thicker than data lines)
- Graphical ducks (novelty shapes, pictograms, 3D-for-2D)
- Decorative elements (drop shadows, gradients, background images)
- Redundant tick marks or over-dense axis labeling

### Check 3 — Data-ink ratio

Ask the eraser test for every non-data element: "If I remove this,
does the viewer lose information not conveyed elsewhere?"

Common eliminations:

- The data frame box
- Tick marks paired with explicit axis labels
- Legend boxes when direct labeling is possible
- Background fill color that encodes nothing
- 3D depth rendering

### Check 4 — Comparison structure

- What comparison does this graphic enable? Name it.
- Is there a better comparison the data supports but doesn't show?
- If multiple series are overlaid: is a small multiples layout
  clearer? Use small multiples whenever comparing shape across
  conditions matters more than comparing precise values at a moment.
- Does the graphic answer "compared to what?" or does it strand a
  single number without context?

### Check 5 — Color audit

Apply the 4-use framework — each color element should serve exactly
one role:

| Role      | Function                   | Rule                                         |
| --------- | -------------------------- | -------------------------------------------- |
| Label     | Distinguish categories     | ≤ 8 categories; use hue not lightness        |
| Measure   | Encode continuous variable | Sequential palette, never rainbow            |
| Represent | Mimic natural appearance   | Blue for water, green for vegetation         |
| Decorate  | Beauty/attention           | Sparingly; small areas; against muted ground |

Red flags:

- Rainbow palette for continuous data (false boundaries at red-yellow,
  cyan-blue transitions)
- Equal-value complementary colors adjacent (red/green, orange/blue
  at same lightness → Albers vibration)
- More than 8–10 categorical colors (loses distinguishability)
- Saturated color over large background areas

---

## Output Shape

### Critique output

Structure every critique as:

1. **Diagnosis** — one sentence summary of the primary problem
2. **Lie factor** (if applicable) — computed estimate and cause
3. **Chartjunk found** — species list with location
4. **Data-ink opportunities** — specific elements to erase or simplify
5. **Comparison question** — what "compared to what?" this graphic
   misses or could add
6. **Color issues** (if any)
7. **Redesign sketch** — describe the better form (chart type, encoding,
   layout) in plain language or ASCII. Cite the Tufte exemplar this
   should aspire toward.

### Design output

Structure every design recommendation as:

1. **The comparison question answered** — "This graphic shows X
   compared to Y"
2. **Form chosen + rationale** — chart type, why it's right for
   this data, which principle governs the choice
3. **Encoding specification** — what maps to x, y, size, color, shape
4. **Ink budget** — what will NOT appear (no legend because labels
   are direct, no grid because…)
5. **Sketch** — ASCII layout or prose description of the final form
6. **Exemplar anchor** — which Tufte exemplar this most resembles and
   why

---

## Quick Rules Card

**Six principles of graphical integrity (VDQI, pp. 53–87):**

1. Numerical proportionality: size of effect in graphic = size of
   effect in data.
2. Label clearly and thoroughly; write explanations on the graphic.
3. Show data variation, not design variation.
4. Standardize monetary data for inflation before displaying.
5. Number of visual dimensions = number of data dimensions.
6. Do not quote data out of context.

**Five data-ink heuristics (VDQI, pp. 91–105):**

1. Maximize data-ink ratio.
2. Erase non-data-ink.
3. Erase redundant data-ink.
4. Revise and edit.
5. Every mark must earn its place.

**Color (4 purposes — EI, p. 81):**

Label → ≤ 8 hue categories | Measure → sequential palette, never rainbow
Represent → natural associations | Decorate → small areas, muted ground only

**Sparkline rules (SFE, pp. 22–33):**

- Word-sized (12–14pt tall), no axes, no labels
- Show shape, not precise values — context comes from surrounding text
- Common baseline when comparing multiple sparklines
- Include reference band or endpoint marker
- Array many together = image quilt analysis

---

## Anti-Pattern Shortlist

| Anti-pattern                       | Quick fix                                  |
| ---------------------------------- | ------------------------------------------ |
| 3D bar / pie chart                 | 2D sorted horizontal bar or dot plot       |
| Pie chart for ranking              | Sorted horizontal bar chart                |
| Spaghetti multi-line               | Small multiples, one series per panel      |
| Legend requiring eye travel        | Label data directly                        |
| Heavy grid dominating data         | Remove grid or use hair-thin gray lines    |
| Rainbow palette on continuous data | Sequential single-hue or diverging palette |

For the full catalogue with lie-factor examples, chartjunk species
anatomy, and color misuse patterns, read `references/anti-patterns.md`.

---

## Exemplar Anchors

When evaluating or designing, anchor judgment to these five exemplars
from Tufte's canon. They represent the ceiling of what graphic design
can do for data.

- **Minard's Napoleon March (1869)** — Six variables (army size,
  latitude, longitude, direction, date, temperature) in one image.
  No chartjunk, no legend needed, the graphic tells its own story.
  Aspire here when handling multivariate narrative data.

- **Galileo's Sunspot Records (1613)** — Small multiples indexed by
  date. Sequential observation proves mechanism (sun's rotation)
  through accumulation of constancy-of-design panels.

- **Yokohama Station Timetable** — Micro/macro perfection: each
  departure minute-digit IS the frequency distribution. Same ink
  serves exact lookup AND aggregate pattern simultaneously.

- **Swiss Topographic Maps (Matterhorn)** — All four color uses
  deployed simultaneously (label, measure, represent, decorate) with
  Imhof discipline: strong colors only on small extreme areas;
  muted tones on large calm areas.

- **Measles Vaccination Image Quilt (WSJ/van Panhuis 2015)** — 50
  states × decades; 1963 vaccine introduction appears as a
  near-universal color phase transition. The viewer sees not just that
  vaccination worked, but that it worked everywhere, consistently.
  This is visual causality evidence.

Full analysis of why each works in `references/exemplars.md`.

---

## Reference Files

Load the relevant reference file when you need deeper detail:

| File                                | Load when                                                                       |
| ----------------------------------- | ------------------------------------------------------------------------------- |
| `references/principles.md`          | You need the full definition, formula, and page citation for any principle      |
| `references/chart-decision-tree.md` | User is choosing between chart types; you need rationale beyond the table above |
| `references/color.md`               | Detailed palette choices, Imhof rules, specific color-by-data-type guidance     |
| `references/anti-patterns.md`       | Full catalogue of lie factor violations, chartjunk anatomy, color misuse        |
| `references/exemplars.md`           | Deep analysis of why the five canonical exemplars work                          |
| `references/checklists.md`          | Ship-check before handing off a design or critique                              |
