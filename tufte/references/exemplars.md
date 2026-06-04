# Exemplars Gallery — Full Reference

Source: VDQI §7; EI throughout; SFE §§3–4

These five graphics represent the ceiling of what information design can
achieve. Use them as anchors when evaluating or designing: "does this approach
what Minard did, or does it slide toward the NYT fuel road?"

---

## 7.1 Minard's Napoleon March (1869)

**"Probably the best statistical graphic ever drawn."** — Tufte, VDQI, p. 40

**What it shows:** Charles Joseph Minard's 1869 map of Napoleon's 1812 Russian
campaign.

**Variables encoded — six in one image:**

1. Army size → band width (thickness of the flow line)
2. Latitude → y-axis position
3. Longitude → x-axis position
4. Direction of movement → color (tan = advance, black = retreat)
5. Date → annotations along the retreat path
6. Temperature → separate line graph below, keyed to retreat by date

**Why it works:**

- The graphic tells its own story without explanation: the tan band flows east
  at full width (422,000 men), then the black band returns thinner and thinner,
  correlating directly with the temperature line plunging below zero.
- No legend needed — the encoding is so natural and rich that a viewer who has
  never seen it before can decode the tragedy in seconds.
- Zero chartjunk. Every mark encodes data.
- Multivariate without confusion: the 6 variables are assigned to distinct
  channels (position, size, color, time, annotation) that don't compete.
- Micro/macro: you can read the overall arc of catastrophe (macro) or focus on
  individual cities and temperature readings (micro) in the same image.

**Principles demonstrated:**

- Graphical excellence (VDQI §2.1): greatest number of ideas in least space
- Multifunctioning elements (VDQI §2.5): band width serves both the flow map
  and the data encoding simultaneously
- Narratives of space and time (EI §3.6): space and time combined
- Escaping flatland (EI §3.1): 6-dimensional data on 2D paper

**When to aspire here:** Any multivariate narrative dataset where causality and
change over time are both present. When the data tells a story with moral weight.

---

## 7.2 Galileo's Sunspot Records (1613)

**Source:** Galileo Galilei, _Istoria e dimostrazioni intorno alle macchie
solari_, 1613. (EI, pp. 18–19)

**What it shows:** A series of hand-drawn images of the solar disk, each
showing sunspot positions on a specific date, arranged sequentially.

**Why it works:**

- **Small multiples as proof:** The same design (solar disk outline, spots plotted
  by position) repeats across dates. The constancy of design means any change
  between panels is data, not format.
- **Visual causality:** The spots shift consistently across the disk from one
  panel to the next, and then reappear on the same side in later panels. This
  sequential pattern proves that the spots are on the surface of the sun
  (rotating with it), not independent orbital bodies. The proof is visual and
  immediate.
- **Multivariate:** Each panel encodes location (x/y on disk), time (panel
  index), and identity (spot labels A, B, C… parade alphabetically across
  panels).
- No chartjunk. The solar disk outline is necessary (the boundary of the data).
  The spots are data. Nothing else.

**Principles demonstrated:**

- Small multiples (EI §3.4; VDQI §2.6): "inevitably comparative, deftly
  multivariate"
- Evidence presentation (SFE §4.3): sequential observation converts raw data
  into causal evidence
- Graphical integrity (VDQI §2.2): the representation never distorts

**When to aspire here:** Any dataset where the question is about change over
conditions, time, or categories — especially where the pattern across panels
is the evidence.

---

## 7.3 Yokohama Station Keihin Express Timetable

**Source:** EI, p. 46

**What it shows:** A departure timetable for trains from Yokohama Station — 292
daily trains, shown as a grid of departure times organized by hour (rows) and
minute (columns).

**Why it works:**

- **Pure micro/macro:** Each entry is an individual departure time (micro). The
  density of entries in each row is the frequency distribution of train
  departures by hour (macro). The same ink serves two completely different
  reading modes simultaneously.
- **Multifunctioning element perfection:** The departure minute digits ARE the
  frequency distribution. No additional graphic element needed. The data itself
  is the chart.
- **Zero chartjunk:** No grid lines. No background. No decoration. The digit
  positions communicate the distribution; the digit values communicate the
  exact times.
- High data density: 292 readings in a compact space.

**Principles demonstrated:**

- Micro/macro readings (EI §3.2)
- Multifunctioning graphical elements (VDQI §2.5)
- Data density (VDQI §2.6): the data IS the structure

**When to aspire here:** Any dataset where individual data points are both
lookup values AND parts of a distribution. Dense tabular data that has
structure worth revealing visually.

---

## 7.4 Swiss Topographic Maps (Matterhorn)

**Source:** EI, p. 80

**What it shows:** The official Swiss 1:25,000 topographic map of the Matterhorn
region, designed according to Eduard Imhof's cartographic principles.

**Why it works:**

- **All four color uses deployed simultaneously:**
  - _Label:_ Blue for water, gray for stone — distinguishes categories
  - _Measure:_ Elevation shading from light valleys to dark peaks — encodes
    continuous quantitative variable
  - _Represent:_ Glaciers in white/blue, vegetation in greens — natural
    associations that require no decoding
  - _Decorate:_ The overall visual harmony and aesthetic care — but subordinate
    to all the above

- **Imhof's Rule 1 in practice:** Strong, saturated colors appear only on small
  extreme areas (very high peaks, deep water bodies, glaciers). Large calm areas
  (slopes, meadows, intermediate terrain) use muted, low-saturation tones. The
  eye is drawn to the extremes because they stand out against the calm ground.

- **Layering and separation:** Contour lines (structural) are thin and muted.
  Terrain shading (structural) recedes. Labels and spot elevations (annotation)
  are clear but do not overwhelm. The geography (data) dominates.

- **Escaping flatland:** A 2D sheet encodes 3D terrain (contours + shading),
  4th variable of land cover (color representation), and 5th variable of
  infrastructure (roads, trails).

**Principles demonstrated:**

- Color (EI §3.5): the four uses in practice
- Layering and separation (EI §3.3): visual strata by informational importance
- Escaping flatland (EI §3.1): multiple dimensions on 2D surface

**When to aspire here:** Any geographic visualization. Any design challenge
requiring multiple simultaneous variables. Any case where color is the primary
tool.

---

## 7.5 Measles Vaccination Image Quilt (WSJ / van Panhuis 2015)

**Source:** SFE, p. 33

**What it shows:** A matrix of measles case rates in the United States —
50 states (rows) × years 1928–2002 (columns) — with color encoding case count
per year per state.

**Why it works:**

- **Before/after natural experiment:** Each state serves as its own control.
  The same unit (each state) is observed across the treatment divide (1963
  vaccine introduction). No separate control group needed — time provides it.

- **The evidence is visual and immediate:** The 1963 vaccine introduction line
  appears as a near-universal color phase transition across all 50 rows
  simultaneously. Warm colors (high case counts) dominate the left half; cool
  colors (low or zero cases) dominate the right half. The viewer sees not just
  that vaccination worked, but that it worked everywhere, consistently, in the
  same year.

- **Image quilt as analysis tool:** 50 rows × ~75 years = 3,750 individual
  data cells. A single line chart of national average would hide state-level
  variation. The quilt shows the heterogeneity (some states had lower rates
  earlier; some spiked later) AND the dominant trend simultaneously.

- **Causal evidence, not just correlation:** The temporal alignment with the
  intervention, the universality across all 50 rows, and the absence of
  alternative explanations that could cause a simultaneous shift in all states
  constitute strong visual evidence of causation.

**Principles demonstrated:**

- Image quilts / sparklines (SFE §4.2): matrix of many series
- Evidence presentation (SFE §4.3): before/after, universal effect
- Small multiples (EI §3.4): each state is one panel in a constancy-of-design
  matrix
- Statistical integrity (SFE §4.4): shows the full data (all states, all years),
  not a summary statistic

**When to aspire here:** Any dataset with a natural experiment structure (same
unit, before and after an intervention). Any case where you want to show that
a pattern is universal, not just average. Any high-dimensional dataset where
a summary would hide important structure.
