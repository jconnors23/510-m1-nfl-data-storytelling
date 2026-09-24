"""Draw a one-column-per-feature chart of the 2024 ranking table.

Reads Kansas City’s row from `data/processed/2024_record_vs_diff.csv` so the
example column matches the CSV. Writes `data/figures/engineered-features.png`.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

# This file lives in scripts/; the repo root is one folder up.
REPO_ROOT = Path(__file__).resolve().parents[1]
# 32-team ranking (one row per team) written by record_vs_diff.py.
TABLE_PATH = REPO_ROOT / "data" / "processed" / "2024_record_vs_diff.csv"
FIGURES_DIR = REPO_ROOT / "data" / "figures"
OUT_PATH = FIGURES_DIR / "engineered-features.png"

TITLE_COLOR = "#222222"
MUTED_TEXT = "#5a6570"
# Group tints: point differential, rankings, gap — light so body text stays readable.
GROUP_COLORS = {
    "Point differential": "#eef1f4",
    "Two rankings": "#e8eef4",
    "Gap between rankings": "#f6eeef",
}
ACCENT = {
    "Point differential": "#5c6b7a",
    "Two rankings": "#3d5a73",
    "Gap between rankings": "#c41e3a",
}


def load_kansas_city(path: Path = TABLE_PATH) -> pd.Series:
    """Return Kansas City’s ranking row (the worked example on the chart).

    Args:
        path: Season table with one row per team.

    Returns:
        One row: point differential, both rankings, and the gap columns.
    """
    teams = pd.read_csv(path)
    kc = teams.loc[teams["team"] == "KC"]
    if kc.empty:
        raise ValueError("Kansas City (KC) is missing from the ranking table.")
    return kc.iloc[0]


def feature_rows(kc: pd.Series) -> list[tuple[str, str, str, str]]:
    """Build the six one-column features with a Kansas City example.

    Args:
        kc: Kansas City’s row from the season table.

    Returns:
        Tuples of (group name, column name, what it represents, KC example).
    """
    gap = int(kc["rank_gap"])
    mismatch_text = "Yes" if bool(kc["mismatch"]) else "No"
    ahead = int(kc["record_ahead_by"])
    ahead_text = f"+{ahead} spots" if ahead > 0 else f"{ahead} spots"
    return [
        (
            "Point differential",
            "point_diff",
            "Points scored minus points allowed, added up over 17 games",
            f"{int(kc['point_diff']):+d}",
        ),
        (
            "Two rankings",
            "rank_win_pct",
            "Place among 32 teams by win–loss record (1 = best)",
            f"{int(kc['rank_win_pct'])}st of 32",
        ),
        (
            "Two rankings",
            "rank_point_diff",
            "Place among 32 teams by point differential (1 = best)",
            f"{int(kc['rank_point_diff'])}th of 32",
        ),
        (
            "Gap between rankings",
            "rank_gap",
            "How many spots apart those two places are",
            str(gap),
        ),
        (
            "Gap between rankings",
            "mismatch",
            "Yes when the gap is at least 6 spots",
            mismatch_text,
        ),
        (
            "Gap between rankings",
            "record_ahead_by",
            "Point-diff place minus record place; + means the record ranking is ahead",
            ahead_text,
        ),
    ]


def plot_feature_map(kc: pd.Series, out_path: Path = OUT_PATH) -> Path:
    """Draw the six-feature chart and write a PNG.

    Args:
        kc: Kansas City’s row for the example column.
        out_path: Where to save the figure.

    Returns:
        Path of the written PNG.
    """
    rows = feature_rows(kc)
    # Short group labels so they fit a left column without hitting `column`.
    group_short = {
        "Point differential": "1. Point diff",
        "Two rankings": "2. Rankings",
        "Gap between rankings": "3. Gap",
    }

    fig_w, fig_h = 13.2, 7.6
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    fig.text(
        0.5,
        0.965,
        "Engineered Features: One Column Each",
        fontsize=18,
        fontweight="bold",
        color=TITLE_COLOR,
        ha="center",
        va="top",
        transform=fig.transFigure,
    )
    # Underline rule centered beneath the title.
    fig.add_artist(
        plt.Line2D([0.32, 0.68], [0.925, 0.925], transform=fig.transFigure,
                   color=TITLE_COLOR, linewidth=1.6)
    )
    fig.text(
        0.5,
        0.905,
        "Kansas City 2024 (15–2) is the example. Rank 1 = best among 32 teams.",
        fontsize=12,
        color=MUTED_TEXT,
        ha="center",
        va="top",
        transform=fig.transFigure,
    )

    # Four columns in data units. Header strip sits above the six cards.
    x_group, x_col, x_mean, x_ex = 0.35, 2.35, 4.85, 12.85
    header_bottom = 6.55
    header_h = 0.38
    ax.add_patch(
        FancyBboxPatch(
            (0.18, header_bottom),
            12.84,
            header_h,
            boxstyle="round,pad=0.01,rounding_size=0.06",
            linewidth=0,
            edgecolor="none",
            facecolor="#f4f6f8",
            transform=ax.transData,
            clip_on=False,
        )
    )
    header_cy = header_bottom + header_h / 2
    ax.text(x_group, header_cy, "Group", fontsize=10, color=MUTED_TEXT, fontweight="bold", va="center")
    ax.text(x_col, header_cy, "Column", fontsize=10, color=MUTED_TEXT, fontweight="bold", va="center")
    ax.text(x_mean, header_cy, "What it represents", fontsize=10, color=MUTED_TEXT, fontweight="bold", va="center")
    ax.text(x_ex, header_cy, "Kansas City", fontsize=10, color=MUTED_TEXT, fontweight="bold", va="center", ha="right")

    card_h = 0.82
    gap = 0.10
    # First card top stays below the header strip.
    top = header_bottom - gap - card_h
    left = 0.18
    width = 12.84

    for i, (group, column, meaning, example) in enumerate(rows):
        y = top - i * (card_h + gap)
        face = GROUP_COLORS[group]
        edge = ACCENT[group]
        box = FancyBboxPatch(
            (left, y),
            width,
            card_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.5,
            edgecolor=edge,
            facecolor=face,
            transform=ax.transData,
            clip_on=False,
        )
        ax.add_patch(box)
        cy = y + card_h / 2
        ax.text(
            x_group,
            cy,
            group_short[group],
            fontsize=11,
            color=edge,
            va="center",
            ha="left",
            fontweight="bold",
        )
        ax.text(
            x_col,
            cy,
            column,
            fontsize=12,
            color=TITLE_COLOR,
            va="center",
            ha="left",
            fontfamily="monospace",
        )
        ax.text(x_mean, cy, meaning, fontsize=11, color=TITLE_COLOR, va="center", ha="left")
        ax.text(
            x_ex,
            cy,
            example,
            fontsize=13,
            color=TITLE_COLOR,
            va="center",
            ha="right",
            fontweight="bold",
        )

    fig.text(
        0.025,
        0.03,
        "Built in scripts/record_vs_diff.py. Per-game point_diff lives only in memory; this chart uses the season total.",
        fontsize=9,
        color=MUTED_TEXT,
        ha="left",
        va="bottom",
        transform=fig.transFigure,
    )

    fig.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.08)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out_path


def main() -> None:
    """Write `data/figures/engineered-features.png` and print the path."""
    kc = load_kansas_city()
    path = plot_feature_map(kc)
    print(f"Wrote {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
