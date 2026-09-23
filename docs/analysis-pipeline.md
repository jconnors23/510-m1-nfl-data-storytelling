# Analysis pipeline

How to rebuild this 2024 record-vs-scoring ranking from a clone, and how the tables connect. Scripts live in `scripts/`. Findings live on the [analysis](record-vs-point-diff-analysis.md) page. Column meanings live on [feature engineering](feature-engineering.md).

A **record** like **15–2** means 15 wins and 2 losses. **Point differential** is points scored minus points allowed.

## End to end

Clone the repo, install packages, run the four scripts in order, then read the pages.

```mermaid
flowchart TD
  clone[Clone the repo] --> venv[python3 -m venv then pip install]
  venv --> pull["python scripts/pull_schedules.py"]
  pull --> games["data/nflverse_2024_reg_games.csv<br/>272 games"]
  games --> rank["python scripts/record_vs_diff.py"]
  rank --> table["data/2024_record_vs_diff.csv<br/>32 teams"]
  table --> charts["python scripts/record_vs_diff_charts.py"]
  table --> fmap["python scripts/engineered_features_chart.py"]
  charts --> pngs["figures/ scatter and bar"]
  fmap --> featpng["figures/engineered-features.png"]
  pngs --> analysis[docs/record-vs-point-diff-analysis.md]
  featpng --> featpage[docs/feature-engineering.md]
```

Source credit for the games file: [source citation](../data/source-citation.md).

## Grain: games to teams

Each extract row is one completed game (home points and visiting points). The ranking script copies that game twice so each team has a row, then adds the season up.

```mermaid
flowchart LR
  g["272 game rows"] --> tg["544 team-game rows<br/>in memory only"]
  tg --> t["32 team rows<br/>written to CSV"]
```

One example game:

```mermaid
flowchart TD
  game["Week 1: KC 30, SF 17"] --> kc["KC row: points_for 30, points_against 17, win, point_diff +13"]
  game --> sf["SF row: points_for 17, points_against 30, loss, point_diff -13"]
```

## Engineered columns

Season `point_diff` feeds the scoring ranking. Win percentage feeds the win ranking. The gap columns are built from those two places.

```mermaid
flowchart TD
  scores["Home and away final scores"] --> pd["point_diff<br/>scored minus allowed"]
  scores --> w["win / loss"]
  w --> wp["win_pct"]
  wp --> rwin["rank_win_pct<br/>1 = best record"]
  pd --> rpd["rank_point_diff<br/>1 = best margin"]
  rwin --> gap["rank_gap"]
  rpd --> gap
  gap --> mm["mismatch<br/>yes if gap is 6 or more"]
  rwin --> ahead["record_ahead_by<br/>scoring place minus win place"]
  rpd --> ahead
```

Kansas City 2024: `point_diff` +59, win ranking 1st, scoring ranking 11th, `rank_gap` 10, `mismatch` yes, `record_ahead_by` +10.

## How the pictures use those columns

```mermaid
flowchart TD
  table["32-team table"] --> scatter["Scatter: win percentage vs point_diff<br/>gray = rankings close, red = mismatch"]
  table --> bar["Bar: record_ahead_by for the five red teams"]
  table --> map["Feature chart: one row per column"]
```

Mean `rank_gap` across 32 teams is **2.9**. Median is **2.5**. The red flag is a gap of **6** or more.

## What to open after the scripts

```mermaid
flowchart TD
  scripts[Scripts finished] --> a[Analysis: story, five teams, ethics]
  scripts --> p[This page: diagrams]
  scripts --> f[Feature engineering: columns and worked example]
  scripts --> n[Notebook: same logic, no file writes]
```

**Also:** [README](../README.md) · [analysis](record-vs-point-diff-analysis.md) · [feature engineering](feature-engineering.md) · [source citation](../data/source-citation.md)
