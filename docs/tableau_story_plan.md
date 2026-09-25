# Tableau churn story: build plan

**Deliverable:** a Tableau Story (Story Points) that presents
[story.md](story.md) as a linear readout. **Framework:** SIGNAL, all six moves
in order: Tableau Story Points are the one place in a BI tool that does linear
narrative. **Data:** `rpt_story_segments` and `rpt_story_cost_estimates`
(dbt exposure `churn_story_tableau`).

The rule that governs every decision below: **the story must show the same
numbers as `story.md`, to the decimal.** That is why it reads pre-aggregated
exhibits instead of recomputing from customer rows, and why the confidence
intervals come from SQL — Tableau has no native Wilson or Newcombe interval.

---

## 1. Data sources

| Source | Model | Rows | Used by |
| --- | --- | --: | --- |
| `Segments` | `dbt_dev.rpt_story_segments` | 58 | Story points 2–9: one exhibit per sheet |
| `Estimates` | `dbt_dev.rpt_story_cost_estimates` | 2 | Story point 9: the fiber-specific cost bar and its range |

- **Connector:** Google BigQuery, billing project `focus-appliance-507309-h8`.
  Point it at `dbt_dev` while building. Repoint to the production dataset once
  the marts are promoted (a data-source swap, no sheet rework).
- **Extract, not live.** Sixty rows change only when dbt runs, so an extract
  refreshed after each `dbt build` keeps the story fast and offline-safe.
- **Every sheet filters to one `exhibit_id`** — add it as a data-source filter
  on a duplicated source, or a sheet filter with "show only relevant values".
- **Do not join the two sources.** Story point 9 stacks two sheets on one fixed
  axis instead (see 4.9).

The parity test `tests/assert_story_parity.sql` guards the numbers upstream: if
a data refresh moves a headline figure, dbt warns before the extract refreshes.

---

## 2. Brand: Slate

From the personal design system, with one validated correction.

| Role | Hex | Use in Tableau |
| --- | --- | --- |
| Base | `#0F1B2A` | Worksheet, dashboard and story background |
| Text primary | `#F2F6FA` | Titles, values, row labels |
| Text secondary | `#8FA6BC` | Captions, axis labels, footers (6.90:1 on base — passes body text) |
| Border | `#3D4B5C` | Gridlines and axis rules only — **never text** (1.95:1) |
| **Accent** | `#4CC2A5` | The one series the story point is about |
| Grey | `#56687D` | Everything else |
| Light grey | `#8FA6BC` | A third step, **never placed beside the accent** |

**The correction.** The design system pairs the accent with `#8FA6BC` as "grey
for everything else". Validated on the Slate base, that pair fails: the two sit
at the same lightness, so deuteranopes see a ΔE of 5.1 (floor 6) and even full
colour vision gets 11.3 (floor 15). `#56687D` separates by lightness instead —
ΔE 23.5 and 25.5, and still above 3:1 against the base. Use it for every
de-emphasised mark.

**Custom palette** — add to `My Tableau Repository/Preferences.tps`:

```xml
<?xml version='1.0'?>
<workbook>
  <preferences>
    <color-palette name="Slate - focus" type="regular">
      <color>#4CC2A5</color>
      <color>#56687D</color>
      <color>#8FA6BC</color>
    </color-palette>
  </preferences>
</workbook>
```

**Typography.** Source Serif 4 (titles), Inter (text), JetBrains Mono (figures).
Tableau renders a font only where it is installed. Tableau Desktop is fine once
the fonts in `notebooks/fonts/` are installed. **Tableau Public and Server fall
back** unless the fonts are installed on the server. Choose one before building:

- **Tableau Server you control:** install the three fonts on the server.
- **Tableau Public:** use Georgia for titles and Tableau Book for everything
  else. Keep the brand in colour, not type, rather than ship a broken fallback.

**Formatting defaults** (Format → Workbook): gridlines `#3D4B5C` at the thinnest
weight, zero lines off, borders off, row and column dividers off. Mark labels
use text colours, never the series colour. The one exception is a label sitting
*inside* a filled mark: use `#0F1B2A` on the accent and `#F2F6FA` on the grey.

---

## 3. Story structure

Story size **1280 × 800**. Caption boxes carry the verb-sentence title of each
point. Read the captions alone, top to bottom, and the argument should hold.

| # | SIGNAL move | Caption (the story-point title) | Sheet | Exhibit |
| --- | --- | --- | --- | --- |
| 1 | Setting | Fiber on month-to-month is two-thirds of the billing lost to churn | Title dashboard | — |
| 2 | Interruption | Seniors churn at twice the rate, at every stage of tenure | Age × tenure dumbbell | 01 |
| 3 | Guilty party | Seven in ten seniors are on fiber | Product mix bars | 02 |
| 4 | Guilty party | At the same price, fiber churns far more than DSL | Price-band dumbbell | 03 |
| 5 | Narrow in | Fiber churners name a competitor, not price | Reason dumbbell + reason codes | 04 |
| 6 | Guilty party | Four month-to-month segments hold 88.6% of all churn | Concentration bars | 05 |
| 7 | Narrow in | Senior fiber customers churn at 78% on month-to-month, 1% on two-year | Contract × age dumbbell | 06 |
| 8 | Narrow in | The same customers leave from the first month, only faster | Slope chart | 07 |
| 9 | Ante | About $37,000 a month is specific to fiber | Cost bars + range | 08 + estimates |
| 10 | Landing | Three decisions, three owners | Asks dashboard | — |

**Chekhov's gun:** anything that cannot name its row in this table goes in an
appendix story point or nowhere.

---

## 4. Story points

Each point below gives: the mark and shelf layout, the focus rule (what gets
the accent), the labels, and the footer. **Every point carries a base footer**
("Base: …") in `#8FA6BC`, taken from `base_population` and the totals.

### 4.1 Setting — title dashboard

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ▬▬                                                                           │
│ CHURN · ONE QUARTER                                                          │
│ Fiber on month-to-month is two-thirds of the billing                         │
│ lost to churn — and price is not why they leave                              │
│                                                                              │
│ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ │
│ │ Customers      │ │ Churn rate     │ │ Lost billing   │ │ Fiber m2m      │ │
│ │ 7,043          │ │ 26.5%          │ │ $139.1k / mo   │ │ 68.7% of it    │ │
│ │ 1,869 churned  │ │ 21.2% after    │ │ 1,869 churners │ │ 1,107 churners │ │
│ │                │ │ month 3        │ │                │ │                │ │
│ └────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘ │
│                                                                              │
│ The decision this informs: where retention effort goes next, and whether     │
│ fiber churn should be met with price.                                        │
│ Base: all 7,043 customers, one quarter. A snapshot, not a trend.             │
└──────────────────────────────────────────────────────────────────────────────┘
```

- KPI tiles read from exhibit 05 (totals) and 08 (billing). Each tile has a
  label, a value and a context line. There is never a bare number.
- Value in JetBrains Mono, label in Inter, headline in Source Serif 4.

### 4.2 Exhibit 01 — seniors vs under-65 across tenure (dumbbell)

- **Rows:** `dim_2_value` (tenure band), sorted by `dim_2_sort`.
- **Columns:** `churn_rate` twice on a **synchronised** dual axis — circles on
  one, a line on the other with `dim_1_value` on Path. Synchronising keeps it
  one scale, so it is still a single-axis chart, not a dual-scale one.
- **Colour:** `[Focus]` = `dim_1_value = 'senior (65+)'` → accent, else grey.
- **Labels:** the senior value (bold, primary) and the under-65 value
  (secondary). Put each on its outer end, and the gap above the connector.
- **Tooltip:** rate with its Wilson interval (`churn_rate_lower`–`churn_rate_upper`)
  and n.
- **Footer:** Base: 5,992 established customers.

### 4.3 Exhibit 02 — what each age group buys (100% stacked bar)

- **Rows:** `dim_1_value` (age group). **Columns:** `share_of_dim_1_customers`,
  stacked by `dim_2_value`, sorted by `dim_2_sort`.
- **Colour:** fiber → accent, cable or DSL → `#56687D`, no internet →
  `#8FA6BC`. The accent never touches the light grey.
- **Labels inside segments, only where they fit.** Tableau clips rather than
  hides, so set the 4.9% senior no-internet label off and state it in the footer.

### 4.4 Exhibit 03 — fiber vs DSL at the same price (dumbbell)

- As 4.2, with `dim_2_value` = price band and focus = fiber.
- Annotation (Annotate → Area, beside the $88–100 row): "Fiber churn falls as
  the bill rises".
- **Footer:** Base: 2,496 established fiber and DSL customers in the three
  price bands where both are sold.

### 4.5 Exhibit 04 — what churners say (dumbbell + Speech)

- **Rows:** `dim_2_value` (reason category), sorted by fiber share
  descending. **Columns:** `share_of_dim_1_churners`.
- Bold row labels and value labels only on **competitor** and **price** — the
  two rows the argument uses.
- **Speech:** a text box beside the chart with the two reason codes verbatim —
  "competitor had better devices" (207) and "competitor made better offer"
  (204) — labelled *reason codes, not customers' own words*.
- **Footer:** Base: 1,543 fiber and DSL churners; difference in reason mix
  p = 0.03.

### 4.6 Exhibit 05 — where churn sits (bars)

- **Rows:** a combined field `[Segment]` = `dim_1_value + ' · ' + dim_2_value + ' · ' + dim_3_value`,
  showing the four month-to-month leaves plus one grouped "committed contracts"
  row (group the eight committed leaves in a calculated field).
- **Columns:** `share_of_exhibit_churners`. Colour: fiber → accent.
- **Reference band** or bracket annotation across the four month-to-month rows:
  "88.6% of all churn".
- Sub-label each row with customers and churn rate.

### 4.7 Exhibit 06 — seniors on fiber by contract (dumbbell)

- As 4.2, with `dim_1_value` = contract and focus = senior.
- **The two-year senior value is 2 churners of 197.** Say so in the caption or
  tooltip, and put the Wilson interval (0.3%–3.6%) on that point. This is the
  most dramatic number in the story and the thinnest.
- **Footer:** "Customers choose their contract, so this is an association, not
  the effect of one."

### 4.8 Exhibit 07 — the first three months (slope chart)

- **Columns:** `dim_1_value` (era), sorted by `dim_1_sort`. **Rows:** `churn_rate`.
- Line + circle, `dim_2_value` on Detail. Fiber → accent; others → grey.
- **No y-axis.** Every point is labelled, so the axis only repeats them.
  Show the end labels with the product name on the right.
- **Footer:** the 0–3 band holds no "stayed" customers — a new-cohort rate.

### 4.9 Exhibit 08 — cost of inaction (two stacked sheets, one axis)

Tableau cannot draw the three rows from one source, because two are actual
billing (`Segments`) and one is an estimate (`Estimates`). Build two sheets and
stack them in a dashboard container:

1. **Actual:** `Segments`, exhibit 08, `lost_monthly_charge` by `dim_1_value`.
2. **Estimate:** `Estimates`, `estimate_id = 'fiber_over_dsl'`,
   `excess_monthly_billing` as a bar, plus a Gantt mark from
   `excess_monthly_billing_lower` sized to (`upper − lower`) for the whisker.

Fix **both axes to 0–150,000** and hide the top sheet's axis, so the three bars
read as one chart. Senior estimate: a text line under the chart ("of which about
$9,800 a month is seniors — inside the fiber figure, not on top of it"), never
a fourth bar, because it would read as additive.

### 4.10 Landing — the asks

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ▬▬                                                                           │
│ WHAT WE DO NEXT                                                              │
│ Stop treating fiber churn as a pricing problem                               │
│                                                                              │
│  1  No blanket fiber discounts           Owner [name]   Decide by [date]     │
│  2  Pull competitor detail               Owner [name]   Report by [date]     │
│  3  Test a one-year contract offer,      Owner [name]   Launch by [date]     │
│     starting with senior fiber customers                                     │
│                                                                              │
│ The twist: fiber customers at a lower price churn more, not less.            │
│ Base: all 7,043 customers. Full recommendations: story.md, section 6.        │
└──────────────────────────────────────────────────────────────────────────────┘
```

A callback to story point 1's question, answered, plus the one thing that was
not expected going in. It ends in a decision, an owner and a date, not in
admiration.

---

## 5. Calculated fields

On `Segments`:

```text
[Focus]            // accent vs grey, per exhibit
CASE [Exhibit Id]
  WHEN '01' THEN [Dim 1 Value] = 'senior (65+)'
  WHEN '03' THEN [Dim 1 Value] = 'fiber optic'
  WHEN '04' THEN [Dim 1 Value] = 'fiber optic'
  WHEN '05' THEN [Dim 3 Value] = 'fiber'
  WHEN '06' THEN [Dim 2 Value] = 'senior (65+)'
  WHEN '07' THEN [Dim 2 Value] = 'fiber optic'
  ELSE FALSE
END

[Rate label]       // value with a thin-cell flag
STR(ROUND([Churn Rate] * 100, 1)) + '%' + IIF([Customers] < 100, '*', '')

[Interval label]   // for tooltips
STR(ROUND([Churn Rate Lower] * 100, 1)) + '–' + STR(ROUND([Churn Rate Upper] * 100, 1)) + '%'

[Segment]          // exhibit 05 rows: four month-to-month leaves + committed
IIF([Dim 2 Value] = 'month-to-month',
    [Dim 1 Value] + ' · ' + [Dim 2 Value] + ' · ' + [Dim 3 Value],
    'committed contracts')

[Gap pts]          // dumbbell gap label, exhibits 01 and 03
{ FIXED [Exhibit Id], [Dim 2 Value] :
    MAX(IIF([Focus], [Churn Rate], NULL)) - MAX(IIF(NOT [Focus], [Churn Rate], NULL)) } * 100
```

---

## 6. Build order

1. Install the fonts, or choose the fallback (section 2). Add the palette to
   `Preferences.tps`.
2. Connect both sources and extract. Set workbook formatting defaults.
3. Build the sheets for exhibits 01–08 as numbered, each with its footer.
4. Build the title and landing dashboards.
5. Assemble the story in the section 3 order and write the captions.
6. Run the QA checklist (section 7), then publish.

---

## 7. QA checklist

- [ ] Every value matches the table views in `story.md`. Spot-check: 21.2%,
      88.6%, 78.3%, $37.4k (range $31.5k–$42.9k).
- [ ] `dbt test --select assert_story_parity` passes before the extract refreshes.
- [ ] Every story point has a base footer.
- [ ] Captions alone, read top to bottom, carry the argument.
- [ ] One accent per point. The accent never touches `#8FA6BC`.
- [ ] No label clipped by a mark; thin cells (n < 100) carry `*`.
- [ ] The two-year senior figure shows 2 of 197 and its interval.
- [ ] The senior cost estimate is text, not a bar.
- [ ] Fonts render on the publishing target, or the fallback is applied
      throughout.
- [ ] SIGNAL pre-flight: latecomer can orient (1); pattern break stated (2);
      the mechanism's limit is stated — competitors, not yet which offer (4–5);
      cost has a range (9); ends in owner and date (10).

---

## 8. Open decisions

| Decision | Options | Default if not decided |
| --- | --- | --- |
| Publishing target | Tableau Public / Server / Desktop-only | Public, with the font fallback |
| Owners and dates for the asks | — | Placeholders stay visible, which blocks publishing |
| Dataset | `dbt_dev` / production | `dbt_dev` until the marts are promoted |
