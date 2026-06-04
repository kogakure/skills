# Chart Type Decision Tree — Full Reference

Source: VDQI §8.4 + Tufte exemplar per branch

The master question: **"What comparison am I trying to enable?"**

Every chart type is a machine for enabling a specific kind of comparison.
Choose the chart type that makes the most important comparison visible at a glance,
with minimum viewer effort and maximum honesty.

---

## The Decision Tree

### Does the viewer need exact values, or shape/trend?

**Exact values** → **Table** (unless one of the exceptions below applies)

Use a table when:

- Readers need precise lookup of individual values
- Multiple heterogeneous quantities per row (different units)
- Single measurement per row item
- n < 20 rows
- The data resists meaningful visual encoding

Use a **table-graphic hybrid (sparkline table)** when:

- Rows need both exact values AND trend shape simultaneously
- Many time-series, one row each, trend matters as much as current value
- Example: quarterly financial report — numbers in columns, sparkline in last column

**Shape/trend/pattern** → continue below

---

### What is the primary data structure?

#### A. Two continuous variables → **Scatterplot**

- Do NOT use a bar chart or line chart
- Use range-frame axes (axis lines span only data min–max, not beyond)
- Consider range-frame with dot-dash marginals for distribution insight
- Label outliers or interesting points directly
- Add reference line only if the comparison requires it (identity line, regression)
- If overplotting: use alpha transparency, jitter, or bin-based size encoding

When NOT to use: ranking, time-series with >2 points (use line chart instead),
categorical x-axis.

**Exemplar:** Galileo's data points for sunspot positions — clean, no chartjunk,
scatter reveals pattern.

---

#### B. One variable over time (single series) → **Line chart**

- Draw the data line, label endpoints directly, remove legend
- No fill under the curve unless you're encoding area deliberately
- Start y-axis at a meaningful value — zero is correct when the baseline matters;
  a cut-in baseline is acceptable only when the data range is narrow AND the
  cut is clearly labeled
- For monetary data: adjust for inflation first; label units as "in [year] dollars"
- Range-frame axes: draw axis from data min to data max, not beyond

**Exemplar:** Playfair's 1786 trade surplus/deficit chart — the shaded area
between export and import lines directly encodes the surplus or deficit as
geometric area.

---

#### C. One variable over time, multiple series (compare shape) → **Small multiples**

Do NOT overlay into a spaghetti chart unless there are ≤ 3–4 series with
clearly separated values and no crossing.

**Small multiples:**

- Same design, same scale, same encoding in every panel
- Index by the variable that changes across panels (category, region, condition)
- Place panels in reading order or sorted by a meaningful variable (e.g., decreasing
  total, geographic position)
- Common y-axis range across all panels unless the per-panel scale is the
  explicit message
- Panels should fit within a single eyespan — postage-stamp size is enough for
  pattern detection

**When series are many and detail is needed:** small multiples in a grid.
**When series are very many and shape comparison suffices:** sparkline table.

**Exemplar:** Galileo's sunspot small multiples (1613) — sequential panels, same
disk outline, spots plotted by date. The accumulation of constancy-of-design
panels proves mechanism through visual comparison.

---

#### D. Many time-series, pattern comparison → **Sparkline table**

- One row per series
- Sparklines in the same column, aligned on a common baseline
- Adjacent numeric columns for current value and key statistics
- No axes, no labels on sparkline itself — prose context surrounds it
- Height: word-height (12–14pt)

---

#### E. Distribution of one continuous variable

- **n < 50:** Dot plot or strip plot. Plot every observation. No binning —
  the actual data is the display. Jitter if overplotting.
- **n ≥ 50:** Histogram or kernel density. Choose bin width so that the
  distribution shape is visible, not dominated by noise.
- **Comparing distributions across groups:** Parallel dot plots (aligned on
  common axis). Or Tufte's quartile plot (stripped-down box plot): erase the box,
  show only the IQR as an offset tick, median as a point, whiskers to data range.
- **Never:** 3D bar chart for distributions. It obscures the actual height
  relationship through parallax.

---

#### F. Ranking / comparing magnitudes across categories → **Sorted horizontal bar chart**

- Sort by value, descending (or the ordering that serves the comparison)
- Horizontal orientation: category labels are readable without rotation
- Use dots (Cleveland dot plot) instead of bars — encodes once instead of twice
- Keep bars or dots aligned on a common zero baseline
- Direct label or adjacent number — no legend
- **Never:** Pie chart for ranking. The eye cannot compare arc lengths or slice
  areas reliably. Studies consistently show ranked bar charts are decoded faster
  with less error.

**Exemplar:** Any of Tufte's sorted dot plots in VDQI pp. 133–136.

---

#### G. Part-to-whole (proportions of a total)

- Sorted bar chart showing shares (each bar is x% of total)
- Or a stacked bar with ≤ 3 segments (segment count beyond 3 destroys
  comparability)
- **Avoid pie chart.** The only case for a pie: a single dramatic dominant
  slice (>80%) where the visual message is "almost all of it."
- **Never:** 3D pie chart. The front slices appear larger than the back slices
  at equal value — systematic lie.

---

#### H. Geographic distribution → **Map with proportional symbols or dots**

- Proportional symbols (circles scaled to value) at location: honest, shows
  magnitude + geography simultaneously
- Dot map (one dot = N units): shows spatial density, avoids area distortion
- **Choropleth (filled map):** use ONLY for rates (per capita, per area). Never
  for totals — Wyoming and California populations in absolute terms encoded by
  fill color would systematically mislead because area and population are
  uncorrelated.
- Sequential palette for continuous rate data (not rainbow)
- Direct labeling > legend wherever legible

---

#### I. Many variables, same subjects, across time → **Parallel coordinates or slopegraph**

- **Parallel coordinates:** vertical axes for each variable, subjects as lines
  crossing all axes. Reveals clustering, outliers, and correlations that scatter
  matrix misses for high-dimensional data.
- **Slopegraph:** two-column parallel coordinates (time 1 vs time 2). Lines
  show direction and magnitude of change per subject. Sort both columns
  consistently.

---

## Table vs. Graph: The Decision Rule

| Use a **table** when…             | Use a **graph** when…            |
| --------------------------------- | -------------------------------- |
| Readers need exact values         | Shape, trend, or pattern matters |
| Multiple heterogeneous quantities | Comparing many items             |
| Single measurement per item       | Temporal change                  |
| n < 20 rows                       | Distribution or relationship     |

**Mixed form:** Sparkline in each table cell = exact lookup AND pattern
simultaneously. The best of both worlds when you have both requirements.

---

## When Small Multiples Beat Everything Else

Deploy small multiples whenever:

1. You have data that varies across two dimensions (e.g., time × category)
2. The question is about **shape or pattern change** across the second dimension
3. Overlaying into one chart would create crossing lines, overplotting, or
   a legend requiring eye travel
4. You want the viewer to compare patterns without re-encoding

Constancy of design is the key: every panel is identical in structure. The only
thing that changes is the data. This is what Tufte means by "inevitably comparative,
deftly multivariate" (VDQI, p. 170).

**Never use small multiples when:**

- Panels would have such different y-ranges that comparison is impossible
  without a shared scale (exception: explicitly per-panel normalized scales
  with clear labeling)
- You only have 1–2 series (just overlay or use a slopegraph)
