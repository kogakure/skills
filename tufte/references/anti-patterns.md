# Anti-Patterns Gallery — Full Reference

Source: VDQI §§6, 8.4; EI §§5–6; compiled from Tufte's catalogues

For each anti-pattern: diagnosis, mechanism, and fix.

---

## 6.1 Lie Factor Violations

### The NYT Fuel Economy Road (VDQI, pp. 57–58)

**Graphic:** A receding road perspective showing fuel economy standards 1978–1985.

**What happened:** Data changed from 18 to 27.5 mpg (+53%). The road graphic
(measured by the line representing the 18 mpg standard vs. the 27.5 standard)
changed 783%.

**Lie Factor = 783/53 = 14.8** — one of the most extreme examples in Tufte's
catalogue.

**Mechanism:**

- Perspective distortion: the road recedes into the distance
- The "future" (1985) appears physically farther and more aspirational than
  the data justifies
- Dates remain constant size while values change — breaks proportionality

**Fix:** Simple line chart or dot plot, y-axis shows mpg, x-axis shows years.
No perspective. No road metaphor.

---

### The Incredible Shrinking Doctor (VDQI, p. 69)

**Graphic:** Icon-based graphic where doctor figures are scaled in height to
represent a 1D data value (dollar amount per person).

**Mechanism:** When a 2D icon is scaled by one dimension (height) to represent
a 1D quantity, the area changes by height². If the value doubles, the icon
height doubles but the area quadruples. The viewer perceives area, not height.

**General formula:**

```
Displayed change = (actual change)² for 2D icons
Displayed change = (actual change)³ for 3D icons
```

**Diagnosis:** Whenever a 2D or 3D icon is scaled by one dimension to represent
a 1D quantity, the graphic systematically inflates the change.

**Fix:** Use a bar or dot where the encoded dimension directly encodes the value.
If using area encoding, scale by area (radius = √value), not by height.

---

### Perspective Distortion (general)

**Pattern:** Charts drawn in perspective (3D bar charts, 3D pie charts, 3D area
charts) where depth cues cause front elements to appear larger than back elements
even at equal value.

**Mechanism:** 3D projection adds a parallax distortion. Front faces appear
larger than back faces. 3D pie slices near the viewer appear larger than equal
slices farther away.

**Rule:** Never use 3D for 2D data. A 3D bar chart adds depth that encodes no
data, introduces parallax distortion, and forces viewers to mentally project
back to 2D. Every such graphic has a Lie Factor > 1.0.

**Fix:** 2D bar chart, 2D pie (if you must use pie at all), or preferably sorted
horizontal bar chart.

---

### Dual-Axis Manipulation

**Pattern:** A chart with two y-axes, where the right axis is scaled to make
two lines appear to cross, converge, or track each other — when the relationship
is an artifact of the chosen scales.

**Mechanism:** Any two independent time series can be made to appear correlated
or anti-correlated by choosing different scale ranges for each axis. The visual
impression of relationship is manufactured by the designer's choices, not
present in the data.

**Fix:** If the relationship between two series matters, show it directly
(scatter plot of one vs. the other). If two series must be shown over time,
normalize each to a common index (e.g., both = 100 at start year) and overlay.
Label the normalization clearly.

---

### Cherry-Picked Baselines

**Pattern:** A line chart with a start date chosen to show the most favorable
trend; or a cut-in y-axis that makes a small change appear dramatic.

**Rules:**

- Cut-in baselines (y-axis not starting at zero) are acceptable only when the
  data range is narrow AND the cut-in is clearly labeled with a break symbol
  and both the true zero and the cut-in value.
- Start dates should reflect the natural period of the phenomenon, not the
  point that makes the trend look best.
- Show the full available time series; if you must truncate, explain why.

---

## 6.2 Chartjunk Patterns

### Moiré Vibration

**What it is:** Hatching, cross-hatching, diagonal stripes, or fine dot patterns
used as fill in bars, areas, or backgrounds.

**Why it's bad:** Fine periodic patterns interact with the physiological tremor
of the eye to produce the perception of shimmer and movement. The graphic
appears to vibrate. This optical noise overwhelms the data signal.

**Where it appears:**

- Bar charts with diagonal-stripe fills (common in academic publications)
- Area charts with dot or crosshatch fills
- Background patterns behind data

**Fix:** Solid fill. Use different gray values for different categories (varying
lightness encodes information cleanly). Or use white/outline bars and vary hue
only minimally.

---

### Heavy Grids (The Dreaded Grid)

**What it is:** Grid lines that are heavier (thicker, darker) than the data
lines or data points they surround.

**Why it's bad:** The most visually prominent element on the page is the grid
rather than the data. The structure meant to help read values becomes the
dominant visual feature — it competes with the information it's supposed to
support.

**Rule:** Grid lines should always be lighter and thinner than any data element.
If a grid line is more prominent than the data, erase it. Use it only if it
aids reading and cannot be replaced by direct labeling.

**Fix:**

- Remove grid entirely and label endpoints or key values directly.
- Or use very light gray hair-lines (approximately #e0e0e0 on white).
- Never use black or dark gray for grid lines in a data chart.

---

### Graphical Ducks

**Definition:** A graphic whose design (shape, decoration, novelty) overrides its
data content. Named after a duck-shaped building in Long Island that exists only
to look like a duck.

**Three forms:**

1. **Novelty shapes:** Bar chart where bars are replaced by shaped icons (stacks
   of oil barrels to represent oil production, stacks of people to represent
   population). The shape communicates the designer's cleverness, nothing about
   the data.

2. **Pictograms as data encoders:** Icons scaled in size to represent a value
   — combined with the shrinking-icon distortion problem (see above).

3. **Self-promoting decoration:** Background imagery, elaborate borders, or
   theme graphics that compete with the data for visual attention.

**Diagnosis:** "The design speaks louder than the data."

**Fix:** Remove the decoration. Use the simplest possible visual encoding
(bar, dot, line). The data should be the loudest thing on the page.

---

### 3D Effects on 2D Data

**What it is:** Drop shadows, beveling, 3D perspective, extrusion applied to
bars, columns, pie slices, or areas that represent 2D data.

**Why it's bad:**

- Adds visual complexity that encodes nothing
- Creates parallax distortion (see Lie Factor section above)
- Forces viewers to mentally project 3D rendering back to 2D data values
- The bottom face of a 3D bar is ambiguous — does the bar end at the top edge
  or the bottom edge of the top face?

**Fix:** 2D everything. The third dimension of a display should be reserved for
data that actually has a third dimension.

---

### Redundant Legends

**What it is:** A separate legend box requiring eye travel, when the same
information could be labeled directly on the data.

**Why it's bad:** Forces the viewer to repeatedly look away from the data to
decode it. Slows comprehension. The legend is a non-data element that takes
space and attention.

**Fix:** Label data directly wherever space permits. In a line chart with 3
lines, label each line at its rightmost point. In a bar chart with 3 categories,
label inside or adjacent to each bar. Reserve the legend for cases where direct
labeling is genuinely impossible due to density.

---

## 6.3 Color Misuse

### Rainbow Palette for Continuous Data

**Problem:** Non-monotonic luminance creates false perceptual boundaries in
continuous data. The eye "sees" sharp edges at the red-yellow and cyan-blue
transitions even when the data is smooth.

**Example:** A temperature map using the full ROYGBIV rainbow — the viewer
perceives bands of equal temperature even though the data gradient is smooth.
These phantom bands communicate false structure.

**Fix:** Sequential single-hue palette or a perceptually uniform palette
(viridis is the canonical modern standard). The lightness gradient should be
monotonic — lighter = less, darker = more (or vice versa), with no reversals.

---

### Equal-Value Complementary Colors Adjacent

**Problem:** Red next to green at equal lightness; blue next to orange; yellow
next to purple — produces the Albers vibration. Apparent shimmer and instability
at boundaries. Especially problematic over large areas (see Imhof Rule 1).

**US Census map example (EI, p. 82):** Adjacent regions in saturated
complementary colors create unreadable vibration across the entire map.

**Fix:** Ensure adjacent color regions differ in lightness, not just hue. Or
separate them with a white/gray boundary. Or use the Imhof approach: strong
saturated colors only on small extreme areas against a muted ground.

---

### Too Many Categorical Colors

**Problem:** Beyond 8–10 distinguishable categorical colors, reliable
identification fails. Viewers confuse similar hues; legend-to-data matching
becomes guesswork.

**Common failure:** 15-line chart with 15 differently-colored lines and a legend.
Nobody can reliably match a line color to a legend entry beyond ~5–8.

**Fix:**

- Reduce categories (group minor ones into "Other")
- Use small multiples — one category per panel eliminates the need for a
  multi-color legend entirely
- Highlight the most important 1–2 categories in color, render the rest in
  gray
- Use shape + color together so color is not the only differentiator
