"""
Generate the illustrative cumulative-PnL figure used on the research page.

The curves are synthetic — correlated random walks with mild positive drift and
volatility clustering — chosen to look like a typical set of backtest equity
curves without disclosing any real model, result, or scale. Deliberately there
are no model names, no legend, and no tick labels on either axis.

Light and dark variants are emitted so the page can swap them with the theme.

    py -3.13 tools/make_pnl_figure.py
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "images" / "research"

SEED = 20260830
N_CURVES = 6
N_STEPS = 2520          # ~10 years of trading days
DT = 1.0 / 252.0

# Per-curve annualised drift and volatility. The spread is what makes the
# family read as "several models, some better than others" — the weakest one
# barely clears zero, which is what an honest sweep usually looks like.
DRIFTS = np.array([0.80, 0.67, 0.52, 0.36, 0.21, 0.07])
VOLS = np.array([0.46, 0.42, 0.37, 0.34, 0.31, 0.28])

# Share of each curve's shock that comes from a common market factor. Real
# backtests of related models co-move; fully independent walks look wrong.
COMMON_LOAD = 0.55

THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#1b1b1a",
        "muted": "#6a6863",
        "grid": "#e2e0da",
        "zero": "#b8b5ae",
        "colors": ["#b81d3a", "#2f6f9f", "#4a8c5f", "#c77e28", "#6b5b95", "#8a8578"],
    },
    "dark": {
        "bg": "#1d1f24",
        "fg": "#e6e4e0",
        "muted": "#9d9b95",
        "grid": "#33363d",
        "zero": "#4a4e57",
        "colors": ["#ef6b83", "#6bb0dd", "#7cc48f", "#e5a94f", "#a290c9", "#b0aaa0"],
    },
}


def volatility_path(rng, n):
    """A slow-moving volatility multiplier, so quiet and choppy regimes alternate."""
    shocks = rng.standard_normal(n)
    log_vol = np.zeros(n)
    for t in range(1, n):
        # Mean-reverting in logs (Ornstein-Uhlenbeck), strongly persistent so
        # calm stretches and turbulent ones each last a plausible while.
        log_vol[t] = 0.997 * log_vol[t - 1] + 0.085 * shocks[t]
    return np.exp(log_vol - log_vol.mean())


def build_curves():
    rng = np.random.default_rng(SEED)

    common = rng.standard_normal(N_STEPS)
    idio = rng.standard_normal((N_CURVES, N_STEPS))
    vol_regime = volatility_path(rng, N_STEPS)

    # Blend the shared factor with each curve's own noise, keeping unit variance.
    shocks = COMMON_LOAD * common + np.sqrt(1.0 - COMMON_LOAD**2) * idio
    shocks *= vol_regime

    daily = DRIFTS[:, None] * DT + VOLS[:, None] * np.sqrt(DT) * shocks
    curves = np.cumsum(daily, axis=1)

    # Every backtest starts flat at zero.
    return np.hstack([np.zeros((N_CURVES, 1)), curves])


def render(curves, theme_name, theme):
    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=200)
    fig.patch.set_facecolor(theme["bg"])
    ax.set_facecolor(theme["bg"])

    x = np.arange(curves.shape[1])

    ax.axhline(0.0, color=theme["zero"], linewidth=0.9, zorder=1)
    ax.set_axisbelow(True)

    for i in range(curves.shape[0]):
        ax.plot(
            x,
            curves[i],
            color=theme["colors"][i % len(theme["colors"])],
            linewidth=1.15,
            solid_joinstyle="round",
            zorder=3,
        )

    # No legend, no model names, and no readable scale on either axis.
    ax.set_xlabel("Time", color=theme["muted"], fontsize=10, labelpad=8)
    ax.set_ylabel("Cumulative PnL", color=theme["muted"], fontsize=10, labelpad=8)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(x[0], x[-1])

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(theme["grid"])
        ax.spines[side].set_linewidth(0.9)

    fig.tight_layout(pad=0.7)

    stem = OUT_DIR / f"pnl-illustrative-{theme_name}"
    for suffix in (".pdf", ".png"):
        fig.savefig(
            stem.with_suffix(suffix),
            facecolor=theme["bg"],
            edgecolor="none",
            transparent=False,
        )
        print(f"wrote {stem.with_suffix(suffix).relative_to(OUT_DIR.parents[3])}")

    plt.close(fig)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    curves = build_curves()
    for name, theme in THEMES.items():
        render(curves, name, theme)


if __name__ == "__main__":
    main()
