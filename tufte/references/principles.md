# Tufte Principles — Full Reference

All citations to:

- VDQI = _The Visual Display of Quantitative Information_, 2nd ed., 2001
- EI = _Envisioning Information_, 1990
- SFE = _Seeing with Fresh Eyes_, 2020

---

## 2.1 Graphical Excellence (VDQI, Ch. 1, pp. 13–51)

**Definition:** The well-designed presentation of interesting data — a matter of
substance, statistics, and design. Gives the viewer the greatest number of ideas
in the shortest time with the least ink in the smallest space.

**Rules:**

- Show the data above all else; do not distort it.
- Induce the viewer to think about the substance, not the design or methodology.
- Present many numbers in a small space.
- Make large data sets coherent.
- Encourage the eye to compare different pieces of data.
- Reveal data at several levels of detail: broad overview to fine structure.
- Serve a clear purpose: description, exploration, tabulation, or decoration.
- Be closely integrated with the statistical and verbal descriptions of a data set.

---

## 2.2 Graphical Integrity (VDQI, Ch. 2, pp. 53–87)

**Definition:** Graphics must not lie. The representation of numbers, as physically
measured on the surface of the graphic, should be directly proportional to the
numerical quantities represented.

**The 6 Principles of Graphical Integrity:**

1. The representation of numbers should be directly proportional to the numerical
   quantities they represent.
2. Clear, detailed, and thorough labeling defeats graphical distortion and
   ambiguity. Write out explanations of the data on the graphic itself. Label
   important events in the data.
3. Show data variation, not design variation.
4. In time-series displays of money, deflated and standardized units of monetary
   measurement are nearly always better than nominal units.
5. The number of information-carrying (variable) dimensions depicted should not
   exceed the number of dimensions in the data.
6. Graphics must not quote data out of context.

**Lie Factor formula (VDQI, p. 57):**

```
Lie Factor = (size of effect shown in graphic) / (size of effect in data)
```

Acceptable range: **0.95–1.05**. Outside this range = substantial distortion.

- LF > 1: graphic overstates the effect
- LF < 1: graphic understates the effect
- Classic violation: NYT fuel economy road graphic. Data changed 53% (18→27.5
  mpg); road graphic changed 783%. Lie Factor = 783/53 = **14.8** (VDQI, p. 57)

**Causes of high lie factors:**

- Perspective distortion (roads, columns receding into depth)
- Shrinking icons (scaling a 2D icon by one dimension inflates area ∝ change²)
- Dual-axis manipulation that changes apparent ratios
- No zero baseline without clear labeling
- 3D effects adding depth cue on 2D data (actual change^2 or change^3 distortion)

---

## 2.3 Data-Ink Ratio (VDQI, Ch. 4, pp. 91–105)

**Definition:** Data-ink is the non-erasable core of a graphic — the ink devoted
to the presentation of the data-information.

**Formula:**

```
Data-Ink Ratio = data-ink / total ink used to print the graphic
               = 1.0 − (proportion of graphic that can be erased without data loss)
```

**Target:** Maximize toward 1.0, within reason.

**Four rules:**

1. Maximize the data-ink ratio, within reason.
2. Erase non-data-ink, within reason.
3. Erase redundant data-ink, within reason.
4. Revise and edit.

**Erasing principles in practice:**

- Remove background grid lines that don't add new information.
- Remove tick marks that duplicate what axis labels already communicate.
- Remove data frame boxes unless they encode information.
- Remove legend boxes and redundant labels when data can be labeled directly.
- Halve bars: a bar chart encodes its value twice (height + shaded area). A dot
  plot encodes it once. Prefer dot plots.
- Range-frame axes: draw axis lines only across the actual data range, not
  extending beyond it. Removes ink that implies non-existent data (VDQI, pp. 130–132).

---

## 2.4 Chartjunk (VDQI, Ch. 5, pp. 107–121)

**Definition:** Non-data-ink or redundant data-ink that clutters a graphic,
obscuring the data signal. Decoration that competes with data.

**Three species:**

| Type            | Description                                                    | Example                                   |
| --------------- | -------------------------------------------------------------- | ----------------------------------------- |
| Moiré vibration | Hatching, cross-hatching, fine patterns that vibrate optically | Bar charts with diagonal stripes          |
| Heavy grids     | Prominent grid lines dominating over data                      | Gridlines thicker than data lines         |
| Graphical ducks | Decoration that overrides the data; design louder than signal  | 3D bar charts, novelty shapes, pictograms |

**Rules:**

- Never fill bars, areas, or backgrounds with patterns (stripes, hatching,
  cross-hatching, polka dots).
- Grids should be muted, subordinate to data; if in doubt, erase them.
- Data should be the most visually prominent element; decoration should recede.
- A graphic with zero chartjunk is almost always better than one with even
  small amounts.

---

## 2.5 Multifunctioning Graphical Elements (VDQI, Ch. 6, pp. 139–150)

**Definition:** When a single graphical element serves multiple data functions
simultaneously, information density increases without adding ink.

**Rules:**

- Design elements to carry as many data dimensions as space allows.
- Use data labels as data points (e.g., two-letter state abbreviations plotted
  at their data value).
- Use the data itself as the graphical structure (stem-and-leaf plots; dot plots
  with labeled points).
- Avoid single-function ink — every mark should communicate something.

---

## 2.6 Data Density and Small Multiples (VDQI, Ch. 6, pp. 161–166)

**Data density formula:**

```
Data Density = (entries in data matrix) / (area of data graphic in cm²)
```

Higher is generally better. Tufte's exemplars often achieve >20 entries/cm².

**Small multiples:** A series of graphics using the same design structure,
showing how a variable changes across conditions. They are "inevitably
comparative" (VDQI, p. 170).

**Rules:**

- Same design, same scale, same encoding across all panels.
- Constancy of design puts the emphasis on changes in data, not changes in format.
- Index panels by the most important variable (time, condition, category).
- Postage-stamp-sized images are sufficient for pattern detection.
- Position within eyespan so viewers can compare without re-encoding.
- Core question answered: "Compared to what?"

---

## 2.7 Aesthetics and Technique (VDQI, Ch. 9, pp. 177–190)

**Rules:**

- Have a properly chosen format and design.
- Use words, numbers, and drawing together.
- Reflect a balance of data complexity and data density; achieve data-rich designs.
- Have a narrative quality — a story to tell about the data.
- Avoid content-free decoration.
- Draw in a professional manner, with obvious care.
- Tell the truth about the data.

---

## 3.1 Escaping Flatland (EI, Ch. 1, pp. 12–33)

**Definition:** The core challenge of information design is to represent
N-dimensional data on the 2-dimensional flatland of paper or screen. Every tool
available to the designer must be recruited to add dimensions back.

**Strategies for escaping flatland:**

| Strategy                  | Dimension added     | Exemplar               |
| ------------------------- | ------------------- | ---------------------- |
| Micro/macro readings      | Scale + detail      | Yokohama timetable     |
| Layering                  | Semantic depth      | Annotated calligraphy  |
| Small multiples           | Time or condition   | Galileo sunspots       |
| Color                     | 4th variable        | Swiss topographic maps |
| Narrative of space + time | Combined dimensions | Marey train schedule   |

---

## 3.2 Micro/Macro Readings (EI, Ch. 2, pp. 37–53)

**Definition:** A design achieves micro/macro readings when it provides coherent
detail at both a magnified level (individual data points) and a zoomed-out level
(overall pattern), simultaneously.

**Rules:**

- Use the same visual element to encode both individual data and aggregate
  structure.
- Replace empty bars in a histogram with the actual data values (digit plots,
  dot plots).
- Design tables so that the individual entry and the marginal totals are both
  readable.
- Compress many readings into a small space; the eye should move between detail
  and overview without losing context.

**Exemplar:** Yokohama Station timetable — 292 daily trains encoded as stacked
minute-digits. The individual departure times ARE the frequency distribution.
Pure micro/macro. (EI, p. 46)

---

## 3.3 Layering and Separation (EI, Ch. 3, pp. 53–65)

**Definition:** Visual stratification of information layers — background, data,
annotation, labels — so that each layer is legible and the layers do not fight
each other.

**The 1+1=3 effect (Albers):** When two visual elements share flatland, they
generate not only themselves but also an incidental third element — the
interaction between them. This interaction is almost always noise. Design to
minimize it.

**Rules:**

- Assign light gray (muted) values to background and structural elements.
- Reserve saturated color and heavy weight for data.
- Annotation (labels, leaders, callouts) should be visually subordinate to the
  data it describes.
- Tables: avoid ruled grids wherever possible ("Tables should not look like
  nets"). Use white space to separate columns; use thin rules only when columns
  are too narrow to separate by space alone.
- When a grid is needed, use very fine, light lines — they should read as
  texture, not barricade.
- Maintain proportion and harmony between layers; the visual weight of each
  layer should reflect its informational importance.

---

## 3.4 Small Multiples (EI, Ch. 4, pp. 67–79)

**Definition:** A series of graphics using the same design structure, repeated
for different slices of data — indexed by category, time, or a quantitative
variable.

**Core question answered:** _Compared to what?_

**Rules:**

- Use the same design, same scale, same encoding across all panels.
- Constancy of design puts the emphasis on changes in data, not changes in format.
- Index panels by the most important variable (time, condition, category).
- Illustration at postage-stamp size is sufficient for pattern detection.
- Position within eyespan so viewers can compare at a glance without re-encoding.
- Differences between panels should encode one thing: the data change.

---

## 3.5 Color and Information (EI, Ch. 5, pp. 81–95)

See `color.md` for full color reference.

**Definition:** Color serves four distinct purposes. Most failures in color arise
from conflating these purposes or exceeding the eye's discrimination capacity.

**Imhof's Rules:**

- **Rule 1:** Pure, bright, or very strong colors have loud, unbearable effects
  when used unrelieved over large areas adjacent to each other. Use strong colors
  sparingly, on small areas of extremes, against muted or gray backgrounds.
  ("Noise is not music.")
- **Rule 2:** Light, bright colors mixed with white placed next to each other
  produce unpleasant results, especially over large areas.
- **Constructive corollary:** Small color spots against a light gray or muted
  field highlight and italicize data, weave overall harmony, and avoid the
  1+1=3 interaction noise.

---

## 3.6 Narratives of Space and Time (EI, Ch. 6, pp. 97–121)

**Definition:** Graphics that encode both spatial position and temporal sequence —
allowing the eye to trace a journey through time and space simultaneously.

**Rules:**

- Show movement, trajectory, and change — not just static position.
- Use path width or intensity to encode quantity (Minard uses army size as
  band width).
- A graphical timetable (position × time) reveals scheduling structure
  impossible to see in tabular form.
- Combine macro overview (entire route) with micro precision (individual
  times) in one display.

**Exemplar:** Marey/Ybry graphical train schedule — diagonal lines encode each
train's journey from Paris to Lyon. Slope = speed; vertical spacing = stations;
overlaps reveal conflicts. (EI, p. 107)

---

## 4.1 Meaning, Space, Data, Truth (SFE, throughout)

**Core framework:** Every visual element earns its place by serving one of four
masters:

1. **Meaning** — Does this element communicate something true and relevant about
   the data?
2. **Space** — Is the available visual space used efficiently for information?
3. **Data** — Are the data shown accurately, at sufficient density?
4. **Truth** — Does the representation honor the actual numbers, relationships,
   and uncertainties?

**Rules:**

- Eliminate anything that fails all four tests.
- Prefer words, numbers, and images integrated together on the same display.
- Annotate directly on the graphic; do not require viewers to cross-reference
  a legend.
- Show causes and effects together when you have causal evidence.
- Distinguish correlation from causation explicitly in the display.

---

## 4.2 Sparklines (SFE, pp. 22–33)

**Definition:** Intense, simple, word-sized graphics. They embed data graphics
directly in the flow of text, enabling comparisons between many time-series at
once.

**Properties:**

- Size: word-height (approximately 12–14pt tall)
- No axes, no labels, no titles — context comes from surrounding words
- Show shape, not precise values
- Many sparklines can be arrayed in a table, creating a matrix of time-series

**Rules:**

- Use sparklines when comparing many time-series simultaneously.
- Sparklines should be the same height; scale to make variation visible but not
  exaggerated.
- Align sparklines on a common baseline when comparing multiple series.
- Include a reference band or marker for the current value.
- Never use a sparkline where a single number would suffice.

**Image quilt variant:** A matrix of sparklines indexed by two variables (rows
and columns), enabling visual analysis of interactions across thousands of series
simultaneously. Example: measles vaccination — 50 states × years; the 1963
vaccine introduction is visible as a near-universal color phase transition.

---

## 4.3 Evidence Presentation (SFE, pp. 45–75)

**Definition:** Showing data with sufficient context, comparison, and annotation
that viewers can evaluate causal claims.

**Rules:**

- Show comparisons: before/after, treatment/control, expected/observed.
- Use the natural experiment structure when available (same unit, different time).
- Include uncertainty: error bars, confidence intervals, prediction bands.
- Show the data that generated the claim, not just the summary statistic.
- Annotate key events (policy changes, interventions) directly on time-series.
- Causality requires: correlation + plausible mechanism + ruling out alternatives.

---

## 4.4 Statistical Integrity (SFE, pp. 90–110)

**Rules:**

- Report the number of observations (n) that generated any statistic.
- Use per-capita or normalized measures when comparing groups of different sizes.
- Show distributions, not just means. Show the full data when n is small.
- Distinguish statistical significance from practical significance.
- Avoid cherry-picking start dates that make trends look better or worse.
- For medical/public-health data: always report absolute risk alongside relative
  risk.
- "Statistical lives" (population-level benefits) are real and should be
  quantified.
