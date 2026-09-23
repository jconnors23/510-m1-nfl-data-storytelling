"""Draw 2024 record vs point-differential charts and save PNGs.

Reads `data/2024_record_vs_diff.csv` (one row per team). Writes two figures
under `figures/` so GitHub and the public piece do not require a notebook.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# This file lives in scripts/; the repo root is one folder up.
REPO_ROOT = Path(__file__).resolve().parents[1]
# 32-team ranking written by record_vs_diff.py (one row per team).
TABLE_PATH = REPO_ROOT / "data" / "2024_record_vs_diff.csv"
FIGURES_DIR = REPO_ROOT / "figures"
SCATTER_PATH = FIGURES_DIR / "record-vs-diff.png"
BAR_PATH = FIGURES_DIR / "win-ranking-ahead-of-scoring.png"

# Slide colors: red = mismatch, gray = record matches scoring rank.
MISMATCH_COLOR = "#c41e3a"
MATCH_COLOR = "#5c6b7a"
TREND_COLOR = "#a8b3bd"
TITLE_COLOR = "#222222"
MUTED_TEXT = "#5a6570"

# Named scatter callouts. Offsets keep three-line labels off the dots and each other.
LABEL_OFFSET = {
    "KC": (16, -26),
    "DET": (12, 12),
    "MIN": (-78, 20),
    "HOU": (16, 20),
    "LA": (16, -36),
    "CAR": (12, 16),
}


def ordinal(n: int) -> str:
    """English ordinal for a ranking place (1 → 1st, 2 → 2nd, 11 → 11th)."""
    n = int(n)
    if 10 <= (n % 100) <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def scatter_callout(row: pd.Series) -> str:
    """Three-line scatter label: record, then both ranks among 32 teams.

    Example: KC 15–2 / 1st of 32 in record / 11th of 32 in scoring ranking.
    """
    record_line = f"{row['team']}  {row['record']}"
    win_line = f"{ordinal(row['rank_win_pct'])} of 32 in record"
    scoring_line = f"{ordinal(row['rank_point_diff'])} of 32 in scoring ranking"
    return f"{record_line}\n{win_line}\n{scoring_line}"


def load_ranking_table(path: Path = TABLE_PATH) -> pd.DataFrame:
    """Load the 32-team 2024 ranking table.

    Args:
        path: CSV from `record_vs_diff.py` (one row per team).

    Returns:
        Table with boolean `mismatch`, win% as a percent, and a record string.
    """
    # One row per team from the ranking script.
    teams = pd.read_csv(path)
    # CSV stores True/False as text; turn that into a real boolean.
    teams["mismatch"] = teams["mismatch"].astype(str).str.lower().eq("true")
    # Scatter wants 0–100, not 0–1 (50 = .500).
    teams["win_percent"] = teams["win_pct"] * 100
    # Wins–losses as text, e.g. "15–2".
    teams["record"] = (
        teams["wins"].astype(int).astype(str)
        + "–"
        + teams["losses"].astype(int).astype(str)
    )
    # Bar-chart tick: team plus record, e.g. "KC  15–2".
    teams["label"] = teams["team"] + "  " + teams["record"]
    return teams


def style_slide_axes(ax: plt.Axes) -> None:
    """Clean spines and tick look for a slide, not a spreadsheet."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#c5ccd3")
    ax.spines["bottom"].set_color("#c5ccd3")
    ax.tick_params(colors=MUTED_TEXT, labelsize=11)
    ax.grid(axis="both", color="#eef1f4", linewidth=1)
    ax.set_axisbelow(True)


def save_figure(fig: plt.Figure, out_path: Path, close: bool) -> tuple[plt.Figure, Path]:
    """Save PNG; optionally close so a script run does not leave windows open."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # 180 dpi keeps the PNG sharp on GitHub without a huge file.
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    if close:
        plt.close(fig)
    return fig, out_path


def plot_scatter(
    teams: pd.DataFrame, out_path: Path = SCATTER_PATH, close: bool = True
) -> tuple[plt.Figure, Path]:
    """Scatter: 2024 win percentage vs point differential.

    Gray dots: win ranking and scoring ranking are close (the record matches
    how they scored). Red dots: those two rankings are at least 6 spots apart.
    Detroit is labeled in gray as the matching 15–2 (both ranks filled).
    Each named label shows record, win rank of 32, and scoring rank of 32.

    Args:
        teams: Season ranking table from `load_ranking_table`.
        out_path: PNG path under `figures/`.
        close: If True, close the figure after saving.

    Returns:
        The matplotlib figure and the path that was written.
    """
    sns.set_theme(style="white", context="talk")
    fig, ax = plt.subplots(figsize=(11.8, 7.6))
    fig.patch.set_facecolor("white")

    # Gray = similar win ranking and scoring ranking. Red = those rankings far apart.
    matching_teams = teams.loc[~teams["mismatch"]]
    mismatch_teams = teams.loc[teams["mismatch"]]

    # Dashed line = “if the record matched the scoring, you would sit near here.”
    sns.regplot(
        data=teams,
        x="win_percent",
        y="point_diff",
        scatter=False,
        ax=ax,
        color=TREND_COLOR,
        line_kws={"linewidth": 2, "linestyle": "--"},
        ci=None,
    )

    ax.scatter(
        matching_teams["win_percent"],
        matching_teams["point_diff"],
        c=MATCH_COLOR,
        s=64,
        alpha=0.55,
        label="Similar win ranking and scoring ranking",
        zorder=2,
        edgecolors="none",
    )
    ax.scatter(
        mismatch_teams["win_percent"],
        mismatch_teams["point_diff"],
        c=MISMATCH_COLOR,
        s=130,
        label="Win ranking and scoring ranking 6+ spots apart",
        zorder=3,
        edgecolors="white",
        linewidths=0.8,
    )

    # Detroit stays gray (both ranks filled). Red mismatch teams: scoring rank blank.
    labeled_abbrevs = {"KC", "DET", "MIN", "HOU", "LA", "CAR"}
    labeled_rows = teams.loc[teams["team"].isin(labeled_abbrevs)]
    for _, row in labeled_rows.iterrows():
        abbrev = row["team"]
        xy_offset = LABEL_OFFSET.get(abbrev, (8, 6))
        label_text = scatter_callout(row)
        color = MISMATCH_COLOR if row["mismatch"] else MATCH_COLOR
        ax.annotate(
            label_text,
            (row["win_percent"], row["point_diff"]),
            textcoords="offset points",
            xytext=xy_offset,
            fontsize=9.5,
            color=color,
            fontweight="bold",
            linespacing=1.25,
            bbox={
                "boxstyle": "round,pad=0.28",
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": 0.92,
            },
            arrowprops={
                "arrowstyle": "-",
                "color": color,
                "lw": 0.8,
                "shrinkA": 1,
                "shrinkB": 6,
            },
        )

    # Crosshairs: 0 = scored as many as allowed; 50 = .500 record.
    ax.axhline(0, color="#c5ccd3", linewidth=1.2, zorder=1)
    ax.axvline(50, color="#c5ccd3", linewidth=1.2, zorder=1)

    ax.set_xlabel("Win percentage   →  more wins", fontsize=12, color=TITLE_COLOR)
    ax.set_ylabel("Point differential   →  more points scored than allowed", fontsize=12, color=TITLE_COLOR)
    fig.suptitle(
        "A 2024 win–loss record does not always match how the team scored",
        fontsize=16,
        fontweight="bold",
        color=TITLE_COLOR,
        x=0.01,
        ha="left",
        y=0.98,
    )
    ax.set_title(
        "Gray: the two rankings agree. Red: they sit 6+ spots apart. "
        "Neither ranking, in a vacuum, is team strength.",
        fontsize=11,
        color=MUTED_TEXT,
        loc="left",
        pad=12,
    )
    ax.legend(frameon=False, loc="lower right", fontsize=10, labelcolor=MUTED_TEXT)
    # Room for 3–14 through 15–2, and Carolina (−193) through Detroit (+222).
    ax.set_xlim(12, 100)
    ax.set_ylim(-230, 260)
    style_slide_axes(ax)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    return save_figure(fig, out_path, close)


def plot_mismatch_bars(
    teams: pd.DataFrame, out_path: Path = BAR_PATH, close: bool = True
) -> tuple[plt.Figure, Path]:
    """Horizontal bars: how far the win ranking sits ahead of the scoring ranking.

    All five mismatch teams have a better win ranking than scoring ranking.
    A longer bar means a bigger mismatch.

    Args:
        teams: Season ranking table from `load_ranking_table`.
        out_path: PNG path under `figures/`.
        close: If True, close the figure after saving.

    Returns:
        The matplotlib figure and the path that was written.
    """
    sns.set_theme(style="white", context="talk")
    # Smallest gap at the top so the longest bar (Kansas City) sits at the bottom.
    mismatch_teams = teams.loc[teams["mismatch"]].sort_values(
        "record_ahead_by", ascending=True
    ).copy()
    # Y-axis: record plus both ranks among 32 (one line so ticks stay aligned).
    mismatch_teams["bar_label"] = (
        mismatch_teams["team"]
        + "  "
        + mismatch_teams["record"]
        + " · "
        + mismatch_teams["rank_win_pct"].map(ordinal)
        + " of 32 in record · "
        + mismatch_teams["rank_point_diff"].map(ordinal)
        + " of 32 in scoring ranking"
    )

    fig, ax = plt.subplots(figsize=(13.2, 6.2))
    fig.patch.set_facecolor("white")
    ax.barh(
        mismatch_teams["bar_label"],
        mismatch_teams["record_ahead_by"],
        color=MISMATCH_COLOR,
        height=0.62,
        zorder=2,
    )
    for y, (_, row) in enumerate(mismatch_teams.iterrows()):
        # Sit the “+10 spots” label just past the end of the bar (ranking gap).
        ax.text(
            row["record_ahead_by"] + 0.12,
            y,
            f"+{int(row['record_ahead_by'])} spots",
            va="center",
            fontsize=11,
            color=TITLE_COLOR,
            fontweight="bold",
        )

    ax.set_xlabel(
        "How far the win ranking sits ahead of the scoring ranking",
        fontsize=12,
        color=TITLE_COLOR,
    )
    ax.set_ylabel("Team", fontsize=12, color=TITLE_COLOR)
    fig.suptitle(
        "Win ranking ahead of scoring ranking, 2024",
        fontsize=16,
        fontweight="bold",
        color=TITLE_COLOR,
        x=0.01,
        ha="left",
        y=0.98,
    )
    ax.set_title(
        "Kansas City’s 15–2 ranked 1st by wins and 11th by scoring (+10 ranking spots). "
        "Neither ranking, on its own, is enough.",
        fontsize=11,
        color=MUTED_TEXT,
        loc="left",
        pad=12,
    )
    ax.set_xlim(0, mismatch_teams["record_ahead_by"].max() + 2)
    style_slide_axes(ax)
    ax.tick_params(axis="y", labelsize=9)
    ax.grid(axis="x", color="#eef1f4", linewidth=1)
    ax.grid(axis="y", visible=False)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    return save_figure(fig, out_path, close)


def main() -> None:
    """Write both PNGs and print their paths."""
    teams = load_ranking_table()
    _, scatter_path = plot_scatter(teams)
    _, bar_path = plot_mismatch_bars(teams)
    print(f"Wrote {scatter_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {bar_path.relative_to(REPO_ROOT)}")
    print(f"mismatch teams: {', '.join(teams.loc[teams['mismatch'], 'team'])}")


if __name__ == "__main__":
    main()
