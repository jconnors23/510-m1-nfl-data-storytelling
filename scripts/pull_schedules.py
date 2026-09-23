"""Pull 2024 regular-season completed games from the nflverse schedules release.

Downloads the full historical `games.csv`, then keeps one finished regular
season (272 games, 32 teams). That extract is the input to `record_vs_diff.py`.
"""

from pathlib import Path

import pandas as pd

# Direct download link for the schedules CSV on GitHub Releases
# (not a file inside the nflverse-data source tree). Tag name: schedules.
# Cite nflverse; license CC-BY-4.0.
SCHEDULES_URL = (
    "https://github.com/nflverse/nflverse-data/releases/download/"
    "schedules/games.csv"
)
SEASON = 2024  # This story is 2024 only; the Release CSV holds many years.
# This file lives in scripts/; the repo root is one folder up.
REPO_ROOT = Path(__file__).resolve().parents[1]
# Filtered extract: 2024 REG games with final scores (272 rows).
OUT_PATH = REPO_ROOT / "data" / "nflverse_2024_reg_games.csv"


def pull_regular_season(url: str = SCHEDULES_URL, season: int = SEASON) -> pd.DataFrame:
    """Download the full historical table, then keep one completed regular season.

    Args:
        url: Direct GitHub Release URL for `games.csv`.
        season: NFL season year to keep (this project: 2024).

    Returns:
        One row per finished regular-season game, sorted by week and date.
    """
    # Download the full historical table (many seasons) into memory.
    all_games = pd.read_csv(url)

    # Keep this season only. REG = regular season (not preseason, not playoffs).
    # dropna: remove games that never got a final home/away score.
    season_games = all_games.loc[
        (all_games["season"] == season) & (all_games["game_type"] == "REG")
    ].dropna(subset=["home_score", "away_score"])

    # Chronological order; reset_index so row numbers start at 0 again.
    return season_games.sort_values(["week", "gameday", "game_id"]).reset_index(drop=True)


def main() -> None:
    """Write the 2024 regular-season extract to `data/` and print a short summary."""
    season_games = pull_regular_season()
    # Make data/ if it is missing, then write the filtered table as CSV.
    # index=False so pandas does not add a row-number column.
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    season_games.to_csv(OUT_PATH, index=False)

    # Unique teams = home names plus away names, counting each franchise once.
    team_count = pd.concat([season_games["home_team"], season_games["away_team"]]).nunique()
    print(f"Wrote {len(season_games)} games to {OUT_PATH.relative_to(REPO_ROOT)}")
    print(
        f"weeks {int(season_games['week'].min())}–{int(season_games['week'].max())}; "
        f"teams {team_count}"
    )


if __name__ == "__main__":
    main()
