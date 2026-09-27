### Baseline


*Base: all 7,043 customers. The status x tenure table below covers the whole book; the churn rate beneath it is the 4+ month book only (5,992 customers).*
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>tenure_band</th>
      <th>0 0-3</th>
      <th>1 4-12</th>
      <th>2 13-24</th>
      <th>3 25+</th>
    </tr>
    <tr>
      <th>customer_status</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>churned</th>
      <td>597</td>
      <td>440</td>
      <td>294</td>
      <td>538</td>
    </tr>
    <tr>
      <th>joined</th>
      <td>454</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>stayed</th>
      <td>0</td>
      <td>695</td>
      <td>730</td>
      <td>3295</td>
    </tr>
  </tbody>
</table>
</div>

`joined` status only spans a tenure band of 0 - 3 months, and `stayed` starts from month 4. This might be an indication of a onboarding period and might lead to different churn analysis. `churned` status spans all months, hence two seperate analysis will be conducted to on 0-3 months and 4+ months.

- Base Churn rate `0.212`  of `5992` Customers

## Tenure


*Base: 5,992 customers with tenure > 3 months, 1,272 churners (21.2%).*
- Q1: what is the rate of churn based on tenure bands?
  - Tenure has a negative correlation with churn rate, with the `4-12` months churn group having a `0.346` churn, `13-24` - `0.231`, `25-48` - `0.256` and `48+` having a `16.7`

## Age


*Base: 5,992 customers with tenure > 3 months, 1,272 churners (21.2%), unless a question states otherwise.*
Age column showed significant spike in churn rate around 65+, hence ages bands was created between <65 (Non-Senior) and 65+ (Senior)

- **Q1: Which age group churns more?**
  
  - Seniors churn at `35.6%` (352 of 988) against `18.4%` (920 of 5,004) for
    non-seniors — a `17.2pp` gap (95% CI 14.1–20.5). Seniors are `1.94×` as
    likely to churn as non-seniors.

  - <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }

        .dataframe tbody tr th {
            vertical-align: top;
        }

        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>is_senior</th>
          <th>customers</th>
          <th>churners</th>
          <th>pct_churn</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>False</th>
          <td>False</td>
          <td>5004</td>
          <td>920</td>
          <td>0.184</td>
        </tr>
        <tr>
          <th>True</th>
          <td>True</td>
          <td>988</td>
          <td>352</td>
          <td>0.356</td>
        </tr>
      </tbody>
    </table>
    </div>

- **Q2: Is the senior effect just seniors sitting in shorter tenure bands?**
  - No. Seniors churn more in every tenure band, and they are spread across tenure almost identically to non-seniors. Adjusting for tenure *widens* the
    gap slightly, from `17.2pp` to `17.8pp` (95% CI 14.7–20.8). Seniors are
    marginally longer-tenured, so tenure was hiding a little of the effect, not
    creating it.
  - The relative gap varies by band — largest at 25–48 months (`2.59×`),
    smallest in the first year (`1.56×`) — but the evidence that it genuinely
    differs is weak (p = 0.043 across four bands). A single figure of about `2×`
    is a fair summary.

- **Q3: Is the senior effect just marital status?**
  - No. Seniors and non-seniors are split across marital status almost identically (54.3% vs 53.4% married), so there is no imbalance for marital
    status to act through. It accounts for `−0.1pp` of the `17.2pp` gap.
  - Seniors churn more in both groups: married `31.3%` (536) vs `14.7%` (2,673); not married `40.7%` (452) vs `22.7%` (2,331). At a common marital mix the gap is `17.3pp` (95% CI 14.2–20.5), or `1.94×`.
  - The effect is the same size in both groups (Breslow-Day p = 0.413, likelihood-ratio p = 0.413), so one figure describes everyone.

*Base: 4,024 internet customers (tenure ≥ 4). The senior gap here is 12.1pp,
smaller than the 17.2pp across all customers.*

- **Q4: Does the senior effect hold across internet types?**
  - Yes. Seniors churn more on both: DSL `19.4%` vs `12.0%` (+7.3pp); fiber
    `40.6%` vs `33.0%` (+7.6pp). The gap is the same size on both
    (homogeneity p = 0.32).
  - Seniors are far more likely to choose fiber — `82%` of senior customers are
    on fiber against `60%` of non-seniors — and fiber churns more. That route
    accounts for `4.6pp` of the `12.1pp` gap (38%).
  - Since internet type cannot affect age, this is not the senior effect being
    inflated: it is part of how the senior effect works. Seniors churn more
    partly because of what they choose, and partly regardless of it (`7.5pp` at
    a common internet mix, 95% CI 4.0–11.1; `1.26×`).
  
- **Q5: Does the senior effect hold across contract types?**
  - No — it exists in one contract type only. Seniors on month-to-month churn at
    `77.3%` (410) against `33.8%` (2,197) for non-seniors, a `43.5pp` gap
    (95% CI 38.8–47.8), or `2.29×` the rate.
  - On committed contracts there is no senior effect: one year `11.1%` vs
    `10.7%` (+0.4pp, CI −3.3 to +5.1); two year `1.9%` vs `2.7%` (−0.8pp,
    CI −2.2 to +1.5). Both intervals span zero.
  - The difference between contracts is large and unambiguous (Breslow-Day
    p < 0.001; likelihood-ratio p = 4.5e-19; ΔAIC 80). A single pooled figure
    would average a 43-point gap with two null results and describe no customer.
  - Contract mix explains none of it — seniors are marginally *less* likely to be
    on month-to-month, so mix was hiding `1.2pp` of the effect rather than
    creating it.
  - **Segment:** senior month-to-month customers are `410` customers — `6.8%` of
    the base — and account for `24.9%` of all churn. If they churned at the
    non-senior month-to-month rate, about `178` fewer would leave.

- **Q6: Does the senior effect hold across payment methods?**
  - Yes, but it is much larger among card payers. Seniors paying by card churn
    at `29.1%` (258) against `9.2%` (2,133) — `3.16×`. Among non-card payers,
    `37.9%` (730) vs `25.2%` (2,871) — `1.50×`. The difference is clear
    (Breslow-Day p < 0.001), so no single pooled figure applies.
  - Seniors are less likely to pay by card (`26%` vs `43%`), which accounts for
    `2.1pp` of the `17.2pp` gap. Since payment can't affect age, this is part of
    how the senior effect works rather than something to remove.
  - Card payment is associated with low churn for customers under 65 only.

- **Q7: Is the senior effect explained by what seniors buy?**
  - Partly — but as a route, not a distortion. Seniors rarely take phone-only
    service (`4.9%` vs `24.5%`), which barely churns (`3.4%`). That accounts for
    `5.5pp` of the `17.2pp` gap (32%).
  - Among customers with the same service mix, seniors still churn `10.9pp` more
    (95% CI 8.0–13.9), or `1.58×`.
  - Since service choice can't change age, the `5.5pp` is part of how the senior
    effect works: seniors churn more partly because of what they buy.
  - This also explains why the senior gap is smaller among internet customers
    only (`12.1pp`): excluding phone-only customers removes a low-churn group
    that is mostly non-senior.

## Married


*Base: 5,992 customers with tenure > 3 months, 1,272 churners (21.2%).*
- Q1: Are Married individuals more likly to churn more than Non-Married individuals?
  - Non-Married Customers have a higher churn rate of `25.6%` as aganist `17.5%` of Married customers, a `8.1pp (95 CI 6.0 - 10.2)` gap, they are `1.47x` as likly to churn as Married customers

## Dependents


*Base: 5,992 customers with tenure > 3 months, 1,272 churners (21.2%).*
Dependents was grouped into no dependents and dependents

- **Q1: Does churn differ by whether a customer has dependents?**
  - Customers with no dependents churn at `26.9%` (4,484) against `4.4%`
    (1,508) — `22.4pp` higher (95% CI 20.7–24.0), or `6.05×` the rate
    (95% CI 4.76–7.68).

- **Q2: Does that hold after accounting for age?**
  - Yes, almost entirely. Customers with no dependents are more often senior
    (20.5% vs 4.7%), and seniors churn more, so age inflates the raw gap — but
    only by `1.8pp`, 8% of the total. At a common age mix the gap is still
    `20.7pp` (95% CI 18.7–22.8), or `5.46×`.
  - The gap is larger among non-seniors (`6.10×`) than seniors (`2.65×`), but
    the evidence is marginal (Breslow-Day p = 0.040, likelihood-ratio p = 0.059)
    and rests on a thin cell: only 71 seniors have dependents, of whom about 10
    churned. Treat the pooled figure as the headline.

## Internet Type

Internet type comparison was between the lowest  churn group (DSL) and the heighest (Fiber Optic)

- *Base: 4,024 internet customers with tenure ≥ 4 months, 1,096 churners.*

- **Q1: Does churn vary by internet type?**
  - Fiber customers churn at `35.0%` (2,613) against `12.8%` (1,411) for DSL —
    a `22.2pp` gap (95% CI 19.6–24.7). Fiber customers are `2.73×` as likely
    to churn.

- **Q2: Is the fiber effect just fiber customers sitting on month-to-month?**
  - Partly. Fiber customers are more concentrated on month-to-month (56% vs
    39%), and that mix accounts for `5.4pp` — a quarter of the gap.
  - The rest holds on every contract. At a common contract mix, fiber churns
    `17.4pp` higher (95% CI 14.9–19.9), or `2.15×` the DSL rate.
  - The effect is broadly consistent across contract types (homogeneity
    p = 0.073; LR p = 0.082), so one adjusted figure is a fair summary.

- **Q3: Is fiber's churn just its price?**
  - The two products barely overlap on price. Fiber is not sold below £58
    (0% of fiber customers vs 45.6% of DSL), and DSL is effectively absent above
    £100 (0% vs 33.8%). Price band and internet type are close to the same
    variable, so neither a standardised rate nor a decomposition is meaningful —
    both would extrapolate each product into a price range where it isn't sold.
  - In the three bands where both are sold, the gap is *larger* than the crude
    figure, not smaller: `+36.3pp` at £58–75, `+37.0pp` at £75–88, `+34.5pp` at
    £88–100, against a crude `22.2pp`. Price was masking part of the difference.
  - Within fiber, churn falls as price rises (`45.8%` → `41.2%` → `36.2%`), so
    the pattern does not look like simple price sensitivity.

- **Q4: is fiber effect just a result of streaming?**
  - Fiber churns more in every streaming band. Streaming mix explains none of the gap (−0.2pp), because fiber's under-representation in band 0 and its over-representation in band 3 offset each other, and because streaming count barely moves churn in the first place.

  - One interaction term reaches significance (band 1, ×2.02), but the other two do not, the gap shows no ordering across bands, and the overall test is marginal (p = 0.042, ΔAIC 2.2). Treat the effect as constant: fiber customers churn about 2.8× as often at any streaming level.

- **Q5: Does the fiber effect hold across payment methods?**
  - Yes. Fiber churns more than DSL among card payers (`23.5%` vs `8.2%`,
    `+15.3pp`) and non-card payers (`39.3%` vs `16.5%`, `+22.8pp`). The points
    gap is smaller for card payers because they churn less overall; in relative
    terms the effect is the same (`2.9×` vs `2.4×`; homogeneity p = 0.83).
  - Fiber customers are more often non-card (`73%` vs `56%` of DSL customers).
    That mix accounts for `2.1pp` of the `22.2pp` gap (9%). On a common payment
    mix, fiber churns `20.2pp` more (95% CI 17.6–22.8), or `2.49×`.
  - Internet type and payment are chosen together at sign-up, so it isn't
    possible to say whether that `2.1pp` distorts the fiber effect or is part
    of it.

## Contract


*Base: 5,992 customers with tenure > 3 months, 1,272 churners (21.2%).*
- Q1: Does churn rate vary across Contract?
  - customer on month-to-month contracts have a churn rate of `40.7%` against `9.3%` for one year (`29.9pp diff, 2.8x (280%)`) and `2.6%` for a two year contract (`38.1pp diff, 15.6x (1560%)`) higher.

- **Q1: Is the contract effect just tenure?**
  - No. Tenure mix accounts for `3.0pp` of the `38.1pp` gap — 8%. At a common tenure mix, month-to-month customers churn `35.2pp` more than two-year customers (95% CI 32.8–37.6).
  - The gap holds at every tenure length, including the shortest: among customers with 4–12 months, month-to-month churns at `47.1%` (910) while no
    two-year customer churned at all (0 of 105; upper bound ≈3%).
  - The advantage does shrink with time — `47.1pp` at 4–12 months falling to
    `26.8pp` at 49+ (Breslow-Day p < 0.001) — consistent with lock-in mattering most when a customer would otherwise leave.
  - Note: contract and tenure are entangled by construction, since a long contract produces long tenure. Neither adjusted figure should be read as a clean causal effect.

- **Q2: Does the month-to-month effect hold across internet types?**
  - Yes. Month-to-month churns more than two-year for every internet type —
    from `+10.0pp` without internet to `+47.7pp` on fiber. The gap in points varies because base churn varies; in relative terms the effect is
    consistent (homogeneity p = 0.51), so one adjusted figure applies.
  - Month-to-month customers are concentrated on fiber (`56.6%`), while two-year
    customers lean toward no internet (`34.2%`). That mix accounts for `6.0pp`
    of the `38.1pp` gap (16%). On a common internet mix, month-to-month churns
    `32.4pp` more (95% CI 30.4–34.3).
  - Contract and internet type are chosen together at sign-up, so it isn't
    possible to say whether that `6.0pp` distorts the contract effect or is
    part of it.
  - **Segment:** fiber month-to-month customers churn at `53.3%` and account for
    `61.8%` of all churn.

- **Q3: Does the month-to-month effect hold across payment methods?**
  - Yes. Month-to-month churns more than two-year for both groups: `+23.8pp`
    among card payers and `+43.9pp` among non-card payers. In relative terms the
    effect is nearly identical (`14.9×` vs `13.7×`; homogeneity p = 0.46) — the
    points gap is smaller for card payers only because they churn less overall.
  - Month-to-month customers are more often non-card (`69%` vs `50%` of two-year
    customers). That mix accounts for `2.3pp` of the `38.1pp` gap (6%). On a common payment mix, month-to-month churns `35.9pp` more (95% CI 33.9–37.9).
  - Contract and payment are chosen together at sign-up, so their order is
    unknown.
  - **Segment:** non-card month-to-month customers are `30%` of the base, churn
    at `47.3%`, and account for `67%` of all churners.

- **Q4: Does the month-to-month effect hold across age groups?**
  - Yes, but it is far stronger for seniors. Month-to-month churns `31.1pp` more than two-year among non-seniors (`33.8%` vs `2.7%`; `12×`) and `75.4pp` more among seniors (`77.3%` vs `1.9%`; `41×`).
  - The difference shows up in both points and relative terms, so it is not an artefact of base rates (homogeneity p < 0.001; ΔAIC 80). A single pooled figure would average two very different effects.
  - Age does not distort the comparison: seniors choose contracts at the same rate as everyone else (`15.7%` / `17.1%` / `17.0%` senior), so the mix contributes nothing (`−0.3pp`).
  - This is the same interaction as Age:Q5 seen from the contract side: the senior effect exists only on month-to-month, and the contract effect is strongest for seniors.

- **Q5: Does the month-to-month effect depend on which services customers buy?**
  - No. Month-to-month churns more than two-year for every service mix — from
    `+10.0pp` on phone only to `+41.7pp` on both. The points gap varies because
    base churn varies; in relative terms the effect is consistent (homogeneity
    p = 0.65; likelihood-ratio p = 0.90), so one adjusted figure applies.
  - Month-to-month customers mostly buy both services (`79.5%`, the highest-churn
    group), while two-year customers are three times as likely to be phone only
    (`34.2%` vs `11.0%`, the lowest-churn group). That mix accounts for `4.4pp` of
    the `38.1pp` gap (12%). On a common service mix, month-to-month churns
    `34.1pp` more (95% CI 32.2–36.1).
  - Contract and services are chosen together at sign-up, so it isn't possible to
    say whether that `4.4pp` distorts the contract effect or is part of it.


- **Q6: Does the month-to-month effect depend on how many add-ons customers hold?**
  - Month-to-month churns more than two-year at every add-on level. On a common
    add-on mix the gap is `37.8pp` (95% CI 35.3–40.2).
  - Two-year customers hold far more add-ons (`85%` have two or more, against
    `35%` of month-to-month customers), but that mix accounts for only `3.5pp` of
    the `40.9pp` gap (8%).
  - The effect weakens as add-ons increase — `+51.9pp` with none, `+30.8pp` with
    two or more — consistent with add-ons and long contracts both anchoring
    customers. The evidence is marginal (homogeneity p = 0.07) and the no-add-on
    two-year group is small (54 customers), so this is a pattern to test, not a
    finding.
  
## Gender


*Base: 5,992 customers with tenure > 3 months, 1,272 churners (21.2%).*
both genders have a churn rate of around `21.3%`. and a non signicicant difference (`-0.3pp  ± 2pp`) between them. This suggests that gender may not be a significant factor in churn, but further analysis is needed to confirm this finding and determine if it persists when controlling for other variables such as contract type and monthly charge.

male:   21.1%  (19.7, 22.6)   n=3019
female:   21.4%  (19.9, 22.9)   n=2973
diff:    -0.3pp (-2.3, 1.8)
ratio:   0.99x (0.90, 1.09)

## Add-Ons


*Base: 4,718 internet customers with tenure > 3 months, 1,229 churners (26.0%). Add-ons attach to internet, so phone-only customers are out of scope.*
`add-on` services (online security, online backup, device protection plan, premium tech support) are associated with lower churn rates. Customers with more add-ons tend to be stickier, suggesting that bundling services may improve retention.

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>addon_count</th>
      <th>customers</th>
      <th>churners</th>
      <th>pct_of_churn</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>773</td>
      <td>361</td>
      <td>0.467</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>1241</td>
      <td>441</td>
      <td>0.355</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>1303</td>
      <td>289</td>
      <td>0.222</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>931</td>
      <td>113</td>
      <td>0.121</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>470</td>
      <td>25</td>
      <td>0.053</td>
    </tr>
  </tbody>
</table>
</div>

## Streaming Service


*Base: 4,718 internet customers with tenure > 3 months, 1,229 churners (26.0%).*
customers who don't use any streaming service have a churn rate of `23.4%`, while those who use one or two have a churn rate of around `29.7%`. With customers who use 3 services having a churn rate of `24.9%`.
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>streaming_count</th>
      <th>customers</th>
      <th>churners</th>
      <th>pct_of_churn</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>1428</td>
      <td>334</td>
      <td>0.234</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>811</td>
      <td>241</td>
      <td>0.297</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>886</td>
      <td>258</td>
      <td>0.291</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>1593</td>
      <td>396</td>
      <td>0.249</td>
    </tr>
  </tbody>
</table>
</div>

## Paperless Billing


*Base: 5,992 customers with tenure > 3 months, 1,272 churners (21.2%).*
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>paperless_billing</th>
      <th>customers</th>
      <th>churners</th>
      <th>pct_churn</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>False</td>
      <td>2430</td>
      <td>284</td>
      <td>0.117</td>
    </tr>
    <tr>
      <th>1</th>
      <td>True</td>
      <td>3562</td>
      <td>988</td>
      <td>0.277</td>
    </tr>
  </tbody>
</table>
</div>

Customers who use paperless billing churn at an higher rate `27.7%` as aganist `11.7%`


- **Q1: Is the paperless gap just contract type?**
  - Partly. Paperless customers churn more on every contract: month-to-month
    `46.6%` (1,795) vs `27.5%` (812); one year `13.9%` vs `6.8%`; two year
    `3.6%` vs `1.6%`.
  - Contract mix accounts for `5.5pp` of the `16.0pp` crude gap — `35%` of it —
    because paperless customers are concentrated on month-to-month (`50.4%` of
    them against `33.4%` of paper customers). On a common contract mix the gap
    is `10.8pp` (95% CI 8.9-12.6), or `1.77x` pooled (OR 2.29, 1.96-2.67).
  - The effect is remarkably uniform in relative terms (homogeneity p = `0.973`;
    likelihood-ratio p = `0.973`), so one adjusted figure describes all three.

- **Q2: Is it just internet type?**
  - More so than contract. Internet mix accounts for `8.6pp` of the `16.0pp`
    gap - `54%`, the largest share any single variable takes off it - because
    paperless customers are overwhelmingly on fiber (`56.9%` against `24.2%` of
    paper customers).
  - On a common internet mix the gap falls to `7.8pp` (95% CI 5.7-9.9), `1.50x`
    (OR 1.71, 1.47-2.00), still holding in the same direction everywhere
    (homogeneity p = `0.222`; LR p = `0.214`).
  - Among customers with no internet at all, paperless makes no difference:
    `3.5%` vs `3.3%` (+0.2pp, CI -1.8 to +2.8). The gap needs a product to
    attach to, which is the clearest sign that paperless is a marker rather than
    a mechanism.

- **Q3: So what is paperless billing measuring?**
  - Taken together, over half the raw gap is internet type and a third is
    contract, and the two overlap. Paperless is best read as a proxy for the
    digital, fiber, month-to-month customer rather than as a lever: nothing in
    these cuts suggests moving someone back to paper would retain them.

## Onboarding (0–3 months)

*Base: the whole book, 7,043 customers, 1,869 churners (26.5%). The onboarding
band is 1,051 customers — 597 `churned` and 454 `joined`, with **no `stayed`
status inside it at all**. Its 56.8% is therefore the churn rate of a pure new
cohort and is not a like-for-like reading of the 21.2% posted by the 4+ book.*

- **Q1: How much churn sits in the first three months?**
  - The onboarding band churns at `56.8%` (95% CI 53.8–59.8) against `21.2%`
    (20.2–22.3) for the established book — `35.6pp` higher (32.4–38.7), or
    `2.68×` the rate.
  - It is `14.9%` of customers and `31.9%` of all churn. At the established
    rate, about `374` fewer of them would have left.

- **Q2: Does the contract effect look the same in the first three months?**
  - Month-to-month churns `59.3%` (1,003) in onboarding against `40.7%` (2,607)
    later. On a common era mix month-to-month churns `41.3pp` more than two-year
    (95% CI 39.5–43.0).
  - No detectable interaction (homogeneity p = `0.265`; likelihood-ratio
    p = `0.066`), so one contract effect describes both eras.
  - **Committed contracts barely exist in the onboarding window** — one year
    `26` customers, two year `22` with no churners at all. The onboarding column
    of this cut is effectively about month-to-month, and the standardisation
    carries `15%` of its weight on cells with n<30.

- **Q3: Does the internet-type effect look the same?**
  - Levels are far higher, ordering identical: no internet `27.8%` (252),
    DSL `52.3%` (241), cable `58.8%` (136), fiber `76.1%` (422).
  - Fiber over DSL is `+23.8pp` (16.2–31.1) in onboarding against `+22.2pp`
    (19.6–24.7) later — the same gap (homogeneity p = `0.228`; LR p = `0.059`).
    Pooled, fiber is `2.21×` DSL (OR 3.51, 3.00–4.10).

- **Q4: Does the payment effect look the same?**
  - Bank withdrawal `68.2%` (569), mailed check `66.1%` (124), credit card
    `35.5%` (358). Withdrawal over card is `+32.7pp` (26.3–38.8) in onboarding
    against `+16.8pp` (14.8–18.8) later.
  - The points gap is nearly twice as large early, but in relative terms it is
    not distinguishable (homogeneity p = `0.136`; LR p = `0.185`; pooled OR 3.22,
    2.82–3.67).

- **Q5: Does the senior effect look the same?**
  - Seniors churn `80.5%` (154) in onboarding against `52.7%` (897) for
    non-seniors: `+27.8pp` (20.1–34.2). Later it is `+17.2pp` (14.1–20.5).
  - Marginal and not conclusive (homogeneity p = `0.068`; LR p = `0.064`);
    pooled OR 2.61 (2.27–3.00), `1.81×`.
  - Four in five senior customers in their first three months leave.

- **Q6: So is early churn a different problem?**
  - On this evidence, no — it is the same problem at higher intensity. Contract,
    internet type, payment and age all keep their direction, their ordering and
    (within confidence intervals) their relative size; not one of the four
    interactions clears p = 0.05, though internet type and age sit just above it.
  - What changes is the level, not the mechanism: every segment churns roughly
    two to three times as often inside the first three months.

## Churn Reason (by segment)

*Base: 1,869 churners — `churn_category` and `churn_reason` are populated for
churners only and are null for everyone who stayed, so these are shares of each
segment's churners and never rates. The five-level `churn_category` is used
throughout; the ~20-level `churn_reason` leaves single-digit cells once crossed.*

- **Q1: Do early leavers give different reasons than later ones?**
  - No. Onboarding: competitor `44.1%`, attitude `18.4%`, dissatisfaction
    `14.4%`, price `12.2%`, other `10.9%`. Established: `45.4%` / `16.0%` /
    `17.1%` / `10.8%` / `10.6%`.
  - chi² = `4.0` on 4 df, p = `0.40`. No standardized residual reaches 2.
    Whatever makes the first three months worse, it is not a different
    complaint — the same mix of reasons, nearly twice as often.

- **Q2: Do fiber churners give different reasons than DSL churners?**
  - Yes, mildly. Across the three internet products (1,756 churners):
    competitor is `47.5%` of fiber churn against `40.7%` of DSL, while
    dissatisfaction is `15.8%` of fiber against `20.2%` of DSL, and `other`
    `10.4%` against `14.7%`.
  - Fiber against DSL alone (1,543 churners): chi² = `10.6` on 4 df,
    p = `0.032`. The two cells carrying it are competitor (z = ±2.1) and
    `other` (z = ±2.1); price is flat (`10.2%` vs `11.1%`, z = 0.5).
  - Fiber churn is more often attributed to a competitor and less often to
    unexplained or dissatisfaction reasons. Price is not what separates them.

## Revenue at Risk

*Base: the whole book, 7,043 customers, 1,869 churners. Revenue is the summed
`monthly_charge` of the customers who actually left — `SUM(IF(churn_label,
monthly_charge, 0))` — so it is realised billing, not a model. The 12-month
column multiplies that by twelve: it is what the segment would have billed over
a year had those customers stayed, which is an assumption about horizon, not a
measurement. Total at risk: `$139,131` a month, `$1,669,570` over 12 months, on
an average churner bill of `$74.44`.*

- **Q1: Where does the money actually sit?**
  - By contract: month-to-month `$120,847` a month — `86.9%` of all risk —
    against one year `$14,118` (10.1%) and two year `$4,165` (3.0%).
  - By internet type: fiber `$108,816` a month, `78.2%` of risk, on the highest
    average bill of any segment (`$88.04`). DSL `10.8%`, cable `9.3%`, no
    internet `1.7%`.
  - By payment: bank withdrawal `$104,381` a month (75.0%). Mailed check churns
    at the highest rate of the three (`36.9%`) but is only `5.5%` of risk — 385
    customers on the lowest average bill (`$54.11`).

- **Q2: Does the onboarding band matter in money as well as rate?**
  - Less than its churn rate suggests. It is `31.9%` of churners but `26.2%` of
    revenue at risk (`$36,429` a month), because early leavers bill `$61.02`
    against `$80.74` for later ones — they leave before they have been upsold.

- **Q3: Which demographic and billing splits carry the risk?**
  - Seniors are `16.2%` of customers and `27.6%` of revenue at risk
    (`$38,420` a month), on a higher average bill than non-seniors
    (`$80.71` vs `$72.30`).
  - Paperless customers are `78.7%` of risk (`$109,510` a month), which is the
    same confounded signal as everywhere else — see Paperless Billing Q1–Q2.

## Churn Tree (one segmentation that adds up)

*Base: the whole book, 7,043 customers, 1,869 churners (26.5%). Split once by
tenure era, then contract, then fiber or not, so every customer lands in exactly
one of 12 leaves and the leaves account for 100% of churn. Unlike every other
section, these pieces can be added.*

- **Q1: How concentrated is churn?**
  - Four leaves — every one of them month-to-month — hold `88.6%` of all churn:

    | leaf | n | churners | rate | % of churn | cum | 12-mo risk |
    |---|---|---|---|---|---|---|
    | 4+ / month-to-month / fiber | 1,475 | 786 | 53.3% | 42.1% | 42.1% | $841,418 |
    | 0–3 / month-to-month / fiber | 407 | 321 | 78.9% | 17.2% | 59.2% | $305,711 |
    | 4+ / month-to-month / not fiber | 1,132 | 274 | 24.2% | 14.7% | 73.9% | $172,072 |
    | 0–3 / month-to-month / not fiber | 596 | 274 | 46.0% | 14.7% | 88.6% | $130,964 |

  - The remaining `11.4%` is spread across the eight committed-contract leaves,
    the largest of which is 4+ / one year / fiber at `5.2%`.
  - Those four leaves are exactly the month-to-month book: `3,610` customers,
    `51.3%` of the base, carrying `88.6%` of all churn. Contract is not one
    driver among several in this segmentation — it is the first cut that matters.

- **Q2: Where is the highest-rate cell, as opposed to the biggest?**
  - `0–3 / month-to-month / fiber`: `407` customers churning at `78.9%`. It is
    only `17.2%` of churn volume but the worst rate in the book, and it is the
    cell where the onboarding and fiber and month-to-month effects all land on
    the same customer.
  - The mirror image is `4+ / two year / not fiber`: `1,306` customers, `1.3%`
    churn, `0.9%` of all churn.
