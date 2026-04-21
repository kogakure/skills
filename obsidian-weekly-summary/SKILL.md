---
name: obsidian-weekly-summary
description: 'Summarize the current week from the Obsidian Zettelkasten daily notes. Reads all daily notes for the current calendar week (Monday through today) from the 06 Daily/ folder and produces a structured German-language summary of the most important things done: completed tasks, sport, learning, social events, media consumed, and highlights. Use whenever the user asks for a weekly review, weekly summary, "was habe ich diese Woche gemacht", "Wochenrückblick", "weekly recap", or wants to see what happened this week.'
allowed-tools: Bash(ls*), Read
---

# obsidian-weekly-summary

Read the daily notes for the current calendar week and produce a structured summary of the most important things done.

## Step 1: Determine the current week's dates

Use Python to calculate Monday–today:

```bash
python3 -c "
from datetime import date, timedelta
today = date.today()
monday = today - timedelta(days=today.weekday())
days = [monday + timedelta(days=i) for i in range((today - monday).days + 1)]
for d in days:
    print(d.strftime('%Y%m%d'), d.strftime('%A'))
"
```

The vault path for daily notes: `~/Code/personal/obsidian/zettelkasten/06 Daily/<YYYY>/<YYYYMMDD>.md`

## Step 2: Read each note that exists

For each date in the week, read the file if it exists. Skip missing files silently — the week may not be complete yet.

Read files directly with the Read tool (do not use bash cat).

## Step 3: Analyze the content

Each note has two sections:

**`## Aufgaben`** — tasks with checkboxes:

- `- [x]` = completed ✅
- `- [ ]` = not done (skip these in the summary)

**`## Notizen`** — bullet points with emoji prefixes. The key categories:

| Emoji | Category                           | Include?                                                              |
| ----- | ---------------------------------- | --------------------------------------------------------------------- |
| 🏃🏻‍♂️    | Running (Norwegian Protocol, etc.) | Yes — note duration and heart rate                                    |
| 💪    | Strength training                  | Yes — note exercise and sets                                          |
| 🚶‍♂    | Walking                            | Yes if notable (>30 min)                                              |
| 🎓    | Learning (Duolingo, Anki)          | Summarize totals per app across the week                              |
| ⌨️    | Keyboard practice (Colemak-DH)     | Summarize total time                                                  |
| 📺    | TV shows                           | Yes — list shows watched                                              |
| 📚    | Books                              | Yes — note title and progress %                                       |
| 🎬    | Movies                             | Yes                                                                   |
| 🎙️    | Podcasts                           | Only if something notable is mentioned; skip routine morning podcasts |
| 🛍️    | Shopping                           | Yes if notable                                                        |
| 🤩    | Highlights / notable moments       | Always include                                                        |
| 🩸    | Blood pressure                     | Skip                                                                  |
| 🛌    | Sleep                              | Skip (too routine)                                                    |
| 🩻    | Health/feeling                     | Include only if notable (illness, injury)                             |
| ☀️/🌧️ | Weather                            | Skip                                                                  |
| 🥐/🥗 | Food                               | Skip unless the entry is a meal out or social context                 |
| 🍪    | Snacks                             | Skip                                                                  |

**Freeform text entries** (no leading emoji, or with 🤩) are usually the most important — social events, notable experiences, decisions made. Always include these.

**Tasks with time/person context** (e.g., `[x] 12:00 Uhr – Mittagessen mit X`) count as social events.

## Step 4: Produce the summary

Write the summary in **German**, matching the language of the vault. Structure it as follows:

```
## Wochenrückblick: KW XX (DD. – DD. Monat YYYY)

### ✅ Aufgaben erledigt
- bullet per completed task (with day if helpful for context)

### 🏃 Sport & Fitness
- bullet per workout (type, duration, notable stats)

### 🎓 Lernen
- Duolingo: X Sprachen, ca. Y Minuten insgesamt
- Anki: ca. Z Karten, ca. Y Minuten insgesamt
- Colemak-DH: ca. Y Minuten insgesamt

### 👥 Soziales & Termine
- bullet per social event or notable appointment

### 📺 Medien
- 📺 TV: list shows + episodes
- 📚 Bücher: title + progress
- 🎬 Filme: titles

### ✨ Highlights
- bullet per notable moment, freeform text, or 🤩 entry

### 📝 Sonstige Notizen
- anything notable that doesn't fit above (shopping, health issues, etc.)
```

Omit any section that has no entries. Keep bullets concise — one line per item. For learning totals, add up minutes across all days.

If the week has only 1–2 days (e.g., it's Monday or Tuesday), note this naturally: "Die Woche hat gerade erst begonnen."
