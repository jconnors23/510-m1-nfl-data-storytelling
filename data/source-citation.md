# Source citation

This file sits next to the games CSV. It is the credit for the 2024 regular-season extract.

- Source: https://github.com/nflverse/nflverse-data/releases/tag/schedules
- File: `games.csv` (GitHub Release asset)
- License: CC-BY-4.0
- Cite: nflverse (Carl, Baldwin, and the nflverse team)

Rebuild the extract with:

```bash
python scripts/pull_schedules.py
```

The output is `data/nflverse_2024_reg_games.csv`: `season == 2024`, `game_type == "REG"` (regular season), final scores present. Next: [feature engineering](../docs/feature-engineering.md) and the [analysis pipeline](../docs/analysis-pipeline.md).
