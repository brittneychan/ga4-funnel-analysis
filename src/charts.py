import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from src.config import FIG_DIR

BLUE, RED, GRAY = "#2F5D8A", "#C8553D", "#B8C4CE"

def style() -> None:
    plt.rcParams.update({
        "figure.dpi": 120, "savefig.dpi": 200,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titleweight": "bold", "axes.titlesize": 13, "font.size": 10,
    })

def save(fig, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_DIR / name, bbox_inches="tight")

def funnel_chart(df, title: str, name: str | None = None):
    """df: one funnel_type from funnel_overall."""
    style()
    df = df.sort_values("step_order").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(9, 0.7 * len(df) + 1.2))
    ypos = list(range(len(df)))[::-1]
    ax.barh(ypos, df["sessions"], color=BLUE)
    for y, row in zip(ypos, df.itertuples()):
        label = f"  {row.sessions:,.0f}  ({row.pct_of_top:.1%} of top)"
        if row.step_order > 1:
            label += f"   step conversion {row.step_conversion:.1%}"
        ax.text(row.sessions, y, label, va="center", fontsize=9)
    ax.set_yticks(ypos, df["step"])
    ax.xaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlim(0, df["sessions"].max() * 1.9)
    ax.set_xlabel("Sessions")
    ax.set_title(title, loc="left")
    fig.tight_layout()
    if name:
        save(fig, name)
    return fig

def rate_heatmap(seg, dimension: str, name: str | None = None):
    """Cells show real rates; color shows how each segment compares with the others in that column."""
    style()
    cols = ["view_to_cart", "cart_to_checkout", "checkout_to_purchase", "view_to_purchase"]
    d = (seg[seg["dimension"] == dimension]
         .set_index("segment")[cols]
         .sort_values("view_to_purchase"))
    z = (d - d.mean()) / d.std(ddof=0)
    fig, ax = plt.subplots(figsize=(9, 0.5 * len(d) + 1.5))
    sns.heatmap(z, annot=d, fmt=".1%", cmap="RdBu", center=0, cbar=False, linewidths=0.5, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(f"Funnel step conversion by {dimension} (red = below peers)", loc="left")
    fig.tight_layout()
    if name:
        save(fig, name)
    return fig

def forest_plot(res, step: str, name: str | None = None):
    """Each segment's gap vs the baseline with its 95% CI. Red = significantly worse."""
    style()
    d = res[res["step"] == step].sort_values("abs_diff").reset_index(drop=True)
    y = list(range(len(d)))
    colors = [RED if (sig and diff < 0) else BLUE if sig else GRAY
              for sig, diff in zip(d["significant"], d["abs_diff"])]
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(d) + 1.6))
    ax.errorbar(d["abs_diff"] * 100, y,
                xerr=[(d["abs_diff"] - d["diff_ci_low"]) * 100,
                      (d["diff_ci_high"] - d["abs_diff"]) * 100],
                fmt="none", ecolor=GRAY, capsize=3)
    ax.scatter(d["abs_diff"] * 100, y, c=colors, zorder=3, s=40)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(y, d["segment"])
    ax.set_xlabel(f"Difference vs {d['baseline'].iloc[0]} (percentage points, 95% CI)")
    ax.set_title(f"{step.replace('_', ' ').capitalize()}: gap vs baseline", loc="left")
    fig.tight_layout()
    if name:
        save(fig, name)
    return fig