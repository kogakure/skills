# Ship Checklists

Run the relevant checklist before handing off any visualization work.
These are not aspirational — every item should pass before the graphic ships.

---

## Design Ship-Check

For any graphic you have designed or recommended.

**Integrity:**

- [ ] Lie Factor is between 0.95 and 1.05 (or there is no physical size encoding)
- [ ] Baseline is honest (zero, or cut-in clearly labeled with break symbol)
- [ ] Monetary data adjusted for inflation; units labeled
- [ ] Number of visual dimensions = number of data dimensions
- [ ] Data is not quoted out of context

**Data-ink:**

- [ ] Every mark on the graphic encodes data or aids reading (nothing purely decorative)
- [ ] Grid lines (if any) are lighter and thinner than any data element
- [ ] Legend eliminated in favor of direct labeling (or unavoidable and minimal)
- [ ] Data frame box removed or necessary
- [ ] Tick marks not duplicating axis labels
- [ ] No hatching, cross-hatching, or pattern fills
- [ ] No 3D effects on 2D data
- [ ] No drop shadows, gradients, or decorative backgrounds

**Form:**

- [ ] Chart type matches the comparison the data requires (see decision tree)
- [ ] "Compared to what?" is answered explicitly in the graphic
- [ ] If multiple series: small multiples considered and used or explicitly rejected
- [ ] Table used instead of graph if n < 20 and exact lookup is the primary task

**Color:**

- [ ] Each color element serves exactly one role (label / measure / represent / decorate)
- [ ] ≤ 8 categorical colors
- [ ] No rainbow palette on continuous data
- [ ] No equal-value complementary colors adjacent over large areas
- [ ] Strong colors only on small areas of extremes; background is muted

**Layering:**

- [ ] Data is the most visually prominent element on the page
- [ ] Structural elements (axes, grid) are visually subordinate to data
- [ ] Annotation is subordinate to data but clearly legible
- [ ] Labels annotate directly; no cross-referencing required

**Exemplar anchor:**

- [ ] This graphic is closest to which Tufte exemplar? Named: ******\_\_\_\_******
- [ ] If it's closer to an anti-pattern than an exemplar, revise before shipping.

---

## Critique Audit

For any graphic you have assessed or been asked to improve.

**Integrity check:**

- [ ] Computed lie factor for any size-encoded quantity
- [ ] Identified baseline manipulation (if any)
- [ ] Identified dual-axis manipulation (if any)
- [ ] Checked dimensional integrity (2D icon for 1D quantity?)
- [ ] Checked monetary inflation adjustment (if time-series with money)

**Chartjunk inventory:**

- [ ] Named every chartjunk species present (moiré / heavy grid / duck / 3D)
- [ ] Identified decorative elements not encoding data
- [ ] Identified redundant elements (same information shown twice)

**Data-ink opportunities:**

- [ ] Listed every element that passes the eraser test (can be removed without
      data loss)
- [ ] Noted whether legend could be replaced by direct labeling
- [ ] Noted whether chart type could be simplified (bars → dots, overlay → small
      multiples)

**Comparison structure:**

- [ ] Named the comparison the graphic enables
- [ ] Identified whether "compared to what?" is answered or missing
- [ ] Assessed whether small multiples would serve the comparison better
- [ ] Identified whether additional context (baseline, trend, range) is missing

**Color audit:**

- [ ] Identified each color's role (label / measure / represent / decorate / unclear)
- [ ] Flagged rainbow palette use
- [ ] Flagged equal-value complementary adjacency
- [ ] Flagged excess categories (> 8)

**Redesign prescription:**

- [ ] Named the recommended chart type
- [ ] Described the encoding (what maps to x, y, size, color)
- [ ] Named the Tufte exemplar this redesign should aspire toward
- [ ] Described what will NOT be in the redesign (chartjunk eliminated)
