# iA Presenter Theme Guide

## Applying a Theme

In iA Presenter: Inspector → Design Tab → Theme dropdown.

Each theme has Light and Dark variants, selectable via the Colors section.

---

## Built-in Themes

### New York

**Style:** Bold, modern, opinionated
**Font:** Inter
**Palette:** Yellow/black, varied headline sizes
**Best for:** Tech companies, startups, product launches, keynotes
**Mood:** Assertive, contemporary, high-contrast

### Basel

**Style:** Typographic, clean
**Font:** Noto Serif
**Palette:** White on black (default), simple color backgrounds
**Best for:** Corporate presentations, formal reports, publishing
**Mood:** Serious, authoritative, editorial

### San Francisco

**Style:** Vibrant, bold
**Font:** System font
**Palette:** Colorful, different headline sizes
**Best for:** Startup pitches, consumer products, creative agencies
**Mood:** Energetic, optimistic, modern

### LA

**Style:** Loud, dynamic
**Font:** Display font
**Palette:** Dynamic color backgrounds, high saturation
**Best for:** Entertainment, marketing, bold creative work
**Mood:** Dramatic, expressive, attention-grabbing

### Copenhagen

**Style:** Nordic minimal, elegant
**Font:** Clean sans-serif
**Palette:** Soft pastels, simple backgrounds
**Best for:** Design studios, UX/product, Scandinavian aesthetic
**Mood:** Calm, refined, sophisticated

### Vancouver

**Style:** Clean, dynamic
**Font:** Montserrat
**Palette:** Dynamic color backgrounds
**Best for:** Professional services, healthcare, education
**Mood:** Approachable, trustworthy, fresh

### Tokyo

**Style:** Gradient, vibrant
**Font:** Display
**Palette:** Top-to-bottom Metro line gradients
**Best for:** Creative tech, gaming, youth audiences
**Mood:** Energetic, dynamic, contemporary Japanese aesthetic

### Milano

**Style:** Fashion-forward, luxurious
**Font:** Elegant serif/sans
**Palette:** Sophisticated, restrained
**Best for:** Fashion, luxury goods, premium brands, design presentations
**Mood:** Stylish, exclusive, polished

### Zurich

**Style:** Swiss International, minimal
**Font:** Helvetica-adjacent
**Palette:** Neutral, functional
**Best for:** Academic presentations, data-heavy content, technical talks
**Mood:** Objective, rigorous, timeless

### Paris

**Style:** Classic, editorial
**Font:** Elegant
**Palette:** Alternating color backgrounds
**Best for:** Cultural institutions, journalism, humanities
**Mood:** Refined, cultured, sophisticated

### Helvetica

**Style:** Swiss typographic
**Font:** Helvetica
**Palette:** Strong, clean
**Best for:** Design history, typography-focused talks, graphic design
**Mood:** Classic, disciplined, authoritative visual hierarchy

### Garamond

**Style:** Renaissance, premium
**Font:** Garamond
**Palette:** Warm, elegant
**Best for:** Literature, history, philosophy, premium brand storytelling
**Mood:** Timeless, scholarly, refined

---

## Quick Recommendation Guide

| Context              | Recommended Theme         |
| -------------------- | ------------------------- |
| Tech startup pitch   | New York or San Francisco |
| Enterprise / B2B     | Basel or Zurich           |
| Design portfolio     | Copenhagen or Milano      |
| Product launch       | New York or San Francisco |
| Academic/research    | Zurich or Garamond        |
| Creative/agency      | LA or Tokyo               |
| Premium/luxury brand | Milano or Garamond        |
| Education/training   | Vancouver or Copenhagen   |
| Cultural/arts        | Paris or Helvetica        |
| Data/analytics       | Zurich or Basel           |

---

## Light vs. Dark

- **Dark mode** — Higher contrast, more dramatic; good for dimly lit conference rooms and stage presentations
- **Light mode** — More readable in bright rooms; better for printed handouts; feels more corporate/formal

When uncertain, dark mode is generally more visually impactful on a projector.

---

## Custom Themes

Advanced users can create custom themes using HTML and CSS via Settings → Themes → +.
Custom themes are stored locally and appear at the bottom of the theme list.
Requires knowledge of CSS and iA Presenter's layout class system.

Layout CSS classes for custom themes:

| Layout      | Container                | Content               |
| ----------- | ------------------------ | --------------------- |
| Cover       | `.cover-container`       | `.layout-cover`       |
| Title       | `.title-container`       | `.layout-title`       |
| Section     | `.section-container`     | `.layout-section`     |
| Split       | `.v-split-container`     | `.layout-v-split`     |
| Grid        | `.grid-container`        | `.layout-grid`        |
| Caption     | `.caption-container`     | `.layout-caption`     |
| Image Title | `.title-image-container` | `.layout-title-image` |
| Default     | `.default-container`     | `.layout-default`     |
