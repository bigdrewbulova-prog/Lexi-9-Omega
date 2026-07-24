# Import Lexi hackathon calendar into Notion

## Files
- **CSV:** `lexi-hackathon-content-calendar.csv` (this folder)
- **Playbook:** `hackathon-content-playbook.md`
- **Copy bank:** `social-post-bank.md`

## Dates in the CSV
Sample timestamps assume:

| Phase | Calendar dates (edit these) |
|---|---|
| T−3 | 2026-08-01 |
| T−2 | 2026-08-02 |
| T−1 | 2026-08-03 |
| Hackathon day 1 | 2026-08-04 |
| Hackathon day 2 | 2026-08-05 |
| D+1 | 2026-08-06 |
| D+2 | 2026-08-07 |
| D+3 | 2026-08-08 |

**Shift all `scheduled_at_iso` values** to match your real hackathon weekend.  
`day_offset`: −3…−1 pre · 0–1 during · 1–3 post.

## Notion import steps
1. Open Notion → **Import** → **CSV**.
2. Select `lexi-hackathon-content-calendar.csv`.
3. Confirm first row is column names.
4. After import, set property types:

| Column | Notion type |
|---|---|
| `id` | Title (or Text) |
| `phase` | Select (`pre` / `during` / `post`) |
| `day_offset` | Number |
| `slot` | Select |
| `local_time` | Text |
| `scheduled_at_iso` | Date (include time) |
| `platform` | Multi-select or Text |
| `post_type` | Select |
| `theme` | Multi-select |
| `title` | Text (or Title if `id` is Text) |
| `body` | Text (long) |
| `media` | Text |
| `poll_options` | Text (`|` separated) |
| `hashtags` | Text |
| `tags_mentions` | Text |
| `cta_demo` / `cta_repo` / `cta_feedback` | URL |
| `status` | Select (`planned` / `drafted` / `posted` / `skipped`) |
| `owner` | Person or Text |
| `notes` | Text |

5. Add a **Board** view grouped by `status` or `phase`.  
6. Add a **Calendar** view on `scheduled_at_iso`.  
7. Replace `{DEMO_URL}`, `{REPO_URL}`, `{FORM_URL}`, `{ORGANIZER}`, etc.

## Google Sheets / Excel
Open the CSV directly; use Data → Split text if needed.  
Filter by `phase` = `during` for the 48h sprint board.

## Counts
| Phase | Posts |
|---|---:|
| Pre | 6 |
| During | 12 |
| Post | 4 |
| **Total** | **22** |

During-phase volume ≈ 6/day over 48h (matches 4–6 real-time posts/day with room to skip sleep slots).
