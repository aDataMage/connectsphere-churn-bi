"""
Charts for docs/story.md, in the Slate personal brand.

Every figure is queried live from the dbt staging models, so the images can be
rebuilt from the data rather than from numbers typed into a script:

    python notebooks/story_charts.py

Brand: Slate base, one accent for the series the story is about, grey for
everything else. Source Serif 4 for headlines, Inter for text, JetBrains Mono
for figures. The fonts live in notebooks/fonts (SIL Open Font License).

Colour was checked with the dataviz palette validator on the Slate surface:
  - accent #4CC2A5 against the brand grey #8FA6BC FAILS (deutan dE 5.1, normal
    dE 11.3) - they sit at almost the same lightness, so "the series that
    matters" and "everything else" can be confused. The de-emphasis grey is
    therefore #56687D (deutan dE 23.5, normal dE 25.5, >= 3:1 on the base).
  - #8FA6BC is still used as a third, lighter grey, but never beside the accent.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from google.cloud import bigquery
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch, Rectangle
from statsmodels.stats.proportion import confint_proportions_2indep

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "img"
FONTS = Path(__file__).resolve().parent / "fonts"
OUT.mkdir(parents=True, exist_ok=True)
load_dotenv(ROOT / ".env")
client = bigquery.Client(project="focus-appliance-507309-h8")


def run_query(sql):
    return client.query(sql).to_dataframe()


# --------------------------------------------------------------------- brand
C = dict(
    surface="#0F1B2A",   # Slate base
    ink="#F2F6FA",       # text primary   15.98:1
    ink2="#8FA6BC",      # text secondary  6.90:1
    grid="#3D4B5C",      # border - gridlines only, never text (1.95:1)
    accent="#4CC2A5",    # the series the story is about
    grey="#56687D",      # everything else - validated against the accent
    grey2="#8FA6BC",     # a lighter grey step, never placed beside the accent
)


def font(name, size):
    """Exact static weight from notebooks/fonts - matplotlib can't pick weights
    out of a variable font, so each weight is its own file."""
    return FontProperties(fname=str(FONTS / f"{name}.ttf"), size=size)


SERIF, SANS, SANS_B, MONO, MONO_B = (
    "source-serif-4-600", "inter-400", "inter-600", "jetbrains-mono-400",
    "jetbrains-mono-600")
DPI_LAYOUT, DPI_OUT = 100, 220
W = 8.6  # inches


class Canvas:
    """A figure laid out in inches, so the header block, legend and footer sit at
    the same offsets on every chart regardless of its height."""

    def __init__(self, height, left, right, top, bottom):
        self.h = height
        self.fig = plt.figure(figsize=(W, height), dpi=DPI_LAYOUT, facecolor=C["surface"])
        self.ax = self.fig.add_axes([left / W, bottom / height,
                                     1 - (left + right) / W, 1 - (top + bottom) / height])
        ax = self.ax
        ax.set_facecolor(C["surface"])
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(C["grid"])
        ax.tick_params(colors=C["ink2"], length=0, pad=7)

    def y(self, from_top):
        return 1 - from_top / self.h

    def header(self, eyebrow, title, subtitle):
        fig, x = self.fig, 0.32 / W
        # the brand's accent rule, then a tracked uppercase eyebrow
        fig.patches.append(Rectangle((x, self.y(0.30)), 0.42 / W, 0.035 / self.h,
                                     color=C["accent"], transform=fig.transFigure,
                                     figure=fig))
        self.tracked(eyebrow.upper(), x, self.y(0.44))
        fig.text(x, self.y(0.60), title, fontproperties=font(SERIF, 15.5),
                 color=C["ink"], va="top")
        fig.text(x, self.y(1.00), subtitle, fontproperties=font(SANS, 9.5),
                 color=C["ink2"], va="top")

    def tracked(self, s, x, y, size=7.8, spacing_px=1.9):
        """Letter-spaced eyebrow - matplotlib has no letter-spacing, so each
        glyph is placed and measured in turn."""
        fig = self.fig
        r = fig.canvas.get_renderer()
        for ch in s:
            t = fig.text(x, y, ch, fontproperties=font(SANS_B, size), color=C["ink2"],
                         va="top")
            x += (t.get_window_extent(r).width + spacing_px) / fig.bbox.width

    def legend(self, items, from_top=1.42):
        fig, x = self.fig, 0.32 / W
        r = fig.canvas.get_renderer()
        for label, color in items:
            fig.patches.append(Rectangle((x, self.y(from_top) - 0.055 / self.h),
                                         0.13 / W, 0.13 / self.h, color=color,
                                         transform=fig.transFigure, figure=fig))
            t = fig.text(x + 0.2 / W, self.y(from_top), label,
                         fontproperties=font(SANS, 9), color=C["ink2"], va="center")
            x += (0.2 / W) + t.get_window_extent(r).width / fig.bbox.width + 0.32 / W

    def footer(self, text):
        self.fig.text(0.32 / W, 0.2 / self.h, text, fontproperties=font(SANS, 7.8),
                      color=C["ink2"], va="bottom", linespacing=1.5)

    def mono_ticks(self, axis="x"):
        labels = self.ax.get_xticklabels() if axis == "x" else self.ax.get_yticklabels()
        for lbl in labels:
            lbl.set_fontproperties(font(MONO, 8.5))

    def save(self, name):
        path = OUT / f"{name}.png"
        self.fig.savefig(path, dpi=DPI_OUT, facecolor=C["surface"])
        plt.close(self.fig)
        return path


def px(ax):
    """Data units per logical pixel, x and y, for the axes as laid out."""
    bb = ax.get_window_extent()
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    return (x1 - x0) / bb.width, abs(y1 - y0) / bb.height


def hbar(ax, y, value, color, thick_px=20, radius_px=4, x0=0):
    """Horizontal bar: <=24px thick, 4px rounded data-end, square at baseline."""
    xpp, ypp = px(ax)
    h, r = thick_px * ypp, radius_px * xpp
    ax.add_patch(FancyBboxPatch((x0, y - h / 2), value, h,
                                boxstyle=f"round,pad=0,rounding_size={r}",
                                mutation_aspect=ypp / xpp, fc=color, ec="none", zorder=3))
    ax.add_patch(Rectangle((x0, y - h / 2), min(value, 2 * r), h, fc=color, ec="none",
                           zorder=3))


def dot(ax, x, y, color, size=9.5):
    """>=8px marker with a 2px ring in the surface colour."""
    ax.plot(x, y, "o", ms=size, mfc=color, mec=C["surface"], mew=2, zorder=5)


def backing():
    """Surface-coloured pad behind a label that sits over a gridline."""
    return dict(boxstyle="square,pad=0.15", fc=C["surface"], ec="none")


def grid(ax, axis="x"):
    ax.grid(axis=axis, color=C["grid"], linewidth=1, linestyle="-", zorder=0)
    ax.set_axisbelow(True)


def pct_axis(cv, lo, hi, step):
    ax = cv.ax
    ax.set_xlim(lo, hi)
    ax.set_xticks(range(lo, hi + 1, step))
    ax.set_xticklabels([f"{v}%" for v in range(lo, hi + 1, step)])
    cv.mono_ticks()


def dumbbell_labels(ax, y, a, b, fmt="{:.1f}%", pad=1.4, a_bold=True):
    """Label each end on its outer side, so neither label sits on the connector.
    A left label that would run past the axis start goes above its dot instead of
    into the row-label gutter."""
    lo_v, hi_v = sorted([a, b])
    r = ax.figure.canvas.get_renderer()
    xpp, _ = px(ax)
    for v in (a, b):
        outer_right = v == hi_v and lo_v != hi_v
        bold = (v == a) and a_bold
        t = ax.text(v + pad if outer_right else v - pad, y, fmt.format(v),
                    ha="left" if outer_right else "right", va="center",
                    fontproperties=font(MONO_B if bold else MONO, 9 if bold else 8.5),
                    color=C["ink"] if bold else C["ink2"], bbox=backing(), zorder=6)
        if not outer_right:
            width = t.get_window_extent(r).width * xpp
            if v - pad - width < ax.get_xlim()[0]:
                t.set_position((v, y - 0.2))
                t.set_ha("center")
                t.set_va("bottom")


# ---------------------------------------------------------------------- data
J = """FROM `dbt_dev.stg_telco__services` se
JOIN `dbt_dev.stg_telco__status` st USING (customer_id)
JOIN `dbt_dev.stg_telco__demographics` d USING (customer_id)"""
AGE = "IF(d.age < 65, 'non-senior', 'senior')"
EST = "se.tenure_in_months > 3"

AGE_TENURE = run_query(f"""
SELECT {AGE} AS age,
  CASE WHEN se.tenure_in_months <= 12 THEN '4-12'
       WHEN se.tenure_in_months <= 24 THEN '13-24'
       WHEN se.tenure_in_months <= 48 THEN '25-48' ELSE '49+' END AS band,
  COUNT(*) AS customers, COUNTIF(st.churn_label) AS churners
{J} WHERE {EST} GROUP BY age, band""")

AGE_MIX = run_query(f"""
SELECT {AGE} AS age,
  CASE WHEN NOT se.internet_service THEN 'no internet'
       WHEN se.internet_type = 'fiber optic' THEN 'fiber'
       ELSE 'cable or dsl' END AS product,
  COUNT(*) AS customers
{J} WHERE {EST} GROUP BY age, product""")

PRICE = run_query(f"""
SELECT se.internet_type,
  CASE WHEN se.monthly_charge < 75 THEN '$58-75'
       WHEN se.monthly_charge < 88 THEN '$75-88' ELSE '$88-100' END AS band,
  COUNT(*) AS customers, COUNTIF(st.churn_label) AS churners
{J} WHERE {EST} AND se.internet_type IN ('fiber optic', 'dsl')
  AND se.monthly_charge >= 58 AND se.monthly_charge < 100
GROUP BY se.internet_type, band""")

REASONS = run_query(f"""
SELECT se.internet_type, st.churn_category, COUNT(*) AS churners
{J} WHERE st.churn_label AND se.internet_type IN ('fiber optic', 'dsl')
GROUP BY se.internet_type, st.churn_category""")

CELLS = run_query(f"""
SELECT {AGE} AS age,
  IF(se.internet_type = 'fiber optic', 'fiber', 'not fiber') AS fiber,
  se.contract,
  COUNT(*) AS customers, COUNTIF(st.churn_label) AS churners,
  SUM(IF(st.churn_label, se.monthly_charge, 0)) AS lost_monthly
{J} WHERE {EST} GROUP BY age, fiber, se.contract""")

M2M = run_query(f"""
SELECT se.internet_type, COUNT(*) AS customers, COUNTIF(st.churn_label) AS churners
{J} WHERE {EST} AND se.contract = 'month-to-month'
  AND se.internet_type IN ('fiber optic', 'dsl')
GROUP BY se.internet_type""").set_index("internet_type")

FIBER_BILL = run_query(f"""
SELECT AVG(se.monthly_charge) AS b {J}
WHERE st.churn_label AND se.internet_type = 'fiber optic'""")["b"].item()

TREE = run_query(f"""
SELECT IF(se.tenure_in_months <= 3, 'New', 'Established') AS era, se.contract,
  IF(se.internet_type = 'fiber optic', 'fiber', 'not fiber') AS fiber,
  COUNT(*) AS customers, COUNTIF(st.churn_label) AS churners,
  SUM(IF(st.churn_label, se.monthly_charge, 0)) AS lost_monthly
{J} GROUP BY era, se.contract, fiber""")

ERAS = run_query(f"""
SELECT IF(se.internet_service, se.internet_type, 'no internet') AS internet_type,
  IF(se.tenure_in_months <= 3, 'new', 'established') AS era,
  COUNT(*) AS customers, COUNTIF(st.churn_label) AS churners
{J} GROUP BY internet_type, era""")


# ------------------------------------------------------------------ 01 age
def chart_age_tenure():
    t = AGE_TENURE.copy()
    t["rate"] = t["churners"] / t["customers"] * 100
    bands = ["4-12", "13-24", "25-48", "49+"]
    w = t.pivot(index="band", columns="age", values="rate").loc[bands]
    n = t.pivot(index="band", columns="age", values="customers").loc[bands]

    cv = Canvas(5.0, left=1.55, right=0.45, top=1.72, bottom=1.0)
    ax = cv.ax
    pct_axis(cv, 0, 60, 10)
    ax.set_ylim(len(bands) - 0.45, -0.6)
    grid(ax)
    ax.set_yticks([])
    for i, b in enumerate(bands):
        s, o = w.loc[b, "senior"], w.loc[b, "non-senior"]
        ax.plot([o, s], [i, i], color=C["grid"], lw=2, solid_capstyle="round", zorder=2)
        dot(ax, o, i, C["grey"])
        dot(ax, s, i, C["accent"])
        dumbbell_labels(ax, i, s, o)
        ax.text((s + o) / 2, i - 0.24, f"+{s - o:.1f} pts", ha="center", va="bottom",
                fontproperties=font(MONO, 8), color=C["ink2"], bbox=backing())
        ax.text(-3.2, i - 0.1, f"{b.replace('-', '–')} months", ha="right",
                va="center", fontproperties=font(SANS, 10), color=C["ink"])
        ax.text(-3.2, i + 0.2, f"{int(n.loc[b, 'senior']):,} seniors",
                ha="right", va="center", fontproperties=font(SANS, 7.8), color=C["ink2"])

    tot = t.groupby("age")[["customers", "churners"]].sum()
    sr = tot.loc["senior", "churners"] / tot.loc["senior", "customers"] * 100
    nr = tot.loc["non-senior", "churners"] / tot.loc["non-senior", "customers"] * 100
    cv.header("01 · Age",
              "Seniors churn at about twice the rate, at every stage of tenure",
              f"Churn rate by tenure band. Overall: seniors {sr:.1f}%, everyone else {nr:.1f}%.")
    cv.legend([("Seniors (65+)", C["accent"]), ("Under 65", C["grey"])])
    cv.footer(f"Base: {int(tot['customers'].sum()):,} established customers "
              "(tenure > 3 months), one quarter.")
    return cv.save("01_age_tenure")


# ---------------------------------------------------------- 02 age -> product
def chart_age_mix():
    m = AGE_MIX.copy()
    m["share"] = m["customers"] / m.groupby("age")["customers"].transform("sum") * 100
    w = m.pivot(index="age", columns="product", values="share")
    n = m.groupby("age")["customers"].sum()
    rows = [("senior", "Seniors (65+)"), ("non-senior", "Under 65")]
    segs = [("fiber", "Fiber", C["accent"], C["surface"]),
            ("cable or dsl", "Cable or DSL", C["grey"], C["ink"]),
            ("no internet", "No internet", C["grey2"], C["surface"])]

    cv = Canvas(3.6, left=1.55, right=0.45, top=1.72, bottom=0.62)
    ax = cv.ax
    ax.set_xlim(0, 100)
    ax.set_ylim(1.6, -0.6)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["bottom"].set_visible(False)
    xpp, ypp = px(ax)
    gap, h = 1 * xpp, 26 * ypp  # a 2px surface gap: 1px off each touching edge
    r = cv.fig.canvas.get_renderer()
    for i, (key, label) in enumerate(rows):
        x = 0
        for j, (seg, _, color, text_color) in enumerate(segs):
            v = w.loc[key, seg]
            left = x + (gap if j else 0)
            width = v - (gap if j else 0) - (gap if j < len(segs) - 1 else 0)
            ax.add_patch(Rectangle((left, i - h / 2), width, h, fc=color, ec="none",
                                   zorder=3))
            t = ax.text(x + v / 2, i, f"{v:.1f}%", ha="center", va="center",
                        fontproperties=font(MONO_B, 9), color=text_color, zorder=4)
            # measure first: a label that won't fit its segment is removed, not clipped
            if t.get_window_extent(r).width > (width / xpp) - 10:
                t.remove()
            x += v
        ax.text(-2.2, i - 0.12, label, ha="right", va="center",
                fontproperties=font(SANS, 10), color=C["ink"])
        ax.text(-2.2, i + 0.24, f"{int(n[key]):,} customers", ha="right", va="center",
                fontproperties=font(SANS, 7.8), color=C["ink2"])

    cv.header("02 · Age › internet type",  # '→' is outside Inter's latin subset
              "Seven in ten seniors are on fiber, against under four in ten of everyone else",
              "What each age group buys, as a share of that group's customers.")
    cv.legend([(lbl, color) for _, lbl, color, _ in segs])
    cv.footer(f"Base: {int(n.sum()):,} established customers. "
              f"No-internet share: seniors {w.loc['senior', 'no internet']:.1f}%, "
              f"under 65 {w.loc['non-senior', 'no internet']:.1f}%.")
    return cv.save("02_age_product_mix")


# ------------------------------------------------------------- 03 price
def chart_price():
    p = PRICE.copy()
    p["rate"] = p["churners"] / p["customers"] * 100
    bands = ["$58-75", "$75-88", "$88-100"]
    fib = p[p.internet_type == "fiber optic"].set_index("band").loc[bands, "rate"]
    dsl = p[p.internet_type == "dsl"].set_index("band").loc[bands, "rate"]

    cv = Canvas(4.8, left=1.25, right=0.45, top=1.72, bottom=1.0)
    ax = cv.ax
    pct_axis(cv, 0, 60, 10)
    ax.set_ylim(2.5, -0.6)
    grid(ax)
    ax.set_yticks([])
    for i, b in enumerate(bands):
        f, d = fib[b], dsl[b]
        ax.plot([d, f], [i, i], color=C["grid"], lw=2, solid_capstyle="round", zorder=2)
        dot(ax, d, i, C["grey"])
        dot(ax, f, i, C["accent"])
        dumbbell_labels(ax, i, f, d)
        ax.text((d + f) / 2, i - 0.22, f"+{f - d:.1f} pts", ha="center", va="bottom",
                fontproperties=font(MONO, 8), color=C["ink2"], bbox=backing())
        ax.text(-3.2, i, b.replace("-", "–"), ha="right", va="center",
                fontproperties=font(MONO, 9.5), color=C["ink"])
    ax.text(fib.iloc[-1] + 9, 2, "Fiber churn falls\nas the bill rises",
            fontproperties=font(SANS, 8.8), color=C["ink2"], va="center", linespacing=1.35,
            bbox=backing())

    n = int(p["customers"].sum())
    cv.header("03 · Internet type",
              "At the same monthly price, fiber customers churn far more than DSL",
              "Churn rate by monthly charge, in the three price bands where both are sold.")
    cv.legend([("Fiber", C["accent"]), ("DSL", C["grey"])])
    cv.footer(f"Base: {n:,} established fiber and DSL customers. Gaps are fiber minus "
              "DSL, in percentage points.")
    return cv.save("03_price_bands"), n


# ----------------------------------------------------------- 04 reasons
def chart_reasons():
    r = REASONS.copy()
    r["share"] = r["churners"] / r.groupby("internet_type")["churners"].transform("sum") * 100
    w = r.pivot(index="churn_category", columns="internet_type", values="share")
    w = w.sort_values("fiber optic", ascending=False)
    story = {"competitor", "price"}

    cv = Canvas(5.1, left=1.55, right=0.45, top=1.72, bottom=1.05)
    ax = cv.ax
    pct_axis(cv, 0, 60, 10)
    ax.set_ylim(len(w) - 0.5, -0.6)
    grid(ax)
    ax.set_yticks([])
    for i, (cat, row) in enumerate(w.iterrows()):
        f, d = row["fiber optic"], row["dsl"]
        hot = cat in story
        ax.text(-3.2, i, cat.capitalize(), ha="right", va="center",
                fontproperties=font(SANS_B if hot else SANS, 10),
                color=C["ink"] if hot else C["ink2"])
        ax.plot([min(f, d), max(f, d)], [i, i], color=C["grid"], lw=2,
                solid_capstyle="round", zorder=2)
        dot(ax, d, i, C["grey"])
        dot(ax, f, i, C["accent"])
        if hot:
            dumbbell_labels(ax, i, f, d)

    n = int(r["churners"].sum())
    cv.header("04 · Internet type",
              "Fiber churners name a competitor more often, and price no more often",
              "Share of each product's churners, by the reason recorded at cancellation.")
    cv.legend([("Fiber", C["accent"]), ("DSL", C["grey"])])
    cv.footer(f"Base: {n:,} fiber and DSL churners; difference in reason mix p = 0.03.\n"
              "Reasons are chosen from a fixed list at cancellation - reason codes, not "
              "customers' own words.")
    return cv.save("04_churn_reasons"), n


# ------------------------------------------------------ 05 convergence
def chart_convergence():
    c = CELLS[CELLS.fiber == "fiber"].copy()
    c["rate"] = c["churners"] / c["customers"] * 100
    order = ["month-to-month", "one year", "two year"]
    w = c.pivot(index="contract", columns="age", values="rate").loc[order]
    n = c.pivot(index="contract", columns="age", values="customers").loc[order]

    cv = Canvas(4.8, left=1.75, right=0.45, top=1.72, bottom=1.0)
    ax = cv.ax
    pct_axis(cv, 0, 90, 10)
    ax.set_ylim(2.5, -0.6)
    grid(ax)
    ax.set_yticks([])
    for i, k in enumerate(order):
        s, o = w.loc[k, "senior"], w.loc[k, "non-senior"]
        ax.plot([min(s, o), max(s, o)], [i, i], color=C["grid"], lw=2,
                solid_capstyle="round", zorder=2)
        dot(ax, o, i, C["grey"])
        dot(ax, s, i, C["accent"])
        dumbbell_labels(ax, i, s, o)
        ax.text(-4.5, i - 0.1, k.capitalize(), ha="right", va="center",
                fontproperties=font(SANS, 10), color=C["ink"])
        ax.text(-4.5, i + 0.22, f"{int(n.loc[k, 'senior']):,} senior fiber customers",
                ha="right", va="center", fontproperties=font(SANS, 7.8), color=C["ink2"])

    cv.header("06 · Contract › age",
              "Senior fiber customers churn at 78% on month-to-month, 1% on two-year",
              "Churn rate of fiber customers, by contract and age.")
    cv.legend([("Seniors on fiber", C["accent"]), ("Under 65 on fiber", C["grey"])])
    two = c[(c.contract == "two year") & (c.age == "senior")].iloc[0]
    cv.footer(f"Base: {int(n.values.sum()):,} established fiber customers. The two-year "
              f"senior rate rests on {int(two.churners)} churners of {int(two.customers)}.\n"
              "Customers choose their contract, so this is an association, not the effect "
              "of one.")
    return cv.save("06_contract_convergence")


# --------------------------------------------------------------- 08 cost
def chart_cost():
    """The story's cost of inaction: all billing lost, the month-to-month fiber
    share of it, and the part attributable to fiber over DSL, with its range."""
    t = TREE
    total = t["lost_monthly"].sum()
    mf = t[(t.contract == "month-to-month") & (t.fiber == "fiber")]
    kf, nf = M2M.loc["fiber optic", ["churners", "customers"]].astype(int)
    kd, nd = M2M.loc["dsl", ["churners", "customers"]].astype(int)
    x = excess(kf, nf, kd, nd, FIBER_BILL)
    rows = [
        ("All billing lost to churn", f"{int(t['churners'].sum()):,} churners", total,
         C["grey"]),
        ("Month-to-month fiber customers",
         f"{int(mf['churners'].sum()):,} churners · "
         f"{mf['lost_monthly'].sum() / total * 100:.1f}% of the total",
         mf["lost_monthly"].sum(), C["grey"]),
        ("Fiber-specific: above the DSL rate",
         f"~{x['churners']:.0f} churners (range {x['churners_lo']:.0f}–{x['churners_hi']:.0f})",
         x["monthly"], C["accent"]),
    ]

    cv = Canvas(4.4, left=2.5, right=1.0, top=1.45, bottom=1.0)
    ax = cv.ax
    ax.set_xlim(0, 150_000)
    ax.set_ylim(len(rows) - 0.45, -0.6)
    grid(ax)
    ticks = range(0, 150_001, 25_000)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"${v // 1000}k" for v in ticks])
    cv.mono_ticks()
    ax.set_yticks([])
    for i, (label, sub, v, color) in enumerate(rows):
        hbar(ax, i, v, color)
        ax.text(-3500, i - 0.12, label, ha="right", va="center",
                fontproperties=font(SANS_B if color == C["accent"] else SANS, 9.8),
                color=C["ink"])
        ax.text(-3500, i + 0.2, sub, ha="right", va="center",
                fontproperties=font(SANS, 7.8), color=C["ink2"])
    for i in (0, 1):
        ax.text(rows[i][2] + 2500, i, f"${rows[i][2] / 1000:,.1f}k", va="center",
                fontproperties=font(MONO_B, 9), color=C["ink"], bbox=backing())
    # the estimate carries its interval as a whisker instead of a bare value
    lo, hi, y = x["monthly_lo"], x["monthly_hi"], len(rows) - 1
    ax.plot([lo, hi], [y, y], color=C["ink"], lw=1.4, zorder=6)
    for edge in (lo, hi):
        ax.plot([edge, edge], [y - 0.13, y + 0.13], color=C["ink"], lw=1.4, zorder=6)
    ax.text(hi + 2500, y, f"${x['monthly'] / 1000:,.1f}k", va="center",
            fontproperties=font(MONO_B, 9), color=C["ink"], bbox=backing())
    ax.text(hi + 2500, y + 0.29, f"range \\${lo / 1000:,.1f}k–\\${hi / 1000:,.1f}k",
            va="center", fontproperties=font(MONO, 7.8), color=C["ink2"], bbox=backing())

    cv.header("08 · Cost",
              "About $37,000 a month of lost billing is specific to fiber",
              "Monthly charge of the customers who churned. Each bar is a subset of the one above.")
    cv.footer(f"Base: all {int(t['churners'].sum()):,} churners. Fiber-specific = established "
              f"month-to-month fiber churners above the DSL month-to-month rate ({nf:,} "
              f"customers),\nat the average fiber churner's bill (\\${FIBER_BILL:.2f}). The "
              "whisker is the 95% interval on the fiber-DSL gap; treat it as a ceiling, not a "
              "forecast.")
    return cv.save("08_cost_of_inaction"), dict(
        total=total, m2m_fiber=mf["lost_monthly"].sum(), **x)


# ----------------------------------------------------- appendix charts
def chart_tree():
    t = TREE.copy()
    total_k = t["churners"].sum()
    m = t[t.contract == "month-to-month"].copy()
    m["share"] = m["churners"] / total_k * 100
    m = m.sort_values("share", ascending=False)
    rest = t[t.contract != "month-to-month"]
    rows = [(f"{r.era} · month-to-month · {r.fiber}",
             f"{int(r.customers):,} customers · {r.churners / r.customers * 100:.1f}% churn",
             r.share, C["accent"] if r.fiber == "fiber" else C["grey"])
            for r in m.itertuples()]
    rows.append(("Eight committed-contract segments",
                 f"{int(rest.customers.sum()):,} customers · "
                 f"{rest.churners.sum() / rest.customers.sum() * 100:.1f}% churn",
                 rest.churners.sum() / total_k * 100, C["grey"]))

    cv = Canvas(5.5, left=2.95, right=1.05, top=1.72, bottom=1.0)
    ax = cv.ax
    pct_axis(cv, 0, 50, 10)
    ax.set_ylim(len(rows) - 0.45, -0.6)
    grid(ax)
    ax.set_yticks([])
    for i, (label, sub, share, color) in enumerate(rows):
        hbar(ax, i, share, color)
        ax.text(share + 0.8, i, f"{share:.1f}%", va="center",
                fontproperties=font(MONO_B, 9), color=C["ink"], bbox=backing())
        ax.text(-1.4, i - 0.12, label, ha="right", va="center",
                fontproperties=font(SANS, 9.8), color=C["ink"])
        ax.text(-1.4, i + 0.22, sub, ha="right", va="center",
                fontproperties=font(SANS, 7.8), color=C["ink2"])
    cum = sum(r[2] for r in rows[:4])
    ax.plot([48, 48.8, 48.8, 48], [-0.25, -0.25, 3.25, 3.25], color=C["ink2"], lw=1,
            clip_on=False)
    ax.text(49.6, 1.5, f"{cum:.1f}%\nof all\nchurn", va="center",
            fontproperties=font(MONO_B, 9), color=C["ink"], linespacing=1.25, clip_on=False,
            bbox=backing())

    cv.header("05 · Contract",
              "Four month-to-month segments hold 88.6% of all churn",
              f"Share of all {int(total_k):,} churners. Every customer sits in exactly one "
              "segment, so the shares add to 100%.")
    cv.legend([("Fiber", C["accent"]), ("Not fiber, or on a committed contract", C["grey"])])
    cv.footer(f"Base: all {int(t.customers.sum()):,} customers, including the first three "
              "months. New = first three months of tenure.")
    return cv.save("05_churn_concentration")


def chart_first_months():
    e = ERAS.copy()
    e["rate"] = e["churners"] / e["customers"] * 100
    w = e.pivot(index="internet_type", columns="era", values="rate")
    order = ["fiber optic", "cable", "dsl", "no internet"]
    names = {"fiber optic": "Fiber", "cable": "Cable", "dsl": "DSL", "no internet": "No internet"}

    cv = Canvas(5.2, left=1.7, right=2.35, top=1.72, bottom=0.95)
    ax = cv.ax
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(0, 85)
    ax.spines["bottom"].set_visible(False)
    ax.set_yticks([])  # every point is labelled - the axis would only repeat them
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["First three months", "Established (4+ months)"])
    for lbl in ax.get_xticklabels():
        lbl.set_fontproperties(font(SANS, 10))
        lbl.set_color(C["ink"])
    for key in reversed(order):
        new, est = w.loc[key, "new"], w.loc[key, "established"]
        color = C["accent"] if key == "fiber optic" else C["grey"]
        ax.plot([0, 1], [new, est], color=color, lw=2, zorder=3, solid_capstyle="round")
        dot(ax, 0, new, color)
        dot(ax, 1, est, color)
        ax.text(-0.045, new, f"{new:.1f}%", ha="right", va="center",
                fontproperties=font(MONO, 8.8), color=C["ink"])
        ax.text(1.045, est, f"{est:.1f}%", ha="left", va="center",
                fontproperties=font(MONO, 8.8), color=C["ink"])
        ax.text(1.2, est, names[key], ha="left", va="center",
                fontproperties=font(SANS_B if key == "fiber optic" else SANS, 9.5),
                color=C["ink"])

    cv.header("07 · The first three months",
              "Every product churns faster early on, in the same order",
              "Churn rate by internet type, new against established customers.")
    cv.legend([("Fiber", C["accent"]), ("Cable, DSL, no internet", C["grey"])])
    cv.footer(f"Base: all {int(e.customers.sum()):,} customers. The first-three-month band "
              "holds no 'stayed' customers, only those who left\nand those who just joined, "
              "so its rate describes a new cohort, not a like-for-like comparison.")
    return cv.save("07_first_months")


# ------------------------------------------------------ estimates
def excess(k1, n1, k0, n0, bill):
    """Churners above the comparison group's rate, and what they bill a month.
    The range carries the 95% Newcombe interval on the rate gap."""
    gap = k1 / n1 - k0 / n0
    lo, hi = confint_proportions_2indep(k1, n1, k0, n0, compare="diff", method="newcomb")
    return dict(gap=gap * 100, gap_lo=lo * 100, gap_hi=hi * 100, n=n1,
                churners=n1 * gap, churners_lo=n1 * lo, churners_hi=n1 * hi,
                monthly=n1 * gap * bill, monthly_lo=n1 * lo * bill,
                monthly_hi=n1 * hi * bill, bill=bill)


if __name__ == "__main__":
    for f in (chart_age_tenure, chart_age_mix, chart_convergence,
              chart_tree, chart_first_months):
        f()
    _, n_price = chart_price()
    _, n_reasons = chart_reasons()
    _, cost = chart_cost()

    kf, nf = M2M.loc["fiber optic", ["churners", "customers"]].astype(int)
    kd, nd = M2M.loc["dsl", ["churners", "customers"]].astype(int)
    fiber_x = excess(kf, nf, kd, nd, FIBER_BILL)

    fm = CELLS[(CELLS.fiber == "fiber") & (CELLS.contract == "month-to-month")].set_index("age")
    s, o = fm.loc["senior"], fm.loc["non-senior"]
    senior_bill = s["lost_monthly"] / s["churners"]
    senior_x = excess(int(s["churners"]), int(s["customers"]), int(o["churners"]),
                      int(o["customers"]), senior_bill)

    fmt = lambda d: {k: round(float(v), 2) for k, v in d.items()}
    print("bases: price", n_price, "| reasons", n_reasons)
    print("cost layers:", fmt(cost))
    print("fiber-specific (m2m fiber vs DSL):", fmt(fiber_x))
    print("senior-specific (m2m fiber, senior vs under 65):", fmt(senior_x))
    print("written to", OUT)
