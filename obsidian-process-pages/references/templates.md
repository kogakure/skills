# Templates & destination folders

Source of truth: `99 Meta/templates/` in the vault. Only `Daily Template.md` uses
Templater syntax — every template below has **static** frontmatter. Field order matters:
rebuild frontmatter in exactly this order, keeping any extra pre-existing fields (aliases,
tags, related, urls values) but dropping fields not in the template.

Always: preserve `created` verbatim as found. Set `updated` to now (`YYYY-MM-DDTHH:MM`).

## Note → `04 Permanent/`

```
type, created, updated, aliases, tags, urls, related, authors, sources, year, reference
```

## Quote → `03 Resources/Zitate/`

```
type, created, updated, aliases, tags (- Zitat), urls, related, authors, publication,
sources, published, language, position, year, reference
```

## Book → `03 Resources/Bücher/`

```
type, created, updated, aliases, tags (- Buch), photo, urls, published, authors,
genres, rating, pages, reference
```

## Movie → `03 Resources/Filme/`

```
type, created, updated, aliases, reference, tags (- Film), photo, urls, year,
directors, actors, genres, rating, IMDb rating
```

## TV Show → `03 Resources/Serien/`

```
type, created, updated, aliases, reference, tags (- TV-Show), urls, related, photo,
directors, actors, genres, rating, IMDb rating, network, started, ended, seasons, episodes
```

## Person → `03 Resources/Personen/`

```
type, created, updated, aliases, tags, photo, urls, related, birthday, death,
location, quotes, books, articles, podcasts, videos
```

## Podcast → `03 Resources/Podcasts/`

```
type, created, updated, aliases, reference, tags, photo, urls, hosts, guests,
genres, language, rating, status, started, ended, episodes
```

## Country → `03 Resources/Länder/`

```
type, created, updated, aliases, tags (- Land), urls, related, capital, continent,
language, currency, photo, visited, rating, cities
```

## City → `03 Resources/Städte/`

```
type, created, updated, aliases, tags (- Stadt), urls, related, country, region,
language, photo, visited, rating
```

## Place → `03 Resources/Orte/`

```
type, created, updated, aliases, tags (- Ort), urls, related, visited, photo,
city, country, category, address, location, rating
```

## Company → `03 Resources/Firmen/`

```
type, created, updated, aliases, tags, urls, related, photo, category, rating,
visited, place, address, zip, city, location, telephone, email
```

## Product → `03 Resources/Produkte/`

```
type, created, updated, aliases, tags, photo, urls, related, manufacturer, product,
date of acquisition, abolition date, price, rating
```

## Lyrics → `03 Resources/Lyrics/`

```
type, created, updated, aliases, tags (- Lyrics), urls, related, authors, album,
year, language, song, reference
```

## Prompt → `03 Resources/Prompts/`

```
type, created, updated, aliases, tags (- Prompt), urls, related, authors, sources,
model, version, purpose, use case
```

## Trip → `03 Resources/Reisen/`

```
type, created, updated, aliases, tags (- Reise), urls, related, photo, startdate,
enddate, country, cities, places, companions, rating
```

## Literature Note → `03 Resources/Literatur Notes/`

```
type, created, updated, aliases, tags, urls, related, authors, publication,
sources, reference, completed
```

Body starts with `## Zusammenfassung` and `## Notizen` headers if not already present —
but do not fabricate content, only keep what exists.

## Field-value conventions

- `authors`: list of `[[Wikilink]]`.
- `sources`: plain string (list), never a wikilink — strip `[[...]]` brackets if present.
- `publication`: `[[Wikilink]]` (Quote / Literature Note only).
- `urls`: list of bare URLs (no angle brackets).
- `reference`: list of footnote ids (e.g. `henderson2021bf`).
- `published`: `YYYY-MM-DD`, only when year+month+day are all known; otherwise omit the field.
- `year`: bare year number/string.
