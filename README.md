# 2024 NFL Record vs. Point Differential

### 📊 Read the full write-up: **[jconnors23.github.io/510-m1-nfl-data-storytelling](https://jconnors23.github.io/510-m1-nfl-data-storytelling/)**
### 🎥 Watch the presentation: **[youtu.be/sqv3Oi22v5w](https://youtu.be/sqv3Oi22v5w?si=4DbluZcx6Qlugwai)**
### 🤖 How AI was used: **[design manifest](design-manifest.md)**

Win–loss record and point differential (total points scored minus total points allowed) are two standard measures of a football team's season, and they can rank the same team quite differently. This project ranks all 32 teams by each measure for the 2024 regular season and identifies the five teams whose rankings differ by at least six places. Kansas City, for instance, ranked 1st by record (15–2) but 11th by point differential (+59). The conclusion is straightforward: on its own, neither measure fully captures how good a team was.

## Documentation

The **[live documentation site](https://jconnors23.github.io/510-m1-nfl-data-storytelling/)** is the best way to read this project. The same pages live in [`docs/`](docs/index.md) and read in this order:

1. [Project overview](docs/index.md)
2. [Data preparation & feature engineering](docs/feature-engineering.md)
3. [Reproduction pipeline](docs/reproduction-pipeline.md) — the exact commands to rebuild the data and charts
4. [Exploratory data analysis](docs/exploratory-data-analysis.md)
5. [Conclusions](docs/conclusions.md)

The [2024 ranking walkthrough notebook](notebooks/2024-ranking-walkthrough.ipynb) runs the same steps cell by cell.

## Building the Docs Site

The site is built with [MkDocs](https://www.mkdocs.org/) and the Material theme, and deploys automatically to GitHub Pages on every push to `main` via `.github/workflows/docs.yml`. To preview it locally:

```bash
pip install mkdocs-material
mkdocs serve          # http://127.0.0.1:8000
```

## Details

- **Requires** Python 3.11 or newer; dependencies are pinned in `requirements.txt`.
- **Produces** `data/processed/2024_record_vs_diff.csv` (32 teams) and the chart PNGs in `data/figures/`.
- **Scope:** the 2024 regular season only — 272 games, 32 teams, 17 games each.

## Data Source

nflverse schedules release, `games.csv` — <https://github.com/nflverse/nflverse-data/releases/tag/schedules>. License CC-BY-4.0; cite nflverse (Carl, Baldwin, and the nflverse team). Credit next to the data: [data/source-citation.md](data/source-citation.md).
