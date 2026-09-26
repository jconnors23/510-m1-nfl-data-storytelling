---
hide:
  - toc
---

# Project Overview

### 🎥 Watch the presentation: **[youtu.be/sqv3Oi22v5w](https://youtu.be/sqv3Oi22v5w?si=4DbluZcx6Qlugwai)**
### 💻 Code and data: **[GitHub repository](https://github.com/jconnors23/510-m1-nfl-data-storytelling)**
### 🤖 How AI was used: **[design manifest](https://github.com/jconnors23/510-m1-nfl-data-storytelling/blob/main/design-manifest.md)**

Win–loss record and point differential (total points scored minus total points allowed) are two standard measures of a football team's season. This project ranks all 32 teams by each measure for the 2024 regular season and identifies the teams whose two rankings differ by at least six places. The conclusion is straightforward: on its own, neither measure fully captures how good a team was.

This is the documentation site. The pages below carry the exploratory data analysis (EDA), the engineered features, and the story the data tells; the [GitHub repository](https://github.com/jconnors23/510-m1-nfl-data-storytelling) has the code, the data, and the commands to run it.

## Audience and Motivation

The audience is anyone who reads or repeats NFL standings — fans, writers, and analysts — plus students learning to question a single summary statistic. Records are quoted constantly ("they were 15–2!") as if a record alone settles how good a team was. This project shows, with one full season of data, that **a team can rank near the top by record and only in the middle by point differential** — the two rankings place the same team many spots apart — so a careful reader should look at both. It is a small, honest example of using exploratory data analysis to check a claim people take for granted.

## Dataset and Topic

Every completed 2024 regular-season game and its final score, from the public nflverse schedules data (see the [source citation](../data/source-citation.md)). The topic is narrow on purpose: compare each team's win–loss record with its season point differential, and study where the two diverge.

## How the Data Flows

```mermaid
flowchart TD
  rel["nflverse schedules release<br/>(games.csv)"] -->|pull_schedules.py| games["data/raw/nflverse_2024_reg_games.csv<br/>272 games"]
  games -->|record_vs_diff.py| table["data/processed/2024_record_vs_diff.csv<br/>32 teams"]
  table -->|record_vs_diff_charts.py| charts["data/figures/<br/>scatter, dumbbell, gap distribution"]
  table -->|engineered_features_chart.py| feat["data/figures/<br/>feature chart"]
```

## Pages, in Reading Order

| Page | What it covers |
| --- | --- |
| [Data preparation & feature engineering](feature-engineering.md) | The steps from games to teams, the column reference, the math |
| [Reproduction pipeline](reproduction-pipeline.md) | Diagrams of the full flow |
| [Exploratory data analysis](exploratory-data-analysis.md) | The five mismatch teams, what the charts show, what the numbers can't tell you |
| [Conclusions](conclusions.md) | The short version and how to use it |

## Key Facts

32 teams; 18 weeks; 17 games per team (one week off); 272 completed regular-season games. Team codes (KC, DET, …) are nflverse abbreviations. A record `15–2` is 15 wins and 2 losses.

Data source and license: [source citation](../data/source-citation.md) (nflverse schedules release, CC-BY-4.0).
