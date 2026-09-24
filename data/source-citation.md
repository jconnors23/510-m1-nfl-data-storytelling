# Source Citation

This file credits the 2024 regular-season data used across the project.

- Source: <https://github.com/nflverse/nflverse-data/releases/tag/schedules>
- File: `games.csv` (a download attached to a GitHub release, not a file on the repo's main branch)
- License: CC-BY-4.0
- Cite: nflverse (Carl, Baldwin, and the nflverse team)

Rebuild the data file with:

```bash
python scripts/pull_schedules.py
```

The output is `data/raw/nflverse_2024_reg_games.csv`: rows where the season is 2024, the game type is regular season, and final scores are present.
