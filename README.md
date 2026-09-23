# 2024 NFL records vs point differential

Compares 2024 REG win–loss records to season point differential (scored − allowed) across 32 clubs. The decision object is the gap between record place and scoring place; `mismatch` ⇔ `rank_gap ≥ 6` ([feature engineering](docs/feature-engineering.md)). Findings, chart encodings, and identification limits: [analysis](docs/record-vs-point-diff-analysis.md). Operator DAG: [analysis pipeline](docs/analysis-pipeline.md).

**Upstream:** nflverse schedules Release (`games.csv`, CC-BY-4.0) — [source citation](data/source-citation.md). **Downstream:** `data/2024_record_vs_diff.csv` (32 rows) and three PNGs under `figures/`.

Scope facts used everywhere: 32 clubs; 18 calendar weeks; 17 games per club; 272 completed REG games. Club codes (KC, DET, …) are nflverse abbreviations. A record `15–2` is 15 wins and 2 losses.

## Lineage

```text
nflverse schedules Release  (games.csv)
        │  scripts/pull_schedules.py
        ▼
data/nflverse_2024_reg_games.csv          272 REG games
        │  scripts/record_vs_diff.py
        ▼
data/2024_record_vs_diff.csv              32 team-seasons
        │  scripts/record_vs_diff_charts.py
        │  scripts/engineered_features_chart.py
        ▼
figures/record-vs-diff.png
figures/win-ranking-ahead-of-scoring.png
figures/engineered-features.png
```

Outputs (interpretation on the analysis page, not here):

![Scatter: win percentage vs point differential.](figures/record-vs-diff.png)

![Bar: record_ahead_by for the mismatch subset.](figures/win-ranking-ahead-of-scoring.png)

## Tree

```text
scripts/     pull_schedules.py · record_vs_diff.py · record_vs_diff_charts.py · engineered_features_chart.py
data/        nflverse_2024_reg_games.csv · 2024_record_vs_diff.csv · source-citation.md
figures/     scatter · mismatch bar · feature map
docs/        record-vs-point-diff-analysis.md · feature-engineering.md · analysis-pipeline.md
notebooks/   2024-ranking-walkthrough.ipynb   (replica; no writes; kernel Python (510-m1))
```

| Order | Path | Role |
| --- | --- | --- |
| 1 | `scripts/pull_schedules.py` | Extract 2024 REG completed games |
| 2 | `data/nflverse_2024_reg_games.csv` | 272 game rows |
| 3 | `scripts/record_vs_diff.py` | Team-season table + mismatch |
| 4 | `data/2024_record_vs_diff.csv` | 32 rows |
| 5 | `scripts/record_vs_diff_charts.py` | Scatter and bar PNGs |
| 6 | `scripts/engineered_features_chart.py` | Feature-map PNG |

`.venv`, MkDocs working drafts, and `.cursor/` are gitignored.

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

| Step | Exit criterion |
| --- | --- |
| 1 | `data/nflverse_2024_reg_games.csv` = 272 rows |
| 2 | `data/2024_record_vs_diff.csv` = 32 rows |
| 3–4 | three PNGs under `figures/` |

| Read next | Owns |
| --- | --- |
| [Analysis](docs/record-vs-point-diff-analysis.md) | Mismatch set, chart encodings, constraints |
| [Feature engineering](docs/feature-engineering.md) | Grain 272→544→32, dictionary, formulas |
| [Analysis pipeline](docs/analysis-pipeline.md) | Mermaid DAG, failure domains |
| [Notebook](notebooks/2024-ranking-walkthrough.ipynb) | In-process replica |

## Data

- Release: https://github.com/nflverse/nflverse-data/releases/tag/schedules
- Asset: `https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv`
- License: CC-BY-4.0. Cite nflverse (Carl, Baldwin, and the nflverse team).
- File-local credit: [data/source-citation.md](data/source-citation.md)
