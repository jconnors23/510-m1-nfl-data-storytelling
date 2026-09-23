# Feature engineering

Contract for transforming 2024 REG final scores into `data/2024_record_vs_diff.csv` (one row per club). Operational boundary: schema, grain, and derivations. Findings: [analysis](record-vs-point-diff-analysis.md). Runtime: [README](../README.md). Topology: [analysis pipeline](analysis-pipeline.md).

**Upstream:** nflverse schedules Release `games.csv` → `data/nflverse_2024_reg_games.csv` (`season == 2024`, `game_type == "REG"`, scores present). **Downstream:** season CSV; `scripts/record_vs_diff_charts.py`; `scripts/engineered_features_chart.py`. **Failure domain:** Release asset unreachable; `nfl.import_schedules()` (different host — this repo does not use it); null scores dropped at extract; post-aggregate `games ≠ 17`.

Each extract row is a completed game’s two point totals (`home_score`, `away_score`). Play-level box-score fields (yards, turnovers, individual stats) are out of scope. Season `point_diff`, record place (`rank_win_pct`), and scoring place (`rank_point_diff`) are compressions of that same 272-game extract. Opponent quality, injuries, and rest sit outside these columns.

```text
nflverse schedules Release
        │  scripts/pull_schedules.py
        ▼
272 game rows     data/nflverse_2024_reg_games.csv
        │  scripts/record_vs_diff.py
        ▼
544 team-game rows     (in memory only)
        │  summarize_season() + rank_min
        ▼
32 team-season rows     data/2024_record_vs_diff.csv
        │  scripts/record_vs_diff_charts.py
        │  scripts/engineered_features_chart.py
        ▼
figures/record-vs-diff.png
figures/win-ranking-ahead-of-scoring.png
figures/engineered-features.png
```

```bash
python scripts/pull_schedules.py
python scripts/record_vs_diff.py
python scripts/record_vs_diff_charts.py
python scripts/engineered_features_chart.py
```

## Extract identity

The schedules table is a **GitHub Release** asset, not a file on the [nflverse-data](https://github.com/nflverse/nflverse-data) `main` tree (that tree is automation).

| Attribute | Value |
| --- | --- |
| Release | https://github.com/nflverse/nflverse-data/releases/tag/schedules |
| Asset | https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv |
| License | [CC-BY-4.0](https://github.com/nflverse/nflverse-data/blob/master/LICENSE.md) |
| Cite | nflverse (Carl, Baldwin, and the nflverse team) |

`scripts/pull_schedules.py` downloads historical `games.csv` and retains one completed REG season. **Verify:** 272 games, weeks 1–18, 32 clubs. Credit: [source citation](../data/source-citation.md). Grain is **game**, not standings.

## Grain: 272 games → 544 team-games → 32 team-seasons

The extract names two clubs on one line. There is no `team` column, so `groupby("team")` is undefined until an unpivot.

`WHEN` a game row names two clubs `THE SYSTEM SHALL` emit two team-game rows (`games_to_team_rows`). Worked game — week 1, KC 30, SF 17:

| week | home_team | away_team | home_score | away_score |
| --- | --- | --- | --- | --- |
| 1 | KC | SF | 30 | 17 |

| Field | KC row | SF row | Derivation |
| --- | --- | --- | --- |
| `week` | 1 | 1 | Copy |
| `team` | KC | SF | `home_team` / `away_team` |
| `points_for` (PF) | 30 | 17 | `home_score` / `away_score` |
| `points_against` (PA) | 17 | 30 | Opponent score |
| `win` | 1 | 0 | `1[PF > PA]` |
| `loss` | 0 | 1 | `1[PF < PA]` |
| `point_diff` | +13 | −13 | `PF − PA` (not in the nflverse file) |

**INVARIANT:** this extract has no ties (`win + loss = 1` per team-game). A 30–17 result and a 17–16 result are both wins; only per-game `point_diff` distinguishes them. Home/away encode venue, not conference.

| Grain | n | Persistence | Role |
| --- | --- | --- | --- |
| Game | 272 | `data/nflverse_2024_reg_games.csv` | Extract |
| Team-game | 544 | Memory only | Per-game `point_diff`, `win`, `loss` |
| Team-season | 32 | `data/2024_record_vs_diff.csv` | Totals, places, mismatch |

`summarize_season` aggregates every team-game. **INVARIANT:** `games = 17` for all 32 clubs (18 calendar weeks, one unplayed week per club).

- `games` = `COUNT` team-games
- `wins` / `losses` = `SUM(win)` / `SUM(loss)`
- season `point_diff` = `SUM` of per-game `point_diff`
- `win_pct` = `wins / games`

Places use pandas `rank(..., method="min")`, `1` = best. Tied `win_pct` shares a place (two 15–2 clubs both 1st; next integer is 3rd). Same tie rule on `point_diff`.

```text
rank_gap          = |rank_win_pct − rank_point_diff|
mismatch          = rank_gap ≥ 6     (MISMATCH_RANK_GAP)
record_ahead_by   = rank_point_diff − rank_win_pct
```

Threshold 6 is ≈ one fifth of a 32-club league: 1–2 place noise is ignored. `record_ahead_by > 0` ⇒ record place is numerically better (smaller) than scoring place.

### Worked values — KC 2024 vs DET 2024

- KC 15–2 → `rank_win_pct = 1` (tied with DET). `point_diff = +59` → `rank_point_diff = 11`. `rank_gap = |1 − 11| = 10` → `mismatch = true`. `record_ahead_by = 11 − 1 = +10`.
- DET 15–2, `point_diff = +222` → `rank_point_diff = 1`. Places agree → `mismatch = false`.

Implementation: `build_season_table` in `scripts/record_vs_diff.py`. Replica (no writes): [2024 ranking walkthrough](../notebooks/2024-ranking-walkthrough.ipynb).

## Data dictionary

`data/2024_record_vs_diff.csv`: 32 rows. Place `1` = best. KC 2024 is the worked example on [engineered-features.png](../figures/engineered-features.png). Plot-time fields are not persisted.

| Column | Type | Derivation | Nullable | Persistence | Description | KC 2024 |
| --- | --- | --- | --- | --- | --- | --- |
| `team` | string | Unpivot identity | No | CSV | nflverse club code | KC |
| `games` | int | `COUNT` team-games | No | CSV | REG games played | 17 |
| `wins` | int | `SUM(win)` | No | CSV | Wins | 15 |
| `losses` | int | `SUM(loss)` | No | CSV | Losses | 2 |
| `point_diff` | float | `SUM(PF − PA)` | No | CSV | Season scoring margin | +59 |
| `win_pct` | float | `wins / games` | No | CSV | Win rate ∈ `[0, 1]` | 15/17 |
| `rank_win_pct` | int | `rank_min(win_pct, desc)` | No | CSV | Record place | 1st of 32 |
| `rank_point_diff` | int | `rank_min(point_diff, desc)` | No | CSV | Scoring place | 11th of 32 |
| `rank_gap` | int | `\|rank_win_pct − rank_point_diff\|` | No | CSV | Absolute place split | 10 |
| `mismatch` | bool | `rank_gap ≥ 6` | No | CSV | Flag; `MISMATCH_RANK_GAP = 6` | true |
| `record_ahead_by` | int | `rank_point_diff − rank_win_pct` | No | CSV | `> 0` ⇒ record place ahead of scoring place | +10 |
| `win_percent` | float | `win_pct × 100` | — | Plot only | Scatter x-axis | — |
| `record` | string | `"{wins}–{losses}"` | — | Plot only | Record as text | `15–2` |
| `label` | string | `"{team}  {record}"` | — | Plot only | Bar-axis label | `KC  15–2` |

`win_pct` feeds `rank_win_pct`. Per-game `point_diff` is built in memory, then summed to the season total used on the feature chart.

## Out of contract

These omissions are constraints on what the two places can mean, not backlog.

| Left out | Rationale |
| --- | --- |
| Opponent-adjusted margin | Extract is schedules + scores only. `point_diff` is unweighted across opponents and has no per-play efficiency. |
| Mid-season or rest-of-season cut | One ranking of the finished 17-game REG season; not a forecast. |
| Pre-game feature table | Not a next-game prediction model. |
| Rest between games | Rest fields exist on the extract; this ranking does not consume them. |
| Play-by-play, injuries, weather, coaching | Outside the extract. Strength is not identified by `win_pct` or `point_diff` alone. |

**Also:** [analysis](record-vs-point-diff-analysis.md) · [analysis pipeline](analysis-pipeline.md) · [README](../README.md) · [walkthrough](../notebooks/2024-ranking-walkthrough.ipynb)
