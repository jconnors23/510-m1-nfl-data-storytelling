# Record vs point differential analysis

Findings for the 2024 REG season table: where win–loss records and point differential (scored − allowed) diverge, what the two figures encode, and which identification limits apply. Schema and grain: [feature engineering](feature-engineering.md). Rebuild: [README](../README.md). Topology: [analysis pipeline](analysis-pipeline.md). Persistence: `data/2024_record_vs_diff.csv`. In-process replica: [`notebooks/2024-ranking-walkthrough.ipynb`](../notebooks/2024-ranking-walkthrough.ipynb).

**Decision object:** the gap between record place (`rank_win_pct`) and scoring place (`rank_point_diff`). **Result:** 5 of 32 clubs satisfy `mismatch` (`rank_gap ≥ 6`); all five have `record_ahead_by > 0`. Neither place, in isolation, is team strength. Strength is multi-faceted (schedule, injuries, close games, late scores).

Record discards margin. Point differential retains margin and treats every opponent as equal. The two orderings are compressions of the same 272 games.

## Mismatch definition (this extract)

Every club is ordered twice, place `1` = best:

1. `rank_win_pct` — `rank_min(win_pct, descending)`.
2. `rank_point_diff` — `rank_min(point_diff, descending)`.

Ties share a place (`method="min"`). KC and DET both 15–2 ⇒ both `rank_win_pct = 1`; no club is 2nd; the next clubs are 3rd.

KC: record place **1**, scoring place **11**, `rank_gap = 10`. **Mismatch** ⇔ `rank_gap ≥ 6` (≈ one fifth of a 32-club league): a threshold on disagreement, not a claim that either ordering is “true strength.”

Coverage: 18 calendar weeks, 17 games per club, full REG extract. No mid-season split. No forecast.

League-wide `rank_gap`: mean **2.9**, median **2.5**. Flag **6**.

## Mismatch set (2024)

Five clubs. In every case record place is numerically ahead of scoring place (`record_ahead_by > 0`).

| Team | Record | `point_diff` | `rank_win_pct` | `rank_point_diff` | `record_ahead_by` |
| --- | --- | --- | --- | --- | --- |
| KC | 15–2 | +59 | 1 | 11 | +10 |
| CAR | 5–12 | −193 | 23 | 32 | +9 |
| LA | 10–7 | −19 | 10 | 17 | +7 |
| MIN | 14–3 | +100 | 3 | 9 | +6 |
| HOU | 10–7 | 0 | 10 | 16 | +6 |

KC finished 15–2 — the same record as DET — with scoring place 11. DET’s 15–2 came with `point_diff = +222`, first in the league: both places **1**, so the two summaries agree. HOU went 10–7 with `point_diff = 0` (points scored equal points allowed). LA went 10–7 with `point_diff = −19` (outscored). CAR’s 5–12 was already a poor record; `point_diff = −193` is last in the league. Directional claim is **2024-specific**: every large mismatch is record-ahead, consistent with this season’s close wins versus blowouts (large final margins). That pattern is not a general law that records “lie.”

## Charts

Writers: `scripts/record_vs_diff_charts.py`. The notebook draws the same figures in-process and does not write PNGs. Feature-map PNG: `figures/engineered-features.png` ([feature engineering](feature-engineering.md)).

### Scatter — `win_pct` vs season `point_diff`

![Scatter of 2024 win percentage versus point differential. Gray = places agree. Red = mismatch.](../figures/record-vs-diff.png)

Each point is one club’s 2024 REG season.

- **Right** on X (`win_pct` as percent): higher win rate.
- **Up** on Y (`point_diff`): larger season margin.
- **Dashed line:** OLS fit of margin on win rate — the ordinary pairing of better record with better margin.
- **Gray** (`mismatch = false`): record place and scoring place are close. Named gray control: DET, 15–2, 1st on both lists.
- **Red** (`mismatch = true`): `rank_gap ≥ 6`. Each red label is club, record, then both places among 32:
  - KC: 15–2, 1st of 32 by record, 11th of 32 by scoring
  - MIN: 14–3, 3rd and 9th
  - HOU: 10–7, 10th and 16th
  - LA: 10–7, 10th and 17th
  - CAR: 5–12, 23rd and 32nd

Crosshairs: X = 50 (`.500` record), Y = 0 (scored = allowed).

### Bar — `record_ahead_by` on the mismatch subset

![Horizontal bars: record_ahead_by for the five mismatch clubs.](../figures/win-ranking-ahead-of-scoring.png)

Each bar is one of the five red clubs. Length = `record_ahead_by`. Longer ⇒ record place further ahead of scoring place. KC 15–2: record place **1**, scoring place **11**, **+10**.

## Analytical constraints

**Neither column identifies strength.** Record maps every game to `{win, loss}`. Point differential retains margin and still collapses a season to one integer. Residual structure — opponent, availability, one-score games, scoring after the winner is decided — is not in either column.

**17-game sample.** REG spans 18 calendar weeks; each club plays 17 games. That is a short panel. Two or three one-score wins can lift `win_pct` with little movement in `point_diff`; one 40-point loss can move `point_diff` with little movement in the win column. KC’s 15–2 and HOU’s `point_diff = 0` both sit on that 17-game stack. This ranking describes those 17 games; it does not estimate a longer-season parameter.

**Schedule (no opponent adjustment).** Point differential is translation-invariant across opponents: `+20` versus a 3–14 club equals `+20` versus a 14–3 club. The series does not encode injuries, rest the prior week, or whether the usual starter played. A “high” or “low” margin can be schedule as much as club. Record has the same hole: a win is a win independent of opponent.

**Garbage time.** After the winner is decided, backups often play; subsequent scoring still enters the final score and therefore `point_diff` and `mismatch`. That movement does not imply the trailing club “almost won,” nor that the blowout winner was stronger by the full margin.

**Role of the gap.** Gray: the two compressions agree; the second number adds little. Red: the season reads differently by which summary is opened. The analysis **is** that gap. It is not a search for a single true ranking and not a prediction of the next season.

## Takeaways

- Record and point differential are two compressions of the **same** 272 games.
- **Neither place, in a vacuum, is team strength.** Schedule, injuries, close games, and late scores sit outside both columns.
- 2024 mismatch set: five clubs, all record-ahead. Sharpest same-record contrast: KC 15–2 vs DET 15–2.

**Also:** [feature engineering](feature-engineering.md) · [analysis pipeline](analysis-pipeline.md) · [README](../README.md) · [walkthrough](../notebooks/2024-ranking-walkthrough.ipynb)
