"""Draw the 2024 record vs point-differential charts and save them as PNGs.

Reads the 32-team table `data/processed/2024_record_vs_diff.csv` (one row per
team) and writes three figures into `data/figures/`. These are the images the
docs site and the README embed, so the site does not need the notebook to build.

Figures written:
- record-vs-diff-augmented.png : every team plotted by win percentage against
                                 season point differential, the four quadrants
                                 shaded and named, and the five mismatch teams
                                 called out with their record and both rankings.
- record-vs-diff-slide.png     : the same scatter with only the mismatch
                                 callouts (plus DET as the anchor for the KC
                                 comparison), for presentations where the small
                                 per-team codes would be hard to read projected.
- record-ahead-dumbbell.png    : for each mismatch team, its record ranking and
                                 its point-differential ranking joined by a line;
                                 a longer line means a larger gap.
- rank-gap-distribution.png    : how many teams sit at each ranking-gap value,
                                 with the mismatch cutoff of 6 marked.

Run it with `python scripts/record_vs_diff_charts.py` after `record_vs_diff.py`
has written the table.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch

# This file lives in scripts/; the repo root is one folder up.
REPO_ROOT = Path(__file__).resolve().parents[1]
# 32-team ranking written by record_vs_diff.py (one row per team).
TABLE_PATH = REPO_ROOT / "data" / "processed" / "2024_record_vs_diff.csv"
FIGURES_DIR = REPO_ROOT / "data" / "figures"

# Slide colors: red = mismatch team, gray = record and scoring rank sit close.
MISMATCH_COLOR = "#c41e3a"
MATCH_COLOR = "#5c6b7a"
TREND_COLOR = "#a8b3bd"
TITLE_COLOR = "#222222"
MUTED_TEXT = "#5a6570"

# Where each mismatch team's callout box sits relative to its dot, in points.
# These offsets are hand-tuned to keep the three-line boxes off the dots and
# clear of each other; adjust them if the data or the axis limits change.
CALLOUT_OFFSET = {
    "KC": (14, -34),
    "MIN": (-158, 20),
    "HOU": (40, 40),
    "LA": (-120, -40),
    "CAR": (16, 20),
}


def ordinal(n: int) -> str:
    """English ordinal for a ranking place (1 -> 1st, 2 -> 2nd, 11 -> 11th)."""
    n = int(n)
    # 11th through 13th are the exceptions that always take "th".
    if 10 <= (n % 100) <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def load_ranking_table(path: Path = TABLE_PATH) -> pd.DataFrame:
    """Load the 32-team table and add the columns the charts need.

    Args:
        path: CSV from `record_vs_diff.py` (one row per team).

    Returns:
        The table with a boolean `mismatch`, win percentage on a 0-100 scale,
        and a "15-2" style record string.
    """
    teams = pd.read_csv(path)
    # The CSV stores the flag as the text "True"/"False"; make it a real boolean.
    teams["mismatch"] = teams["mismatch"].astype(str).str.lower().eq("true")
    # The scatter axis reads better on a 0-100 scale, where 50 is a .500 record.
    teams["win_percent"] = teams["win_pct"] * 100
    teams["record"] = (
        teams["wins"].astype(int).astype(str)
        + "\u2013"
        + teams["losses"].astype(int).astype(str)
    )
    return teams


def style_slide_axes(ax: plt.Axes) -> None:
    """Trim the spines and ticks so a chart reads like a slide, not a spreadsheet."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#c5ccd3")
    ax.spines["bottom"].set_color("#c5ccd3")
    ax.tick_params(colors=MUTED_TEXT, labelsize=11)
    ax.set_axisbelow(True)


def centered_title(
    fig: plt.Figure, title: str, subtitle: str = "", top: float = 0.98
) -> None:
    """Draw a bold title, an underline rule, and an optional subtitle as one block.

    The title and (when given) the subtitle are drawn as figure text at fixed y
    positions just below the top of the figure, with the underline rule between
    them. Keeping both lines here (instead of a figure suptitle plus a separate
    per-axes title) means there is no empty band whose size depends on the axes
    height or on `tight_layout` — the pieces always sit together. Reserve the
    matching top strip with `fig.subplots_adjust(top=...)` in the caller so the
    plot starts just below. Pass no subtitle for a title-only header.

    Matplotlib has no underline, so the rule is a short horizontal line drawn in
    figure coordinates under the title text.
    """
    title_y = top
    rule_y = top - 0.035
    subtitle_y = top - 0.058
    fig.text(0.5, title_y, title, fontsize=18, fontweight="bold",
             color=TITLE_COLOR, ha="center", va="top")
    line = plt.Line2D([0.30, 0.70], [rule_y, rule_y], transform=fig.transFigure,
                      color=TITLE_COLOR, linewidth=1.6)
    fig.add_artist(line)
    if subtitle:
        fig.text(0.5, subtitle_y, subtitle, fontsize=11, color=MUTED_TEXT,
                 ha="center", va="top", wrap=True)


def save_figure(fig: plt.Figure, name: str) -> Path:
    """Write a figure into data/figures/ at slide resolution and close it."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out = FIGURES_DIR / name
    # 180 dpi keeps the PNG sharp on GitHub and the docs site without a huge file.
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


# Non-mismatch teams to still label by code in the slide (callout-only) version,
# because they anchor the story: DET is the other 15-2 team KC is compared to.
SLIDE_KEEP_LABELS = {"DET"}


def plot_scatter_augmented(
    teams: pd.DataFrame,
    label_all_teams: bool = True,
    out_name: str = "record-vs-diff-augmented.png",
) -> Path:
    """Scatter every team by win percentage against season point differential.

    The crosshairs at a .500 record (50 across) and an even point differential
    (0 up) split the plot into four regions. Each region is shaded a light
    version of a saturated key color and named in the legend. The five mismatch
    teams always get a full callout with their record and both rankings.

    Args:
        teams: the ranking table from `load_ranking_table`.
        label_all_teams: if True (the docs version) every team gets a small code
            label. If False (the slide version) only the mismatch callouts and a
            few anchor teams are labeled, so the chart stays legible when
            projected — dense small labels are hard to read from a distance.
        out_name: PNG filename written under `data/figures/`.

    The dashed line is an ordinary least-squares trend line: for a given win
    percentage, it marks the season point differential you would expect on
    average across the 32 teams. A team above the line outscored opponents by
    more than its record suggests; a team below it by less. It is a trend line,
    not a y = x line.
    """
    sns.set_theme(style="white", context="talk")
    fig, ax = plt.subplots(figsize=(13.2, 8.0))
    fig.patch.set_facecolor("white")

    x_lo, x_hi = 12, 100
    y_lo, y_hi = -230, 260

    # Four regions split at x=50 (a .500 record) and y=0 (an even point
    # differential). Each has one saturated key color; the fill drawn on the
    # plot is a light version of that same color so the dots stay legible.
    q_strong = "#2e7d43"   # won a lot AND outscored opponents (top-right)
    q_flat = "#d98a1f"     # won a lot, small or negative point differential (bottom-right)
    q_unlucky = "#2f6da3"  # losing record, positive point differential (top-left)
    q_weak = "#b23a48"     # losing record AND outscored (bottom-left)
    fill_alpha = 0.16

    ax.add_patch(plt.Rectangle((50, 0), x_hi - 50, y_hi, color=q_strong, alpha=fill_alpha, zorder=0))
    ax.add_patch(plt.Rectangle((50, y_lo), x_hi - 50, -y_lo, color=q_flat, alpha=fill_alpha, zorder=0))
    ax.add_patch(plt.Rectangle((x_lo, 0), 50 - x_lo, y_hi, color=q_unlucky, alpha=fill_alpha, zorder=0))
    ax.add_patch(plt.Rectangle((x_lo, y_lo), 50 - x_lo, -y_lo, color=q_weak, alpha=fill_alpha, zorder=0))

    # Dashed trend line: the average point differential at each win percentage.
    sns.regplot(
        data=teams, x="win_percent", y="point_diff", scatter=False, ax=ax,
        color=TREND_COLOR, line_kws={"linewidth": 2, "linestyle": "--"}, ci=None,
    )

    matching = teams.loc[~teams["mismatch"]]
    mism = teams.loc[teams["mismatch"]]
    ax.scatter(matching["win_percent"], matching["point_diff"], c=MATCH_COLOR,
               s=70, alpha=0.9, zorder=2, edgecolors="white", linewidths=0.6)
    ax.scatter(mism["win_percent"], mism["point_diff"], c=MISMATCH_COLOR,
               s=170, zorder=3, edgecolors="white", linewidths=1.0)

    # Non-mismatch teams: a small team-code label next to each dot. The docs
    # version labels them all; the slide version keeps only a few anchor codes
    # (larger) so the chart reads from the back of a room.
    if label_all_teams:
        code_rows = matching
        code_size = 8.5
    else:
        code_rows = matching.loc[matching["team"].isin(SLIDE_KEEP_LABELS)]
        code_size = 11
    for _, row in code_rows.iterrows():
        ax.annotate(
            row["team"], (row["win_percent"], row["point_diff"]),
            textcoords="offset points", xytext=(6, 5), fontsize=code_size,
            color=TITLE_COLOR, fontweight="bold" if not label_all_teams else "normal",
        )

    # Mismatch teams: a boxed callout with the record and both rankings, offset
    # off the dot so the label does not cover it.
    for _, row in mism.iterrows():
        text = (
            f"{row['team']}  {row['record']}\n"
            f"{ordinal(int(row['rank_win_pct']))} of 32 by record\n"
            f"{ordinal(int(row['rank_point_diff']))} of 32 by point differential"
        )
        ax.annotate(
            text, (row["win_percent"], row["point_diff"]),
            textcoords="offset points",
            xytext=CALLOUT_OFFSET.get(row["team"], (12, 10)),
            fontsize=9, color=MISMATCH_COLOR, fontweight="bold", linespacing=1.25,
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "white",
                  "edgecolor": MISMATCH_COLOR, "alpha": 0.92, "linewidth": 0.8},
            arrowprops={"arrowstyle": "-", "color": MISMATCH_COLOR, "lw": 0.8,
                        "shrinkA": 1, "shrinkB": 6},
        )

    ax.axhline(0, color="#5a6570", linewidth=1.6, zorder=1)
    ax.axvline(50, color="#5a6570", linewidth=1.6, zorder=1)
    ax.set_xlabel("Win percentage   \u2192  more wins", fontsize=12,
                  color=TITLE_COLOR, fontweight="bold")
    ax.set_ylabel("Season point differential   \u2192  more points scored than allowed",
                  fontsize=12, color=TITLE_COLOR, fontweight="bold")
    centered_title(
        fig,
        "Record vs. Season Point Differential, 2024",
        "Each dot is a team (red = mismatch). The dashed line is the average point "
        "differential at each win percentage; background color names each region.",
    )

    # Legend uses the saturated key colors, not the faded fill, so it reads clearly.
    quadrant_key = [
        Patch(facecolor=q_strong, label="Won a lot \u00b7 outscored opponents"),
        Patch(facecolor=q_flat, label="Won a lot \u00b7 small or negative point differential"),
        Patch(facecolor=q_unlucky, label="Losing record \u00b7 positive point differential"),
        Patch(facecolor=q_weak, label="Losing record \u00b7 outscored"),
    ]
    legend = ax.legend(
        handles=quadrant_key, title="What Each Quadrant Means",
        frameon=True, framealpha=1.0, edgecolor="#c5ccd3",
        loc="lower right", fontsize=12, title_fontsize=13,
        labelcolor=TITLE_COLOR, handlelength=2.2, handleheight=1.6,
        borderpad=1.0, labelspacing=0.7,
    )
    legend.get_title().set_fontweight("bold")

    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(y_lo, y_hi)
    ax.grid(axis="both", color="#e3e7eb", linewidth=0.7)
    style_slide_axes(ax)
    # Reserve just the title block at the top; the plot starts right below it.
    fig.subplots_adjust(top=0.90, bottom=0.09, left=0.075, right=0.975)
    return save_figure(fig, out_name)


def plot_dumbbell(teams: pd.DataFrame) -> Path:
    """Dumbbell: each mismatch team's two rankings, joined by a line.

    For every mismatch team a gray dot marks its record ranking and a red dot
    marks its point-differential ranking; the line between them is the gap. The
    chart shows both where each ranking sits (1st vs 11th) and how far apart the
    two are. In 2024 all five teams rank higher by record than by point
    differential, so every red dot sits to the right of its gray dot.
    """
    sns.set_theme(style="white", context="talk")
    # Smallest gap at the top so Kansas City (the largest) sits at the bottom.
    mismatch_teams = teams.loc[teams["mismatch"]].sort_values(
        "record_ahead_by", ascending=True
    ).copy()
    labels = mismatch_teams["team"] + "  " + mismatch_teams["record"]
    ys = list(range(len(mismatch_teams)))

    fig, ax = plt.subplots(figsize=(12.5, 6.0))
    fig.patch.set_facecolor("white")

    # The connecting line is the ranking gap.
    for yi, (_, row) in zip(ys, mismatch_teams.iterrows()):
        ax.plot(
            [row["rank_win_pct"], row["rank_point_diff"]], [yi, yi],
            color="#c5ccd3", linewidth=2.5, zorder=1,
        )
    ax.scatter(mismatch_teams["rank_win_pct"], ys, color=MATCH_COLOR, s=150,
               zorder=2, label="Record ranking")
    ax.scatter(mismatch_teams["rank_point_diff"], ys, color=MISMATCH_COLOR, s=150,
               zorder=2, label="Point-differential ranking")
    # The ordinal place above each dot.
    for yi, (_, row) in zip(ys, mismatch_teams.iterrows()):
        ax.annotate(ordinal(int(row["rank_win_pct"])), (row["rank_win_pct"], yi),
                    textcoords="offset points", xytext=(0, 10), ha="center",
                    fontsize=9, color=MATCH_COLOR, fontweight="bold")
        ax.annotate(ordinal(int(row["rank_point_diff"])), (row["rank_point_diff"], yi),
                    textcoords="offset points", xytext=(0, 10), ha="center",
                    fontsize=9, color=MISMATCH_COLOR, fontweight="bold")

    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel("Place among 32 teams (1 = best)", fontsize=12,
                  color=TITLE_COLOR, fontweight="bold")
    centered_title(
        fig,
        "Where Each Mismatch Team Ranks on the Two Lists, 2024",
        "Each line links a team's record ranking (gray) to its point-differential ranking (red). "
        "The longer the line, the larger the gap.",
    )
    ax.legend(frameon=False, loc="lower right", fontsize=10, labelcolor=MUTED_TEXT)
    ax.set_xlim(0, 33)
    # A little headroom above the top row and below the bottom row so the dot
    # labels and the bottom team do not touch the frame.
    ax.set_ylim(-0.6, len(mismatch_teams) - 0.4)
    ax.grid(axis="x", color="#eef1f4", linewidth=1)
    ax.grid(axis="y", visible=False)
    style_slide_axes(ax)
    fig.subplots_adjust(top=0.88, bottom=0.11, left=0.12, right=0.975)
    return save_figure(fig, "record-ahead-dumbbell.png")


def plot_rank_gap_distribution(teams: pd.DataFrame) -> Path:
    """Bar chart: how many teams sit at each ranking-gap value.

    The docs say in words that most teams have a small gap and only five clear
    the cutoff of 6. This shows that directly: a count of teams at each gap
    value, with the cutoff line drawn in.
    """
    sns.set_theme(style="white", context="talk")
    counts = teams["rank_gap"].value_counts().sort_index()

    # Stats computed from the data so the labels never drift from the chart.
    total = len(teams)
    n_mismatch = int((teams["rank_gap"] >= 6).sum())
    pct_mismatch = round(100 * n_mismatch / total)
    mean_gap = teams["rank_gap"].mean()

    fig, ax = plt.subplots(figsize=(11.8, 6.0))
    fig.patch.set_facecolor("white")
    colors = [MISMATCH_COLOR if g >= 6 else MATCH_COLOR for g in counts.index]
    ax.bar(counts.index, counts.values, color=colors, width=0.8, zorder=2)
    for g, c in counts.items():
        ax.text(g, c + 0.1, str(int(c)), ha="center", va="bottom",
                fontsize=10, color=TITLE_COLOR, fontweight="bold")

    # Headroom above the tallest bar for the reference-line labels and callout.
    y_top = counts.values.max() + 2.2
    ax.set_ylim(0, y_top)

    # Average gap as a single reference line (the median adds little for this
    # right-skewed count, so it is left off). Label sits to the right of the
    # line, like the cutoff label, and above the bars so it stays clear of the
    # nearby count.
    stat_color = "#1f2933"
    ax.axvline(mean_gap, color=stat_color, linewidth=2.0, linestyle="--", zorder=4)
    ax.text(mean_gap + 0.15, y_top * 0.94, f"average gap ({mean_gap:.1f})",
            color=stat_color, fontsize=10, fontweight="bold",
            ha="left", va="top")

    # The cutoff sits at 5.5 so the line falls between the gray and red bars.
    ax.axvline(5.5, color=MISMATCH_COLOR, linewidth=1.6, linestyle="--", zorder=3)
    ax.text(5.6, y_top * 0.52, "mismatch\ncutoff (6)",
            color=MISMATCH_COLOR, fontsize=10, fontweight="bold", va="top")

    # Headline metric over the red region: how many teams cleared the cutoff.
    ax.text(
        counts.index.max(), y_top * 0.9,
        f"{n_mismatch} of {total} teams\n({pct_mismatch}%) are mismatches",
        color=MISMATCH_COLOR, fontsize=12, fontweight="bold", ha="right", va="top",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "white",
              "edgecolor": MISMATCH_COLOR, "linewidth": 1.2},
    )

    ax.set_xlabel("Ranking gap \u2014 places between a team's record and point-differential ranks",
                  fontsize=12, color=TITLE_COLOR, fontweight="bold")
    ax.set_ylabel("Number of teams", fontsize=12, color=TITLE_COLOR, fontweight="bold")
    centered_title(fig, "Ranking Gap Across All 32 Teams, 2024")
    ax.set_xticks(range(0, int(counts.index.max()) + 1))
    ax.grid(axis="y", color="#eef1f4", linewidth=1)
    style_slide_axes(ax)
    # Title-only header (no subtitle), so a bit more plot height.
    fig.subplots_adjust(top=0.90, bottom=0.12, left=0.08, right=0.975)
    return save_figure(fig, "rank-gap-distribution.png")


def main() -> None:
    """Write all four PNGs and print their paths.

    The docs embed the fully labeled scatter, the dumbbell, and the gap
    distribution. The slide variant of the scatter (callouts only) is for
    presentations, where the small per-team codes would be hard to read.
    """
    teams = load_ranking_table()
    for path in (
        plot_scatter_augmented(teams),
        plot_scatter_augmented(
            teams, label_all_teams=False, out_name="record-vs-diff-slide.png"
        ),
        plot_dumbbell(teams),
        plot_rank_gap_distribution(teams),
    ):
        print(f"Wrote {path.relative_to(REPO_ROOT)}")
    print(f"mismatch teams: {', '.join(teams.loc[teams['mismatch'], 'team'])}")


if __name__ == "__main__":
    main()
