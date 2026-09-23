"""Compare 2024 regular-season records to point differential.

Each team plays **17 games** across **18 calendar weeks** (one week off, a
bye). This script uses the whole regular season: win–loss record vs points
scored minus points allowed. It is a description of 2024, not a prediction.

Writes `data/2024_record_vs_diff.csv`. Charts are a separate step:
`scripts/record_vs_diff_charts.py`.
"""

from pathlib import Path

import pandas as pd

# Rank gap of 6 ≈ a fifth of the 32-team league. Used as “record vs scoring mismatch.”
MISMATCH_RANK_GAP = 6

# This file lives in scripts/; the repo root is one folder up.
REPO_ROOT = Path(__file__).resolve().parents[1]
# Input: 272 completed 2024 regular-season games (one row per game).
GAMES_PATH = REPO_ROOT / "data" / "nflverse_2024_reg_games.csv"
# Output: one row per team (32 rows) with ranks and the mismatch flag.
OUT_PATH = REPO_ROOT / "data" / "2024_record_vs_diff.csv"


def games_to_team_rows(games: pd.DataFrame) -> pd.DataFrame:
    """Split each game into two rows: one for the home team, one for the away team.

    The extract is one row per *game*: `home_team`, `away_team`, `home_score`,
    `away_score` all sit on the same line. Sports pages often call that a
    box score (the final score of one game). It is not a league table of
    wins and losses. You cannot `groupby("team")` on it, because there is no
    `team` column — each row names two teams.

    Example: KC 30, SF 17 at home becomes two rows so later sums work:

    - team=KC, points_for=30, points_against=17, win=1, point_diff=+13
    - team=SF, points_for=17, points_against=30, win=0, point_diff=−13

    Args:
        games: One row per game with home/away teams and scores.

    Returns:
        One row per team-game with points scored, points allowed, and win/loss.
    """
    # Copy the home side: this team scored home_score and allowed away_score.
    home_rows = pd.DataFrame(
        {
            "week": games["week"],
            "team": games["home_team"],
            "points_for": games["home_score"],
            "points_against": games["away_score"],
        }
    )
    # Copy the away side: scores are swapped.
    away_rows = pd.DataFrame(
        {
            "week": games["week"],
            "team": games["away_team"],
            "points_for": games["away_score"],
            "points_against": games["home_score"],
        }
    )
    # Stack home and away into one table (544 team-game rows from 272 games).
    team_games = pd.concat([home_rows, away_rows], ignore_index=True)
    # Win if you scored more; 2024 regular season in this extract has no ties.
    team_games["win"] = (team_games["points_for"] > team_games["points_against"]).astype(int)
    team_games["loss"] = (team_games["points_for"] < team_games["points_against"]).astype(int)
    # Scored minus allowed for this team in this game (not in the nflverse file).
    team_games["point_diff"] = team_games["points_for"] - team_games["points_against"]
    return team_games


def summarize_season(team_games: pd.DataFrame) -> pd.DataFrame:
    """Add up wins, losses, and point differential for the full regular season.

    One row per team. Every team plays 17 games (one week off), so `games` should
    be 17 for all 32 teams in this extract.

    Args:
        team_games: Team-game rows for the whole regular season.

    Returns:
        One row per team with counts, total point_diff, and win percentage.
    """
    # One row per team: add up every regular-season game they played.
    # size = games played (row count). sum of win/loss = the W–L record.
    season_totals = (
        team_games.groupby("team", as_index=False)
        .agg(
            games=("win", "size"),
            wins=("win", "sum"),
            losses=("loss", "sum"),
            point_diff=("point_diff", "sum"),
        )
    )
    # Win percentage = wins / games played (17 for every team here).
    season_totals["win_pct"] = season_totals["wins"] / season_totals["games"]
    return season_totals


def build_season_table(games: pd.DataFrame) -> pd.DataFrame:
    """One row per team: 2024 record vs scoring, plus a mismatch flag.

    Line teams up twice — by win percentage and by point differential.
    Flag a mismatch when those two rankings are far apart.

    Args:
        games: 2024 regular-season completed games.

    Returns:
        One row per team with season totals, rankings, and mismatch columns.
        `record_ahead_by` is scoring ranking minus win ranking (positive = the
        win ranking sat ahead of the scoring ranking).
    """
    team_games = games_to_team_rows(games)
    teams = summarize_season(team_games)

    # 1 = best. Tied teams share a ranking: KC and DET both 15–2 → both 1st
    # by wins; the next teams are 3rd, not 2nd (pandas rank method="min").
    teams["rank_win_pct"] = teams["win_pct"].rank(ascending=False, method="min").astype(int)
    teams["rank_point_diff"] = (
        teams["point_diff"].rank(ascending=False, method="min").astype(int)
    )
    # How far apart those two place-numbers are. Flag if the gap is 6 or more.
    teams["rank_gap"] = (teams["rank_win_pct"] - teams["rank_point_diff"]).abs()
    teams["mismatch"] = teams["rank_gap"] >= MISMATCH_RANK_GAP
    # Positive: how far the win ranking sits ahead of the scoring ranking.
    teams["record_ahead_by"] = teams["rank_point_diff"] - teams["rank_win_pct"]
    # Best-record-first order for the written CSV (then team name).
    return teams.sort_values(["rank_win_pct", "team"]).reset_index(drop=True)


def main() -> None:
    """Write the season comparison table and print teams with a mismatch."""
    # Load the games extract into a table (one row per game).
    games = pd.read_csv(GAMES_PATH)
    teams = build_season_table(games)
    # Write the 32-team ranking; index=False so pandas does not add a row-number column.
    teams.to_csv(OUT_PATH, index=False)

    # Keep only flagged teams, largest gap first, for the printed list.
    mismatch_teams = teams.loc[teams["mismatch"]].sort_values("rank_gap", ascending=False)
    print(f"Wrote {len(teams)} teams to {OUT_PATH.relative_to(REPO_ROOT)}")
    print(
        f"full 2024 regular season; mismatch if |win ranking − scoring ranking| "
        f">= {MISMATCH_RANK_GAP}"
    )
    print(f"teams with a mismatch: {len(mismatch_teams)}")
    print_columns = [
        "team",
        "wins",
        "losses",
        "point_diff",
        "rank_win_pct",
        "rank_point_diff",
        "rank_gap",
        "record_ahead_by",
    ]
    print(mismatch_teams[print_columns].to_string(index=False))


if __name__ == "__main__":
    main()
