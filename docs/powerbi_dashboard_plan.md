# Power BI churn analytics dashboard: build plan

**Deliverable:** a self-directed analytical dashboard for exploring churn by any
segment. It is not a retelling of [story.md](story.md). The story is read once;
the dashboard is opened repeatedly by people asking their own questions.
**Framework:** SIGNAL moves S, G and N only — structure and framing, not
suspense. A narrative arc in a dashboard is friction by the fortieth visit.
**Data:** `fct_customer_churn`, `dim_geography`, `rpt_story_cost_estimates`
(dbt exposure `churn_analytics_powerbi`).

| Page | SIGNAL move | Job |
| --- | --- | --- |
| 1. Overview | Setting | Where churn stands and where it sits, for whatever slice is selected |
| 2. Drivers | Guilty party | What moves churn, with the fiber-vs-DSL and age-by-contract views |
| 3. Reasons and cost | Guilty party | What churners say, and what the churn costs |
| 4. Customer detail | Narrow in | Drillthrough to the actual customers behind any number |

---

## 1. Data model

A star schema: one fact, one dimension, one disconnected estimates table.

```
                    ┌──────────────────────┐
                    │ dim_geography        │  1,626 rows · one per zip
                    │ zip_code (PK)        │
                    │ city, density_class  │
                    └──────────┬───────────┘
                               │ 1
                               │
                               │ *  single direction
                    ┌──────────┴───────────┐
                    │ fct_customer_churn   │  7,043 rows · one per customer
                    │ customer_id (PK)     │
                    │ zip_code (FK)        │
                    │ bands, flags, money  │
                    └──────────────────────┘

                    ┌──────────────────────────┐
                    │ rpt_story_cost_estimates │  2 rows · disconnected
                    └──────────────────────────┘  (feeds the cost card only)
```

- **Storage mode: Import.** At 7,043 rows, DirectQuery buys nothing and costs
  every interaction a BigQuery round trip. Schedule a refresh after each
  `dbt build`.
- **Connector:** Google BigQuery, project `focus-appliance-507309-h8`, dataset
  `dbt_dev` while building. Repoint to production once the marts are promoted.
  BigQuery is a cloud source, so no gateway is needed.
- **Why the band columns sit on the fact instead of in their own dimensions:**
  there is one fact table, so separate band dimensions would add joins with
  nothing to share. `dim_geography` earns its place: it carries attributes
  (city, population, coordinates) that belong to zips, not customers.
- **Estimates table:** no relationship. It holds two pre-computed estimates,
  and slicing them by segment would be meaningless. The cost card says so.

### Model settings

| Setting | Columns |
| --- | --- |
| **Sort by column** | `age_group` → `age_group_sort`, `era` → `era_sort`, `tenure_band` → `tenure_band_sort`, `internet_type` → `internet_type_sort`, `addon_band` → `addon_band_sort`, `streaming_band` → `streaming_band_sort`, `contract` → `contract_sort`, `price_band` → `price_band_sort`, `density_class` → `density_class_sort` |
| **Hide from report view** | every `*_sort` column, `zip_code` on the fact, the raw columns every measure replaces (`is_churned`, `lost_monthly_charge`) |
| **Summarize by: none** | `age`, `tenure_in_months`, `number_of_dependents`, `number_of_referrals`, the three profile scores, `cltv` |
| **Data category** | `latitude`, `longitude`, `city`, `zip_code` (postal code) on `dim_geography` |
| **Format** | `monthly_charge` and the money columns as currency; rates as percent, 1 dp |

Every column already carries a description from dbt (`fct_customer_churn.yml`).
Paste them into the model's column descriptions, so they appear on hover in the
Fields pane.

---

## 2. DAX measures

Put these in a dedicated `_Measures` table. Rates are recomputed for whatever
the filter context is, which is what makes the dashboard analytical.

```dax
Customers = COUNTROWS ( fct_customer_churn )

Churners = SUM ( fct_customer_churn[is_churned] )

Churn Rate = DIVIDE ( [Churners], [Customers] )

-- The comparison every card needs: the rate for everyone in the same base
Base Churn Rate =
CALCULATE (
    [Churn Rate],
    REMOVEFILTERS ( fct_customer_churn ),
    REMOVEFILTERS ( dim_geography ),
    KEEPFILTERS ( VALUES ( fct_customer_churn[is_established] ) )
)

Churn Rate vs Base (pts) = ( [Churn Rate] - [Base Churn Rate] ) * 100

-- Wilson 95% interval, matching the notebook and the dbt macro
Churn Rate Lower =
VAR k = [Churners]
VAR n = [Customers]
VAR z = 1.959964
VAR p = DIVIDE ( k, n )
RETURN
    IF ( n > 0,
        DIVIDE (
            p + z ^ 2 / ( 2 * n ) - z * SQRT ( p * ( 1 - p ) / n + z ^ 2 / ( 4 * n ^ 2 ) ),
            1 + z ^ 2 / n ) )

Churn Rate Upper =
VAR k = [Churners]
VAR n = [Customers]
VAR z = 1.959964
VAR p = DIVIDE ( k, n )
RETURN
    IF ( n > 0,
        DIVIDE (
            p + z ^ 2 / ( 2 * n ) + z * SQRT ( p * ( 1 - p ) / n + z ^ 2 / ( 4 * n ^ 2 ) ),
            1 + z ^ 2 / n ) )

-- Thin cells get flagged, never hidden
Is Thin = IF ( [Customers] < 100, 1, 0 )

Rate Label =
FORMAT ( [Churn Rate], "0.0%" ) & IF ( [Is Thin] = 1, "*", "" )

Lost Monthly Billing = SUM ( fct_customer_churn[lost_monthly_charge] )

Share of Churn =
DIVIDE ( [Churners], CALCULATE ( [Churners], ALLSELECTED ( fct_customer_churn ) ) )

Share of Customers =
DIVIDE ( [Customers], CALCULATE ( [Customers], ALLSELECTED ( fct_customer_churn ) ) )
```

`Base Churn Rate` keeps the `is_established` filter. Comparing an established
segment against a base that includes the 0–3 month band (56.8% churn, no
"stayed" customers) would flatter every segment.

### Dynamic titles

The single highest-leverage move: the chart narrates itself as filters change.
Bind each visual's title to a measure (Format → Title → fx).

```dax
Selected Segment =
VAR parts =
    CONCATENATEX (
        FILTER (
            {
                ( "contract", SELECTEDVALUE ( fct_customer_churn[contract] ) ),
                ( "internet", SELECTEDVALUE ( fct_customer_churn[internet_type] ) ),
                ( "age", SELECTEDVALUE ( fct_customer_churn[age_group] ) ),
                ( "era", SELECTEDVALUE ( fct_customer_churn[era] ) )
            },
            NOT ISBLANK ( [Value2] )
        ),
        [Value2], " · "
    )
RETURN IF ( parts = "", "all customers", parts )

Title Overview =
"Churn is " & FORMAT ( [Churn Rate], "0.0%" ) & " for " & [Selected Segment]
    & " — " & FORMAT ( ABS ( [Churn Rate vs Base (pts)] ), "0.0" ) & " pts "
    & IF ( [Churn Rate vs Base (pts)] >= 0, "above", "below" ) & " the base"

Title Base Footer =
"Base: " & FORMAT ( [Customers], "#,0" ) & " customers, "
    & FORMAT ( [Churners], "#,0" ) & " churners"
```

---

## 3. Pages

Canvas **1280 × 720**. Every page has the same frame: the title (a sentence with
a verb, dynamic where possible), a scope line that is always visible, one
slicer row, visuals, and a base footer. The slicer row is synced across pages
(View → Sync slicers).

**Slicer row, left to right:** era · age group · internet type · contract ·
payment method · density class. The era slicer defaults to "established (4+
months)" and says so, because that is the base every rate is read against.

### 3.1 Overview — Setting

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ▬▬ CHURN ANALYTICS · ONE QUARTER                                             │
│ Churn is 21.2% for all customers — 0.0 pts above the base      [dynamic]    │
│ [era ▾] [age group ▾] [internet ▾] [contract ▾] [payment ▾] [density ▾]      │
├───────────────┬───────────────┬───────────────┬──────────────────────────────┤
│ CHURN RATE    │ CHURNERS      │ LOST BILLING  │ WHERE CHURN SITS             │
│ 21.2%         │ 1,272         │ $102.7k / mo  │ story_segment × share of     │
│ 20.2–22.3%    │ of 5,992      │ from churners │ churn, bars, fiber in accent │
│ vs base +0.0  │               │               │                              │
├───────────────┴───────────────┴───────────────┤                              │
│ CHURN RATE BY CONTRACT × INTERNET TYPE        │                              │
│ matrix · conditional formatting on rate       │                              │
│ (one-hue ramp on the accent) · n on hover     │                              │
│ thin cells marked *                           │                              │
├───────────────────────────────────────────────┴──────────────────────────────┤
│ Base: 5,992 customers, 1,272 churners · association, not cause    [dynamic]  │
└──────────────────────────────────────────────────────────────────────────────┘
```

- **KPI cards carry comparison context, never a bare number.** Each card shows
  the rate with its Wilson interval, and the gap against the base.
- **"Where churn sits"** shows `story_segment` by `Share of Churn`, fiber leaves
  in the accent. Sorted descending. It sums to 100% under any slicer, because
  every customer sits in exactly one leaf.
- **Matrix:** contract (rows) × internet type (columns), values `Rate Label`,
  background from a single-hue ramp (light → accent). A ramp, not categorical
  colours, because the value is a magnitude.

### 3.2 Drivers — Guilty party

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ▬▬ DRIVERS                                                                   │
│ What moves churn for [selected segment]                          [dynamic]  │
│ [slicer row]                                                                 │
├───────────────────────────────────────┬──────────────────────────────────────┤
│ DECOMPOSITION TREE                    │ KEY INFLUENCERS                      │
│ analyse: Churn Rate                   │ analyse: is_churned = 1              │
│ explain by: contract, internet type,  │ explain by: the same fields          │
│ age group, era, payment, usage,       │                                      │
│ addon band, streaming band,           │ caption: "influencers are            │
│ density class                         │ associations; customers choose       │
│                                       │ their contract and product"          │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ FIBER VS DSL AT THE SAME PRICE        │ SENIORS VS UNDER-65 BY CONTRACT      │
│ price band × churn rate, dot plot     │ contract × churn rate, dot plot      │
│ fiber accent · DSL grey               │ senior accent · under 65 grey        │
│ error bars = Wilson interval          │ error bars = Wilson interval         │
└───────────────────────────────────────┴──────────────────────────────────────┘
```

- **Decomposition tree:** the villain-hunting tool, pointed at `Churn Rate`.
  Lock the first level to `contract`, because it is the first cut that matters
  (88.6% of churn is month-to-month). Leave the rest to AI splits or user choice.
- **Key influencers:** use `is_churned` as the target with value 1. Keep the
  caption. The visual phrases its findings causally ("… increases the
  likelihood"), and the data cannot support that.
- **The two dot plots** carry the story's two strongest cuts, so a user can
  re-slice them. Error bars (Analytics pane → Error bars) show the Wilson
  measures.

### 3.3 Reasons and cost — Guilty party

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ▬▬ REASONS AND COST                                                          │
│ Why [selected segment] leave, and what it costs                  [dynamic]  │
│ [slicer row]                                                                 │
├───────────────────────────────────────┬──────────────────────────────────────┤
│ WHAT CHURNERS SAY                     │ LOST MONTHLY BILLING                 │
│ churn_category × Share of Churn,      │ by the field chosen in a field       │
│ 100% bar per internet type            │ parameter: contract / internet /     │
│ competitor and price highlighted      │ age / payment · bars                 │
│                                       │                                      │
│ note: churners only; reason codes     │                                      │
│ from a fixed list, not verbatims      │                                      │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ TOP REASONS (table)                   │ COST OF INACTION (estimates card)    │
│ churn_reason · churners · share       │ fiber over DSL: $37.4k / mo          │
│ tooltip shows the full reason text    │   range $31.5k–$42.9k                │
│                                       │ of which seniors: $9.8k / mo         │
│                                       │   — inside, not on top               │
│                                       │ note: does not respond to slicers    │
└───────────────────────────────────────┴──────────────────────────────────────┘
```

- **Reason visuals are churners-only.** Say so in the subtitle, because the
  reason columns are null for everyone who stayed.
- **The cost card** reads `rpt_story_cost_estimates` and is **explicitly
  static**. Add a subtitle: "Pre-computed for the story; does not respond to
  slicers."
- **Field parameter** (Modeling → New parameter → Fields) lets one bar chart
  switch the breakdown instead of four charts competing for space.

### 3.4 Customer detail — Narrow in (drillthrough)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ◀ back   ▬▬ CUSTOMER DETAIL                                                  │
│ 1,475 customers · established · month-to-month · fiber           [dynamic]  │
├──────────────────────────────────────────────────────────────────────────────┤
│ customer_id │ age │ tenure │ contract │ internet │ monthly │ status │ reason │
│ ...         │     │        │          │          │         │        │        │
│ table visual · sorted by monthly_charge desc · conditional icon on status   │
├──────────────────────────────────────────────────────────────────────────────┤
│ Base: the customers in the segment drilled from                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Drillthrough fields:** `story_segment`, `contract`, `internet_type`,
  `age_group`, `era`, `churn_category`. Right-click any bar, cell or node on
  pages 1–3 → Drill through → Customer detail.
- The path from "what" to "who" is one click, not a hunt.

### 3.5 Tooltip page

A tooltip page (320 × 240) on the matrix and bars shows the segment's rate with
its interval, n, share of churn, and its top three churn reasons. That puts the
reason codes — the Speech layer — on hover, where the canvas has no room for them.

---

## 4. Theme: Slate

Save as `slate-theme.json` and import it (View → Themes → Browse for themes).

```json
{
  "name": "Slate (brand, validated)",
  "dataColors": ["#4CC2A5", "#56687D", "#8FA6BC", "#5B8DEF", "#E0A458", "#C77DFF", "#EF6F6C"],
  "background": "#0F1B2A",
  "foreground": "#F2F6FA",
  "tableAccent": "#4CC2A5",
  "good": "#0CA30C",
  "neutral": "#8FA6BC",
  "bad": "#D03B3B",
  "maximum": "#4CC2A5",
  "center": "#56687D",
  "minimum": "#152436",
  "textClasses": {
    "title":   { "fontFace": "Georgia",  "fontSize": 16, "color": "#F2F6FA" },
    "header":  { "fontFace": "Segoe UI Semibold", "fontSize": 12, "color": "#F2F6FA" },
    "label":   { "fontFace": "Segoe UI", "fontSize": 10, "color": "#8FA6BC" },
    "callout": { "fontFace": "Segoe UI Semibold", "fontSize": 28, "color": "#F2F6FA" }
  },
  "visualStyles": {
    "*": {
      "*": {
        "background": [{ "color": { "solid": { "color": "#0F1B2A" } }, "transparency": 0 }],
        "border": [{ "show": false }],
        "title": [{ "fontColor": { "solid": { "color": "#F2F6FA" } } }],
        "categoryAxis": [{ "gridlineColor": { "solid": { "color": "#3D4B5C" } },
                           "labelColor": { "solid": { "color": "#8FA6BC" } } }],
        "valueAxis": [{ "gridlineColor": { "solid": { "color": "#3D4B5C" } },
                        "labelColor": { "solid": { "color": "#8FA6BC" } } }]
      }
    },
    "page": {
      "*": { "background": [{ "color": { "solid": { "color": "#0F1B2A" } }, "transparency": 0 }] }
    }
  }
}
```

- **Colour order is the brand rule, validated.** Slot 1 is the accent (the
  series that matters), slot 2 the grey `#56687D` (everything else), slot 3 the
  light grey. The design system's own grey `#8FA6BC` fails against the accent
  on this base — deuteranopia ΔE 5.1, full colour vision 11.3 — so it is
  demoted to slot 3, where it never sits beside the accent.
- **Past three series, the brand's extended palette** (`#5B8DEF` onwards)
  passes colour-blind separation but falls outside the lightness band on the
  Slate base. Prefer "focus + grey" over a fourth colour, as the brand rules
  already ask.
- **Status colours** (`good` / `bad`) are reserved for KPI direction and always
  ship with an icon or sign. They are never a series.
- **Fonts: the brand faces are not used here, deliberately.** The Power BI
  Service renders only its supported font list, and Source Serif 4, Inter and
  JetBrains Mono are not on it — they would silently fall back. Georgia carries
  the serif headline, and Segoe UI (Power BI's own default) the rest.

---

## 5. Interactions and accessibility

- **Edit interactions** (Format → Edit interactions): the KPI cards filter but
  never highlight. The estimates card ignores everything.
- **Cross-filter, not cross-highlight,** on bar charts. Highlighting a rate
  chart produces partial bars that read as a second rate.
- **Alt text** on every visual, written as the finding ("Month-to-month fiber
  customers churn at 53.3%"), not as the chart type.
- **Tab order** set per page. **Keyboard focus** is checked on the slicer row.
- **No colour-only meaning.** Every accent carries a label or legend entry;
  thin cells carry `*`; status colours carry a sign.

---

## 6. Build order

1. Connect BigQuery, import the three tables, and create the relationship.
2. Apply the model settings (section 1) and create the measures (section 2).
3. Import the theme.
4. Build the pages in order 1 → 4, then the tooltip page. Wire up drillthrough
   and sync slicers.
5. Set dynamic titles, alt text and edit interactions.
6. Run the QA checklist, then publish and schedule the refresh.

---

## 7. QA checklist

- [ ] With no slicers and era = established: Churn Rate 21.2%, Customers 5,992,
      Churners 1,272, Lost Monthly Billing $102.7k.
- [ ] Contract = month-to-month × internet = fiber optic (established): 53.3%.
- [ ] Age = senior, contract = month-to-month, internet = fiber optic: 78.3%
      (264 of 337).
- [ ] Wilson measures match `rpt_story_segments` for the same segment.
- [ ] "Where churn sits" sums to 100% under every slicer combination tried.
- [ ] Every page has a dynamic title and a base footer.
- [ ] The cost card says it does not respond to slicers.
- [ ] Key influencers carries the association caption.
- [ ] Drillthrough lands on the right customers from every source visual.
- [ ] Accent never sits beside `#8FA6BC`; no text uses `#3D4B5C`.
- [ ] Chekhov's gun: remove any visual nobody would make a decision from.

---

## 8. Open decisions

| Decision | Options | Default if not decided |
| --- | --- | --- |
| Default era on open | established / all customers | established, labelled on the slicer |
| Geography page | add a map page / leave density as a slicer | slicer only — cities are too small to rank (median 4 customers) |
| Dataset | `dbt_dev` / production | `dbt_dev` until the marts are promoted |
| Refresh | after each dbt build / daily | after each dbt build |
