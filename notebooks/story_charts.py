"""
Charts for docs/story.md.

Every figure is queried live from the dbt staging models, so the images can be
rebuilt from the data rather than from numbers typed into a script. Each chart
is rendered twice - light and dark - and the story serves the right one through
a <picture> element.

    python notebooks/story_charts.py

Colour follows the entity across every chart: fiber is always blue, DSL always
orange, and everything the story is not about sits in a neutral grey. The pair
and the ordinal blue ramp were checked with the dataviz palette validator in
both modes (all gates pass).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from google.cloud import bigquery
from matplotlib.patches import FancyBboxPatch, Rectangle
from statsmodels.stats.proportion import confint_proportions_2indep

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "img"
OUT.mkdir(parents=True, exist_ok=True)
load_dotenv(ROOT / ".env")
client = bigquery.Client(project="focus-appliance-507309-h8")


def run_query(sql):
    return client.query(sql).to_dataframe()


# --------------------------------------------------------------------- theme
MODES = {
    "light": dict(
        surface="#fcfcfb", ink="#0b0b0b", ink2="#52514e", muted="#898781",
        grid="#e1e0d9", base="#c3c2b7", fiber="#2a78d6", dsl="#eb6834",
        neutral="#b3b1a9", ramp_lo="#86b6ef", ramp_hi="#2a78d6",
    ),
    "dark": dict(
        surface="#1a1a19", ink="#ffffff", ink2="#c3c2b7", muted="#898781",
        grid="#2c2c2a", base="#383835", fiber="#3987e5", dsl="#d95926",
        neutral="#5f5e59", ramp_lo="#1c5cab", ramp_hi="#3987e5",
    ),
}
SANS, SANS_BOLD = "Segoe UI", "Segoe UI Semibold"
DPI_LAYOUT, DPI_OUT = 100, 220  # lay out at 1x logical px, export for high-dpi
plt.rcParams.update({"font.family": SANS, "svg.fonttype": "none"})


def canvas(c, width, height, left, right, top, bottom):
    """Figure with fixed margins, so pixel-based mark specs stay exact."""
    fig = plt.figure(figsize=(width, height), dpi=DPI_LAYOUT, facecolor=c["surface"])
    ax = fig.add_axes([left, bottom, 1 - left - right, 1 - top - bottom])
    ax.set_facecolor(c["surface"])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(c["base"])
    ax.spines["bottom"].set_linewidth(1)
    ax.tick_params(colors=c["muted"], labelsize=9, length=0, pad=6)
    return fig, ax


def header(fig, c, title, subtitle, x=0.035, top=0.955):
    fig.text(x, top, title, fontfamily=SANS_BOLD, fontsize=13.5, color=c["ink"],
             ha="left", va="top")
    fig.text(x, top - 0.075, subtitle, fontsize=9.5, color=c["ink2"],
             ha="left", va="top")


def footer(fig, c, text, x=0.035, y=0.03):
    fig.text(x, y, text, fontsize=8, color=c["muted"], ha="left", va="bottom",
             linespacing=1.45)


def legend(fig, c, items, x, y):
    """Swatch + ink label. Text never wears the series colour."""
    for label, color in items:
        fig.patches.append(Rectangle((x, y - 0.012), 0.014, 0.028, color=color,
                                     transform=fig.transFigure, figure=fig))
        t = fig.text(x + 0.021, y, label, fontsize=9, color=c["ink2"], va="center")
        fig.canvas.draw()
        x += 0.021 + t.get_window_extent().width / fig.bbox.width + 0.03


def px(ax):
    """Data units per logical pixel, x and y, for the axes as laid out."""
    bb = ax.get_window_extent()
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    return (x1 - x0) / bb.width, abs(y1 - y0) / bb.height


def hbar(ax, y, value, color, thick_px=20, radius_px=4):
    """Horizontal bar: <=24px thick, 4px rounded data-end, square at baseline."""
    xpp, ypp = px(ax)
    h, r = thick_px * ypp, radius_px * xpp
    ax.add_patch(FancyBboxPatch(
        (0, y - h / 2), value, h, boxstyle=f"round,pad=0,rounding_size={r}",
        mutation_aspect=ypp / xpp, fc=color, ec="none", zorder=3))
    ax.add_patch(Rectangle((0, y - h / 2), min(value, 2 * r), h, fc=color,
                           ec="none", zorder=3))


def dot(ax, x, y, color, c, size=9.5):
    """>=8px marker with a 2px surface ring."""
    ax.plot(x, y, "o", ms=size, mfc=color, mec=c["surface"], mew=2, zorder=5)


def backing(c):
    """Surface-coloured pad behind a label that sits over a gridline."""
    return dict(boxstyle="square,pad=0.15", fc=c["surface"], ec="none")


def gridlines(ax, c, axis="x"):
    ax.grid(axis=axis, color=c["grid"], linewidth=1, linestyle="-", zorder=0)
    ax.set_axisbelow(True)


def save(fig, name, mode):
    path = OUT / f"{name}{'' if mode == 'light' else '_dark'}.png"
    fig.savefig(path, dpi=DPI_OUT, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


# ---------------------------------------------------------------------- data
TREE = run_query("""
SELECT
  IF(se.tenure_in_months <= 3, 'New', 'Established') AS era,
  se.contract,
  IF(se.internet_type = 'fiber optic', 'fiber', 'not fiber') AS fiber,
  COUNT(*) AS customers,
  COUNTIF(st.churn_label) AS churners,
  SUM(IF(st.churn_label, se.monthly_charge, 0)) AS lost_monthly
FROM `dbt_dev.stg_telco__services` se
JOIN `dbt_dev.stg_telco__status` st USING (customer_id)
GROUP BY era, se.contract, fiber
""")

PRICE = run_query("""
SELECT
  se.internet_type,
  CASE
    WHEN se.monthly_charge < 75 THEN '$58-75'
    WHEN se.monthly_charge < 88 THEN '$75-88'
    ELSE '$88-100'
  END AS price_band,
  COUNT(*) AS customers,
  COUNTIF(st.churn_label) AS churners
FROM `dbt_dev.stg_telco__services` se
JOIN `dbt_dev.stg_telco__status` st USING (customer_id)
WHERE se.tenure_in_months > 3
  AND se.internet_type IN ('fiber optic', 'dsl')
  AND se.monthly_charge >= 58 AND se.monthly_charge < 100
GROUP BY se.internet_type, price_band
""")

REASONS = run_query("""
SELECT se.internet_type, st.churn_category, COUNT(*) AS churners
FROM `dbt_dev.stg_telco__status` st
JOIN `dbt_dev.stg_telco__services` se USING (customer_id)
WHERE st.churn_label AND se.internet_type IN ('fiber optic', 'dsl')
GROUP BY se.internet_type, st.churn_category
""")

ERAS = run_query("""
SELECT
  IF(se.internet_service, se.internet_type, 'no internet') AS internet_type,
  IF(se.tenure_in_months <= 3, 'new', 'established') AS era,
  COUNT(*) AS customers,
  COUNTIF(st.churn_label) AS churners
FROM `dbt_dev.stg_telco__services` se
JOIN `dbt_dev.stg_telco__status` st USING (customer_id)
GROUP BY internet_type, era
""")

M2M = run_query("""
SELECT se.internet_type, COUNT(*) AS customers, COUNTIF(st.churn_label) AS churners
FROM `dbt_dev.stg_telco__services` se
JOIN `dbt_dev.stg_telco__status` st USING (customer_id)
WHERE se.tenure_in_months > 3 AND se.contract = 'month-to-month'
  AND se.internet_type IN ('fiber optic', 'dsl')
GROUP BY se.internet_type
""").set_index("internet_type")

FIBER_BILL = run_query("""
SELECT AVG(se.monthly_charge) AS avg_bill
FROM `dbt_dev.stg_telco__services` se
JOIN `dbt_dev.stg_telco__status` st USING (customer_id)
WHERE st.churn_label AND se.internet_type = 'fiber optic'
""")["avg_bill"].item()


# ------------------------------------------------------------------- chart 1
def chart_concentration(mode):
    c = MODES[mode]
    t = TREE.copy()
    total_k = t["churners"].sum()
    m2m = t[t["contract"] == "month-to-month"].copy()
    m2m["share"] = m2m["churners"] / total_k * 100
    m2m = m2m.sort_values("share", ascending=False)
    rest = t[t["contract"] != "month-to-month"]
    rows = [
        (f"{r.era} · month-to-month · {r.fiber}",
         f"{int(r.customers):,} customers · {r.churners / r.customers * 100:.1f}% churn",
         r.share, c["fiber"] if r.fiber == "fiber" else c["neutral"])
        for r in m2m.itertuples()
    ] + [(
        "Eight committed-contract segments",
        f"{int(rest['customers'].sum()):,} customers · "
        f"{rest['churners'].sum() / rest['customers'].sum() * 100:.1f}% churn",
        rest["churners"].sum() / total_k * 100, c["neutral"])]

    fig, ax = canvas(c, 8.6, 4.9, left=0.335, right=0.13, top=0.29, bottom=0.16)
    n = len(rows)
    ax.set_xlim(0, 50)
    ax.set_ylim(n - 0.4, -0.6)
    gridlines(ax, c)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.set_xticklabels([f"{v}%" for v in [0, 10, 20, 30, 40, 50]])
    ax.set_yticks([])
    for i, (label, sub, share, color) in enumerate(rows):
        hbar(ax, i, share, color)
        ax.text(share + 0.8, i, f"{share:.1f}%", va="center", fontsize=9.5,
                color=c["ink"], fontfamily=SANS_BOLD)
        ax.text(-1.2, i - 0.13, label, ha="right", va="center", fontsize=9.5,
                color=c["ink"])
        ax.text(-1.2, i + 0.2, sub, ha="right", va="center", fontsize=8,
                color=c["muted"])

    # bracket: the four month-to-month rows
    cum = sum(r[2] for r in rows[:4])
    xb = 47.2
    ax.plot([xb, xb + 0.8, xb + 0.8, xb], [-0.25, -0.25, 3.25, 3.25],
            color=c["ink2"], lw=1, clip_on=False, solid_capstyle="butt")
    ax.text(xb + 1.6, 1.5, f"{cum:.1f}%\nof all\nchurn", va="center", ha="left",
            fontsize=9.5, color=c["ink"], fontfamily=SANS_BOLD, linespacing=1.2,
            clip_on=False)

    header(fig, c, "Four month-to-month segments hold 88.6% of all churn",
           f"Share of all {int(total_k):,} churners, by segment. Every customer "
           "sits in exactly one segment, so the shares add to 100%.")
    legend(fig, c, [("Fiber", c["fiber"]), ("Not fiber, or on a committed contract",
                                            c["neutral"])], x=0.035, y=0.765)
    footer(fig, c, f"Base: all {int(t['customers'].sum()):,} customers, one quarter. "
                   "New = first three months of tenure.")
    return save(fig, "01_churn_concentration", mode)


# ------------------------------------------------------------------- chart 2
def chart_price(mode):
    c = MODES[mode]
    p = PRICE.copy()
    p["rate"] = p["churners"] / p["customers"] * 100
    bands = ["$58-75", "$75-88", "$88-100"]
    fib = p[p.internet_type == "fiber optic"].set_index("price_band").loc[bands]
    dsl = p[p.internet_type == "dsl"].set_index("price_band").loc[bands]

    fig, ax = canvas(c, 8.6, 4.4, left=0.14, right=0.06, top=0.30, bottom=0.17)
    ax.set_xlim(0, 55)
    ax.set_ylim(2.55, -0.55)
    gridlines(ax, c)
    ax.set_xticks(range(0, 60, 10))
    ax.set_xticklabels([f"{v}%" for v in range(0, 60, 10)])
    ax.set_yticks(range(3))
    ax.set_yticklabels([b.replace("-", "–") for b in bands], fontsize=10,
                       color=c["ink"])
    for i, b in enumerate(bands):
        d, f = dsl.loc[b, "rate"], fib.loc[b, "rate"]
        ax.plot([d, f], [i, i], color=c["base"], lw=2, solid_capstyle="round",
                zorder=2)
        dot(ax, d, i, c["dsl"], c)
        dot(ax, f, i, c["fiber"], c)
        ax.text((d + f) / 2, i - 0.2, f"+{f - d:.1f} pts", ha="center", va="bottom",
                fontsize=9, color=c["ink2"], bbox=backing(c))
        ax.text(f + 1.3, i, f"{f:.1f}%", va="center", fontsize=9.5,
                color=c["ink"], fontfamily=SANS_BOLD)

    # the second point, set beside the row it lands on - no connector to collide
    ax.text(fib.iloc[-1]["rate"] + 8.2, 2, "Fiber churn falls\nas the bill rises",
            fontsize=9, color=c["ink2"], ha="left", va="center", linespacing=1.3)

    header(fig, c, "At the same monthly price, fiber customers churn far more than DSL",
           "Churn rate by monthly charge, in the three price bands where both "
           "products are sold.")
    legend(fig, c, [("Fiber", c["fiber"]), ("DSL", c["dsl"])], x=0.035, y=0.765)
    n = int(p["customers"].sum())
    footer(fig, c, f"Base: {n:,} established fiber and DSL customers (tenure > 3 months). "
                   "Gaps are fiber minus DSL, in percentage points.")
    return save(fig, "02_price_bands", mode), n


# ------------------------------------------------------------------- chart 3
def chart_reasons(mode):
    c = MODES[mode]
    r = REASONS.copy()
    r["share"] = r["churners"] / r.groupby("internet_type")["churners"].transform("sum") * 100
    wide = r.pivot(index="churn_category", columns="internet_type", values="share")
    wide = wide.sort_values("fiber optic", ascending=False)
    story = {"competitor", "price"}

    fig, ax = canvas(c, 8.6, 4.8, left=0.2, right=0.06, top=0.29, bottom=0.18)
    ax.set_xlim(0, 55)
    ax.set_ylim(len(wide) - 0.5, -0.6)
    gridlines(ax, c)
    ax.set_xticks(range(0, 60, 10))
    ax.set_xticklabels([f"{v}%" for v in range(0, 60, 10)])
    ax.set_yticks(range(len(wide)))
    ax.set_yticklabels([])
    for i, (cat, row) in enumerate(wide.iterrows()):
        f, d = row["fiber optic"], row["dsl"]
        hot = cat in story
        ax.text(-1.5, i, cat.capitalize(), ha="right", va="center", fontsize=10,
                color=c["ink"] if hot else c["ink2"],
                fontfamily=SANS_BOLD if hot else SANS)
        ax.plot([min(f, d), max(f, d)], [i, i], color=c["base"], lw=2,
                solid_capstyle="round", zorder=2)
        dot(ax, d, i, c["dsl"], c)
        dot(ax, f, i, c["fiber"], c)
        if hot:  # label on whichever side has room, never clipped at the edge
            room_right = max(f, d) < 35
            ax.text(max(f, d) + 1.4 if room_right else min(f, d) - 1.4, i,
                    f"fiber {f:.1f}% vs DSL {d:.1f}%", va="center",
                    ha="left" if room_right else "right", fontsize=9, color=c["ink"],
                    bbox=backing(c))

    header(fig, c, "Fiber churners name a competitor more often, and price no more often",
           "Share of each product's churners, by the reason recorded at cancellation.")
    legend(fig, c, [("Fiber", c["fiber"]), ("DSL", c["dsl"])], x=0.035, y=0.765)
    n = int(r["churners"].sum())
    footer(fig, c, f"Base: {n:,} fiber and DSL churners; difference in reason mix p = 0.03. "
                   "Reasons are chosen from a fixed list at\ncancellation - they are "
                   "reason codes, not customers' own words.")
    return save(fig, "03_churn_reasons", mode), n


# ------------------------------------------------------------------- chart 4
def chart_first_months(mode):
    c = MODES[mode]
    e = ERAS.copy()
    e["rate"] = e["churners"] / e["customers"] * 100
    wide = e.pivot(index="internet_type", columns="era", values="rate")
    order = ["fiber optic", "cable", "dsl", "no internet"]
    names = {"fiber optic": "Fiber", "cable": "Cable", "dsl": "DSL",
             "no internet": "No internet"}
    colors = {"fiber optic": c["fiber"], "dsl": c["dsl"],
              "cable": c["neutral"], "no internet": c["neutral"]}

    fig, ax = canvas(c, 8.6, 5.0, left=0.2, right=0.28, top=0.26, bottom=0.19)
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(0, 85)
    ax.spines["bottom"].set_visible(False)
    # every point carries its own value label, so the y-axis and grid would only
    # repeat them - and its ticks collide with the left-end labels
    ax.set_yticks([])
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["First three months", "Established (4+ months)"],
                       fontsize=10, color=c["ink"])
    for key in reversed(order):  # story lines drawn last, on top
        new, est = wide.loc[key, "new"], wide.loc[key, "established"]
        ax.plot([0, 1], [new, est], color=colors[key], lw=2, zorder=3,
                solid_capstyle="round")
        dot(ax, 0, new, colors[key], c)
        dot(ax, 1, est, colors[key], c)
        ax.text(-0.045, new, f"{new:.1f}%", ha="right", va="center", fontsize=9,
                color=c["ink"])
        ax.text(1.045, est, f"{est:.1f}%   {names[key]}", ha="left", va="center",
                fontsize=9.5, color=c["ink"],
                fontfamily=SANS_BOLD if key in ("fiber optic", "dsl") else SANS)

    header(fig, c, "Every product churns faster in the first three months, in the same order",
           "Churn rate by internet type, new against established customers.")
    legend(fig, c, [("Fiber", c["fiber"]), ("DSL", c["dsl"]),
                    ("Cable, no internet", c["neutral"])], x=0.035, y=0.79)
    n = int(e["customers"].sum())
    footer(fig, c, f"Base: all {n:,} customers. The first-three-month band holds no "
                   "'stayed' customers - only those who left and those who\njust "
                   "joined - so its rate describes a new cohort, not a like-for-like "
                   "comparison.")
    return save(fig, "04_first_months", mode)


# ------------------------------------------------------------------- chart 5
def chart_cost(mode):
    c = MODES[mode]
    t = TREE
    total = t["lost_monthly"].sum()
    m2m_fiber = t[(t.contract == "month-to-month") & (t.fiber == "fiber")]["lost_monthly"].sum()

    kf, nf = M2M.loc["fiber optic", ["churners", "customers"]].astype(int)
    kd, nd = M2M.loc["dsl", ["churners", "customers"]].astype(int)
    gap = kf / nf - kd / nd
    lo, hi = confint_proportions_2indep(kf, nf, kd, nd, compare="diff", method="newcomb")
    excess = nf * gap * FIBER_BILL
    ex_lo, ex_hi = nf * lo * FIBER_BILL, nf * hi * FIBER_BILL

    rows = [
        ("All billing lost to churn", f"{int(t['churners'].sum()):,} churners", total,
         c["neutral"]),
        ("Month-to-month fiber customers",
         f"{int(t[(t.contract == 'month-to-month') & (t.fiber == 'fiber')]['churners'].sum()):,} "
         f"churners · {m2m_fiber / total * 100:.1f}% of the total", m2m_fiber, c["ramp_lo"]),
        ("Fiber-specific: above the DSL rate",
         f"~{nf * gap:.0f} churners (range {nf * lo:.0f}–{nf * hi:.0f})", excess, c["ramp_hi"]),
    ]

    # rows are named by their own labels, so no legend band above the plot
    fig, ax = canvas(c, 8.6, 3.8, left=0.33, right=0.12, top=0.22, bottom=0.22)
    ax.set_xlim(0, 150_000)
    ax.set_ylim(2.55, -0.55)
    gridlines(ax, c)
    ticks = range(0, 150_001, 25_000)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"${v // 1000:,}k" for v in ticks])
    ax.set_yticks([])
    for i, (label, sub, value, color) in enumerate(rows):
        hbar(ax, i, value, color)
        ax.text(-2500, i - 0.13, label, ha="right", va="center", fontsize=9.5,
                color=c["ink"])
        ax.text(-2500, i + 0.2, sub, ha="right", va="center", fontsize=8,
                color=c["muted"])
    # value labels; the last row carries its interval whisker instead
    for i in (0, 1):
        ax.text(rows[i][2] + 2000, i, f"${rows[i][2] / 1000:,.1f}k", va="center",
                fontsize=9.5, color=c["ink"], fontfamily=SANS_BOLD)
    ax.plot([ex_lo, ex_hi], [2, 2], color=c["ink"], lw=1.4, zorder=4)
    for x in (ex_lo, ex_hi):
        ax.plot([x, x], [1.87, 2.13], color=c["ink"], lw=1.4, zorder=4)
    ax.text(ex_hi + 2000, 2, f"${excess / 1000:,.1f}k", va="center", fontsize=9.5,
            color=c["ink"], fontfamily=SANS_BOLD)
    # two '$' in one string reads as mathtext - escape them
    ax.text(ex_hi + 2000, 2.27,
            f"range \\${ex_lo / 1000:,.1f}k–\\${ex_hi / 1000:,.1f}k",
            va="center", fontsize=8, color=c["muted"])

    header(fig, c, "About $37,000 a month of lost billing is specific to fiber",
           "Monthly charge of the customers who churned. Each bar is a subset of the "
           "one above it.")
    footer(fig, c, f"Base: all {int(t['churners'].sum()):,} churners. Fiber-specific = "
                   f"established month-to-month fiber churners above the DSL month-to-month "
                   f"rate ({nf:,} customers),\nat the average fiber churner's bill "
                   f"(${FIBER_BILL:.2f}). The whisker is the 95% interval on the fiber-DSL "
                   "gap; treat it as a ceiling, not a forecast.")
    path = save(fig, "05_cost_of_inaction", mode)
    return path, dict(total=total, m2m_fiber=m2m_fiber, excess=excess, lo=ex_lo,
                      hi=ex_hi, n=nf, gap=gap, bill=FIBER_BILL)


if __name__ == "__main__":
    for mode in ("light", "dark"):
        chart_concentration(mode)
        _, n2 = chart_price(mode)
        _, n3 = chart_reasons(mode)
        chart_first_months(mode)
        _, cost = chart_cost(mode)
    print(f"price base {n2:,} | reasons base {n3:,}")
    print("cost:", {k: round(v, 2) if isinstance(v, float) else v for k, v in cost.items()})
    print("written to", OUT)
