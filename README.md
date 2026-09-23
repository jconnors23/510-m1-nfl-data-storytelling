# 2024 NFL records vs point differential

This repository looks at every completed **2024 NFL regular-season** game and asks what happens when a team's **win–loss record** and its **point differential** (points scored minus points allowed) tell different stories.

Team strength is multi-faceted: schedule, injuries, close games, and late scores all sit outside a single column. Record and point differential are two summaries of the same 17 games.

You will find two charts, a short analysis of the teams whose rankings diverged, and the scripts that rebuild the whole pipeline from the nflverse schedules release.

## Who this is for

This repo is for **readers new to football**, and for anyone who ranks with a single column — a record, a score, a leaderboard. Rankings show up in sports, school lists, and product metrics. The 2024 season is a concrete case of **two honest summaries of the same 272 games disagreeing**.

## League basics

The **NFL** is the top professional American football league in the United States (**32 teams**). Plays and positions are not required to read this repo.

- Team codes like **KC** and **DET** are short names (Kansas City, Detroit).
- A **record** written **15–2** means **15 wins and 2 losses**.
- The **regular season** is the main schedule before the playoffs (the postseason tournament). It lasts **18 calendar weeks**. Each team gets one week off (a **bye**) and plays **17 games**.
- Each completed game in the data is one row with a **final score**: how many points the home team scored and how many the visiting team scored. Sports pages often call that summary a **box score**. This project uses those two point totals.
- **Home** is the team whose stadium hosted the game; **away** is the visitor.
- **Point differential** is points scored minus points allowed, added up over those 17 games.

## Contents

1. [Who this is for](#who-this-is-for)
2. [League basics](#league-basics)
3. [What the 2024 season shows](#what-the-2024-season-shows)
4. [How to read the charts](#how-to-read-the-charts)
5. [Where to go next](#where-to-go-next)
6. [What's in the repo](#whats-in-the-repo)
7. [Reproduce](#reproduce)
8. [Data](#data)

## What the 2024 season shows

Record and point differential are two summaries of the same 17 games. The **margin** of those games can sit far from the record. When the two rankings mismatch, the season looks different depending on which summary you open. Team strength depends on more than either column.

Over the full 2024 regular season, five teams landed in a very different **win ranking** than **scoring ranking**. Kansas City finished **15–2** (15 wins, 2 losses) — the same record as Detroit — but only 11th in scoring. Houston went 10–7 with a **0 point differential**. Carolina's record was already poor; the scoring margin was worse.

Those two rankings **mismatch** when they are **at least 6 spots** apart.

## How to read the charts

Each dot is one team's regular season. Teams toward the **right** won a larger share of their games. Teams toward the **top** outscored opponents by more. **Gray** dots are teams whose win ranking and scoring ranking were similar. **Red** dots are the mismatch cases: those two rankings are at least six spots apart. Each named label shows the record, then both ranks among 32 teams (for example, 1st of 32 in record and 11th of 32 in scoring ranking).

![Scatter: 2024 win percentage vs point differential. Gray = similar win ranking and scoring ranking. Red = those rankings at least six spots apart.](figures/record-vs-diff.png)

The bar chart isolates those five red teams. A longer bar means the win ranking sat further ahead of the scoring ranking. Kansas City's 15–2 ranked 1st by wins and 11th by scoring (**+10 ranking spots**).

![Horizontal bars: how far each mismatch team's win ranking sat ahead of its scoring ranking.](figures/win-ranking-ahead-of-scoring.png)

For how to read both pictures, the five-team table, and the limits of this ranking, open the [analysis](docs/record-vs-point-diff-analysis.md).

## Where to go next

Read these in order. The notebook is optional — it walks through the same ranking and chart logic.

| Step | Open | What you will find |
| --- | --- | --- |
| 1 | **[Analysis](docs/record-vs-point-diff-analysis.md)** | The story: mismatch rule, five teams, charts, and ethics |
| 2 | **[Analysis pipeline](docs/analysis-pipeline.md)** | End-to-end diagrams: scripts, grains, columns |
| 3 | **[Feature engineering](docs/feature-engineering.md)** | How 272 games become the 32-team ranking |
| 4 | **[Notebook](notebooks/2024-ranking-walkthrough.ipynb)** | A contained copy of the ranking and chart logic (kernel **Python (510-m1)**) |

## What's in the repo

Five folders. That is the whole GitHub tree.

| Folder | What it holds |
| --- | --- |
| `scripts/` | Pull the extract, build the ranking, write the PNGs |
| `data/` | Games CSV, 32-team table, citation |
| `figures/` | Scatter, mismatch bar, feature chart |
| `docs/` | Analysis, feature engineering, and pipeline diagrams |
| `notebooks/` | Optional walkthrough (same logic as the scripts) |

Run the scripts in this order:

| Order | Path | What it is |
| --- | --- | --- |
| 1 | `scripts/pull_schedules.py` | Download the nflverse extract |
| 2 | `data/nflverse_2024_reg_games.csv` | 272 completed 2024 regular-season games |
| 3 | `scripts/record_vs_diff.py` | Build the 32-team ranking |
| 4 | `data/2024_record_vs_diff.csv` | One row per team: record, point differential, mismatch |
| 5 | `scripts/record_vs_diff_charts.py` | Write the scatter and bar PNGs |
| 6 | `scripts/engineered_features_chart.py` | Write the one-column feature chart |

Tooling on this machine (`.venv`, MkDocs, working drafts) is gitignored. It does not ship to GitHub.

## Reproduce

Run the scripts in the same order as the table above:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/pull_schedules.py
python scripts/record_vs_diff.py
python scripts/record_vs_diff_charts.py
python scripts/engineered_features_chart.py
```

## Data

The extract comes from the nflverse schedules GitHub Release (CC-BY-4.0). Cite nflverse (Carl, Baldwin, and the nflverse team).

- Release: https://github.com/nflverse/nflverse-data/releases/tag/schedules
- File: `https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv`

The source citation next to the extract is [data/source-citation.md](data/source-citation.md).
