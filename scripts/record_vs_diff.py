"""Turn 2024 regular-season game scores into a per-team record-vs-scoring table.

Reads the games file (one row per game), reshapes it into one row per team,
ranks the 32 teams two different ways (by win-loss record and by points scored
minus points allowed), and flags teams that land far apart on the two lists.
Writes ``data/processed/2024_record_vs_diff.csv``. This describes the finished
2024 season; it is not a prediction.
"""
from pathlib import Path

import pandas as pd

# A gap of 6 places is about a fifth of a 32-team league. Below this we treat the
# two rankings as "basically agreeing"; at or above it, we call it a mismatch.
MISMATCH_RANK_GAP = 6

REPO_ROOT = Path(__file__).resolve().parents[1]
GAMES_PATH = REPO_ROOT / "data" / "raw" / "nflverse_2024_reg_games.csv"
OUT_PATH = REPO_ROOT / "data" / "processed" / "2024_record_vs_diff.csv"


def games_to_team_rows(games: pd.DataFrame) -> pd.DataFrame:
    """Split each game into two team-rows so we can later group by team.

    The games file has one row per game, and each row names *two* teams
    (``home_team`` and ``away_team``). There is no single ``team`` column, so
    you cannot ``groupby("team")`` on it yet. The fix: copy every game into two
    rows, one written from each team's point of view, swapping which score is
    "for" and which is "against".

    Note: this exactly doubles the row count (272 games -> 544 team-games).
    """
    # Home team's view: it scored home_score and gave up away_score.
    home_rows = pd.DataFrame(
        {
            "week": games["week"],
            "team": games["home_team"],
            "points_for": games["home_score"],
            "points_against": games["away_score"],
        }
    )
    # Away team's view: the same game with the two scores flipped.
    away_rows = pd.DataFrame(
        {
            "week": games["week"],
            "team": games["away_team"],
            "points_for": games["away_score"],
            "points_against": games["home_score"],
        }
    )
    team_games = pd.concat([home_rows, away_rows], ignore_index=True)
    # A team won if it scored more than it allowed. The 2024 regular season here
    # has no ties, so exactly one of win/loss is 1 for every team-game.
    team_games["win"] = (team_games["points_for"] > team_games["points_against"]).astype(int)
    team_games["loss"] = (team_games["points_for"] < team_games["points_against"]).astype(int)
    # Per-game point margin (points for minus points against). This column does
    # not exist in the nflverse file; we build it here and later sum it into the
    # season point differential.
    team_games["point_diff"] = team_games["points_for"] - team_games["points_against"]
    return team_games


def summarize_season(team_games: pd.DataFrame) -> pd.DataFrame:
    """Collapse the 544 team-games into one season row per team.

    Note: every team plays 17 games (one week off during the 18 weeks), so
    ``games`` should equal 17 for all 32 teams after this step.
    """
    season_totals = (
        team_games.groupby("team", as_index=False)
        .agg(
            games=("win", "size"),      # row count = games played
            wins=("win", "sum"),        # total wins
            losses=("loss", "sum"),     # total losses
            point_diff=("point_diff", "sum"),  # season point differential = sum of per-game margins
        )
    )
    # Win rate on a 0..1 scale; feeds the record ranking below.
    season_totals["win_pct"] = season_totals["wins"] / season_totals["games"]
    return season_totals


def build_season_table(games: pd.DataFrame) -> pd.DataFrame:
    """Produce the final per-team table: two rankings plus the gap features."""
    team_games = games_to_team_rows(games)
    teams = summarize_season(team_games)

    # Rank 1 = best. method="min" means tied teams share a place: KC and DET
    # both went 15-2, so both are 1st by record and no team is 2nd.
    teams["rank_win_pct"] = teams["win_pct"].rank(ascending=False, method="min").astype(int)
    teams["rank_point_diff"] = (
        teams["point_diff"].rank(ascending=False, method="min").astype(int)
    )
    # How far apart the two rankings sit for each team, and whether that is large.
    teams["rank_gap"] = (teams["rank_win_pct"] - teams["rank_point_diff"]).abs()
    teams["mismatch"] = teams["rank_gap"] >= MISMATCH_RANK_GAP
    # Positive => the record ranking is ahead of (numerically smaller than) the
    # point-differential ranking.
    teams["record_ahead_by"] = teams["rank_point_diff"] - teams["rank_win_pct"]
    return teams.sort_values(["rank_win_pct", "team"]).reset_index(drop=True)


def main() -> None:
    games = pd.read_csv(GAMES_PATH)
    teams = build_season_table(games)
    # Heads up: this overwrites data/processed/2024_record_vs_diff.csv, which
    # both chart scripts and the docs rely on. index=False keeps pandas from
    # adding an unnamed row-number column.
    teams.to_csv(OUT_PATH, index=False)

    mismatch_teams = teams.loc[teams["mismatch"]].sort_values("rank_gap", ascending=False)
    print(f"Wrote {len(teams)} teams to {OUT_PATH.relative_to(REPO_ROOT)}")
    print(
        f"full 2024 regular season; mismatch if |record ranking − point-differential ranking| "
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
