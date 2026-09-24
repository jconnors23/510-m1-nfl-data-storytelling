---
hide:
  - toc
---

# Reproduction Pipeline

The full path to reproduce the 2024 record-versus-point-differential project, shown as diagrams. For the column details, see [data preparation and feature engineering](feature-engineering.md). For what the results mean, see the [exploratory data analysis](exploratory-data-analysis.md). For the exact commands, see the [README](../README.md). For the data credit, see the [source citation](../data/source-citation.md).

The path has four scripts: `pull_schedules.py` downloads the games, `record_vs_diff.py` builds the 32-team table, `record_vs_diff_charts.py` draws the three main charts, and `engineered_features_chart.py` draws the feature chart.

## End-to-End Reproduction

Clone the repository, install the packages, run the scripts in order, then read the pages. Two scripts build the data (download, then table) and two draw the charts.

**Run environment:** Python 3.11 or newer (the published-site build uses 3.13). The package versions are pinned in `requirements.txt` — pandas, matplotlib, seaborn, and ipykernel for the notebook. No other system tools are needed; the games file downloads over HTTPS from the nflverse release.

```mermaid
flowchart TD
  clone[Clone the repo] --> venv[python3 -m venv then pip install]
  venv --> pull["python scripts/pull_schedules.py"]
  pull --> games["data/raw/nflverse_2024_reg_games.csv<br/>272 games"]
  games --> rank["python scripts/record_vs_diff.py"]
  rank --> table["data/processed/2024_record_vs_diff.csv<br/>32 teams"]
  table --> charts["python scripts/record_vs_diff_charts.py"]
  table --> fmap["python scripts/engineered_features_chart.py"]
  charts --> pngs["data/figures/ scatter, dumbbell, gap distribution"]
  fmap --> featpng["data/figures/engineered-features.png"]
  pngs --> analysis[docs/exploratory-data-analysis.md]
  featpng --> featpage[docs/feature-engineering.md]
```

Credit for the games file: [source citation](../data/source-citation.md).

## From Games to Teams, at a Glance

This page shows the flow as diagrams. For how each step works and why — the game-doubling, the tie-sharing rankings, the worked Kansas City example, and the full column reference — see [data preparation and feature engineering](feature-engineering.md); it is not repeated here.

The scores go through three shapes: one row per game, one row per team-game (in memory), one row per team (saved).

```mermaid
flowchart LR
  g["272 game rows"] --> tg["544 team-game rows<br/>in memory only"]
  tg --> t["32 team rows<br/>saved to CSV"]
```

From the saved scores, season `point_diff` drives the point-differential ranking and win percentage drives the record ranking; the gap columns come from those two rankings.

```mermaid
flowchart TD
  scores["Home and away final scores"] --> pd["point_diff<br/>scored minus allowed"]
  scores --> w["win / loss"]
  w --> wp["win_pct"]
  wp --> rwin["rank_win_pct<br/>1 = best record"]
  pd --> rpd["rank_point_diff<br/>1 = best point differential"]
  rwin --> gap["rank_gap"]
  rpd --> gap
  gap --> mm["mismatch<br/>yes if gap is 6 or more"]
  rwin --> ahead["record_ahead_by<br/>point-differential ranking minus record ranking"]
  rpd --> ahead
```

## Which Columns Each Chart Uses

```mermaid
flowchart TD
  table["32-team table"] --> scatter["Scatter: win percentage vs point_diff<br/>gray = similar place on both lists, red = mismatch"]
  table --> bar["Dumbbell: both rankings for the five red teams"]
  table --> gap["Gap distribution: how many teams sit at each rank_gap"]
  table --> map["Feature chart: one row per column"]
```

Across all 32 teams the average `rank_gap` is **2.9** and the middle value is **2.5**. The mismatch cutoff is a gap of **6** or more.

**See also:** [data preparation and feature engineering](feature-engineering.md) · [exploratory data analysis](exploratory-data-analysis.md) · [conclusions](conclusions.md) · [README](../README.md) · [source citation](../data/source-citation.md)
