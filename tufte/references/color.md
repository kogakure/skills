# Color and Information — Full Reference

Source: EI, Ch. 5, pp. 81–95

The first rule: **"Above all, do no harm."** Before adding any color, ask:
does this encode information, or does it just decorate?

---

## The Four Uses of Color

Color in information design serves exactly four distinct purposes. Every color
element in a graphic should serve exactly one of these roles. Conflating roles
or adding color beyond these purposes creates noise.

| Role          | Color functions as | What it does                 | Example                                |
| ------------- | ------------------ | ---------------------------- | -------------------------------------- |
| **Label**     | Noun               | Distinguish categories       | Water (blue) vs. stone (gray) on a map |
| **Measure**   | Quantity           | Encode a continuous variable | Elevation shading from light to dark   |
| **Represent** | Reality imitation  | Mimic natural appearance     | River blues, vegetation greens         |
| **Decorate**  | Beauty             | Enliven, attract attention   | Use sparingly, small areas only        |

---

## Imhof's Rules

Eduard Imhof's rules from _Cartographic Relief Presentation_ apply to all
information graphics, not just maps.

**Rule 1:** Pure, bright, or very strong colors have loud, unbearable effects when
used unrelieved over large areas adjacent to each other. Use strong colors
sparingly, on small areas of extremes, against muted or gray backgrounds.
_"Noise is not music."_

**Rule 2:** Light, bright colors mixed with white placed next to each other produce
unpleasant results, especially over large areas.

**Constructive corollary:** Small color spots against a light gray or muted field
highlight and italicize data, weave overall harmony, and avoid the 1+1=3
interaction noise.

**Practical translation:**

- Background and structural elements: light gray, low saturation, muted tones.
- Data signals: saturated, high-contrast colors to pop against muted ground.
- Strong colors only on small areas of extremes (the highest values, the
  critical events, the outliers).

---

## Color Rules by Use

### Labeling (categorical distinction)

- Limit distinguishable categories to **5–8 colors maximum** in a single display.
  Beyond 8–10 categorical colors, the eye loses reliable distinguishability.
- Use **hue** (not lightness) to separate categories of equal importance.
- Use **lightness** only to encode hierarchy or quantity — not categories.
- Use color to label only when shape/position alone cannot separate the categories.
- If categories exceed 8: reduce categories, use shape/position to differentiate,
  or use faceting (small multiples) instead.

### Measuring (continuous variables)

- Use **sequential palettes** (single-hue, light to dark) for data with a
  meaningful zero or minimum.
- Use **diverging palettes** (two hues diverging from a neutral midpoint) when
  the data has a meaningful center (zero, target, average) and deviation in
  both directions matters.
- **Never use rainbow** (spectral palette) for continuous data. The rainbow's
  non-monotonic perceptual luminance creates false boundaries — the eye
  perceives sharp edges at red-yellow and cyan-blue transitions that do not
  exist in the data.
- For choropleth maps showing rates: sequential or diverging, never rainbow.

### Representing (natural appearance)

- Follow natural color associations: blue for water, green for vegetation,
  brown for rock/terrain, white for snow.
- These associations are pre-attentive — they reduce cognitive load because
  the viewer doesn't need to decode them.
- Don't fight natural associations: using red for water creates confusion even
  if the legend explains it.

### Decorating

- Sparingly. Small areas only.
- Against a muted gray or neutral ground.
- The decorative color should never be more visually prominent than the data.

---

## Color Anti-Patterns

### Rainbow palette on continuous data

**Problem:** The rainbow (ROYGBIV) has non-monotonic perceptual luminance. The
eye perceives sharp apparent boundaries at the red-yellow transition and the
cyan-blue transition, even when the underlying data is smooth. These phantom
boundaries communicate false structure.

**Fix:** Sequential single-hue palette (e.g., light to dark blue) or a
perceptually uniform palette (viridis, cividis, magma).

### Equal-value complementary colors adjacent

**Problem:** Red placed next to green at equal lightness, or orange next to blue,
or yellow next to purple — creates the Albers vibration effect (apparent
shimmer at the boundary). The 1+1=3 interaction effect; the boundary generates
visual noise.

**The US Census map violation (EI, p. 82):** Adjacent saturated complementary
color regions vibrate visually, making the map unreadable.

**Fix:** Ensure adjacent colors differ in lightness, not just hue. Or separate
them with a neutral boundary or white space.

### Too many categories

**Problem:** Beyond 8–10 distinguishable categorical colors, the viewer cannot
reliably match legend entries to data. Categories become indistinguishable.

**Fix:** Reduce categories. Group minor categories into "Other." Use shape or
position to help differentiate. Or use small multiples with one category per
panel.

### Color as only differentiator

**Problem:** Some viewers have color vision deficiency. Red-green confusion
affects ~8% of male viewers.

**Fix:** Never use color as the _only_ encoding. Always pair color with shape,
position, or direct labeling. Ensure lightness contrast alone distinguishes
critical elements.

---

## Palette Types by Data Type

| Data type                            | Palette type | Example                         |
| ------------------------------------ | ------------ | ------------------------------- |
| Categorical, equal importance        | Qualitative  | ColorBrewer Set1, Set2          |
| Sequential quantitative (0 to max)   | Sequential   | Blues, Greens, viridis          |
| Diverging quantitative (− to 0 to +) | Diverging    | RdBu, PiYG                      |
| Highlighting one category            | Accent       | One saturated, rest gray        |
| Background / structural              | Neutral      | Light gray (#e0e0e0 or similar) |

---

## The Swiss Topographic Map Standard

The Matterhorn Swiss topographic map (EI, p. 80) demonstrates all four color
uses in harmony:

- **Label:** Water (blue) vs. stone (gray) — category distinction
- **Measure:** Elevation shading from light (valleys) to dark (peaks) — quantitative
- **Represent:** Glaciers (white/blue), vegetation (green) — natural associations
- **Decorate:** Overall harmony and aesthetic care

Strong colors appear only on small extreme areas (very high peaks, deep water
bodies). Large calm areas (slopes, fields) use muted tones. This is Imhof's
Rule 1 in practice: the whole map is readable because the decoration recedes
and lets the data lead.
