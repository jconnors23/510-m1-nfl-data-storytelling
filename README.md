# 2024 NFL Record vs. Point Differential

There are two common ways to sum up a football team's season: its win–loss record, and its point differential (points scored minus points allowed). This project ranks all 32 teams both ways for 2024 and finds the teams that rank in very different places on the two lists — for example, Kansas City ranked 1st by record (15–2) but 11th by point differential (+59). A team is a `mismatch` when it ranks at least 6 places apart on the two lists. The single takeaway: neither number, on its own, tells you how good a team really was.

- **Comes from:** the nflverse schedules release (`games.csv`, CC-BY-4.0) — see [source citation](data/source-citation.md).
- **Produces:** `data/processed/2024_record_vs_diff.csv` (32 rows) and five PNGs under `data/figures/`.

The work splits into the usual stages: **preprocessing** (download and clean the games), **feature engineering** (build each team's rankings and the gap between them), and **exploratory data analysis (EDA)** (chart the season and read what stands out). The [docs site](docs/index.md) walks through each stage.

Facts used across the docs: 32 teams; 18 weeks; 17 games per team (one week off); 272 completed regular-season games. Team codes (KC, DET, …) are nflverse abbreviations. A record `15–2` is 15 wins and 2 losses.

## Dataset

| | Raw | Cleaned |
| --- | --- | --- |
| File | `data/raw/nflverse_2024_reg_games.csv` | `data/processed/2024_record_vs_diff.csv` |
| Each row is | one game (272 rows) | one team (32 rows) |
| How to make it | `python scripts/pull_schedules.py` | `python scripts/record_vs_diff.py` |
| Contents | every 2024 regular-season game and its final score | each team's record, point differential, both rankings, and the mismatch flag |

The raw file is the nflverse schedules download narrowed to 2024 regular-season games that were played (`season == 2024`, regular season, final scores present). The cleaned file is the per-team table this project analyzes. Both are small and checked in; if you'd rather regenerate them, run the two commands above. Full field-by-field detail is on [data preparation & feature engineering](docs/feature-engineering.md).

## How the Data Flows

```text
nflverse schedules release  (games.csv)
        │  scripts/pull_schedules.py
        ▼
data/raw/nflverse_2024_reg_games.csv           272 games
        │  scripts/record_vs_diff.py
        ▼
data/processed/2024_record_vs_diff.csv         32 teams
        │  scripts/record_vs_diff_charts.py
        │  scripts/engineered_features_chart.py
        ▼
data/figures/record-vs-diff-augmented.png   (all teams labeled — docs/handout)
data/figures/record-vs-diff-slide.png       (callouts only — projected slide)
data/figures/record-ahead-dumbbell.png
data/figures/rank-gap-distribution.png
data/figures/engineered-features.png
```

What the charts mean is covered in the [exploratory data analysis](docs/exploratory-data-analysis.md), not here:

![Scatter: every team by win percentage and point differential, with the four quadrants shaded and named.](figures/record-vs-diff-augmented.png)
![Dumbbell: where each mismatch team ranks by record versus by point differential.](figures/record-ahead-dumbbell.png)

## Files

```text
scripts/          pull_schedules.py · record_vs_diff.py · record_vs_diff_charts.py · engineered_features_chart.py
data/raw/         nflverse_2024_reg_games.csv
data/processed/   2024_record_vs_diff.csv
data/figures/     record-vs-diff-augmented.png · record-vs-diff-slide.png · record-ahead-dumbbell.png
                  rank-gap-distribution.png · engineered-features.png
data/             source-citation.md
docs/             index.md · feature-engineering.md · reproduction-pipeline.md · exploratory-data-analysis.md · conclusions.md
notebooks/        2024-ranking-walkthrough.ipynb   (runs the same steps; writes no files)
```

| Order | Path | What it does |
| --- | --- | --- |
| 1 | `scripts/pull_schedules.py` | Download the 2024 regular-season games |
| 2 | `data/raw/nflverse_2024_reg_games.csv` | 272 game rows |
| 3 | `scripts/record_vs_diff.py` | Build the team table and flag mismatches |
| 4 | `data/processed/2024_record_vs_diff.csv` | 32 team rows |
| 5 | `scripts/record_vs_diff_charts.py` | Scatter (labeled + slide), dumbbell, and gap-distribution PNGs |
| 6 | `scripts/engineered_features_chart.py` | Feature chart PNG |

`.venv/`, the generated `site/` output, `local/`, and `.cursor/` are gitignored.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/pull_schedules.py
python scripts/record_vs_diff.py
python scripts/record_vs_diff_charts.py
python scripts/engineered_features_chart.py
```

| Step | You should see |
| --- | --- |
| `pull_schedules.py` | `data/raw/nflverse_2024_reg_games.csv` with 272 rows |
| `record_vs_diff.py` | `data/processed/2024_record_vs_diff.csv` with 32 rows |
| `record_vs_diff_charts.py` | four PNGs under `data/figures/` (augmented scatter, callout-only slide scatter, dumbbell, gap distribution) |
| `engineered_features_chart.py` | `data/figures/engineered-features.png` |

## Documentation Site

The `docs/` pages are published with [MkDocs](https://www.mkdocs.org/) + the Material theme.

Run it locally:

```bash
pip install mkdocs-material          # one-time, into your environment
mkdocs serve                          # live preview at http://127.0.0.1:8000
```

`mkdocs serve` reloads on every save. To build the static site once, run `mkdocs build` (output goes to `site/`, which is gitignored).

**Published site (GitHub Pages):** every push to `main` builds and deploys the site automatically via the workflow in `.github/workflows/docs.yml`. Once enabled, it is available at:

```
https://jconnors23.github.io/510-m1-nfl-data-storytelling/
```

To turn it on the first time: in the GitHub repository, open **Settings → Pages** and set the source to **GitHub Actions**. After that, each push to `main` republishes the site with no further steps. (`mkdocs.yml` is tracked in the repository so the workflow can build; only the generated `site/` output stays gitignored.)

## Working With Branches and Pull Requests

Changes land through short-lived branches and pull requests rather than commits straight to `main`:

```bash
git checkout -b feature/short-description   # start a branch off main
# ... make and test changes ...
git add <files> && git commit -m "Describe the change"
git push -u origin feature/short-description
```

Then open a pull request on GitHub, describe what changed and why, and merge after review. This keeps `main` reproducible and leaves a readable history of how the analysis came together.

## Where to Read Next

Read them in this order:

| Page | What it covers |
| --- | --- |
| [Data preparation & feature engineering](docs/feature-engineering.md) | The steps from games to teams, the column reference, the math |
| [Reproduction pipeline](docs/reproduction-pipeline.md) | Diagrams of the full flow |
| [Exploratory data analysis](docs/exploratory-data-analysis.md) | The five mismatch teams, what the charts show, what the numbers can't tell you |
| [Conclusions](docs/conclusions.md) | The short version and how to use it |
| [Notebook](notebooks/2024-ranking-walkthrough.ipynb) | The same steps, cell by cell |

## Data Source

- Release: <https://github.com/nflverse/nflverse-data/releases/tag/schedules>
- File: `https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv`
- License: CC-BY-4.0. Cite nflverse (Carl, Baldwin, and the nflverse team).
- Credit next to the data: [data/source-citation.md](data/source-citation.md)
