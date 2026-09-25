### Baseline

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

- Q1: what is the rate of churn based on tenure bands?
  - Tenure has a negative correlation with churn rate, with the `4-12` months churn group having a `0.346` churn, `13-24` - `0.231`, `25-48` - `0.256` and `48+` having a `16.7`

## Age

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

- **Q: Does the senior effect hold across contract types?**
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

## Married

- Q1: Are Married individuals more likly to churn more than Non-Married individuals?
  - Non-Married Customers have a higher churn rate of `25.6%` as aganist `17.5%` of Married customers, a `8.1pp (95 CI 6.0 - 10.2)` gap, they are `1.47x` as likly to churn as Married customers

## Dependents

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

- Q4: is fiber effect just a result of streaming?
  - Fiber churns more in every streaming band. Streaming mix explains none of the gap (−0.2pp), because fiber's under-representation in band 0 and its over-representation in band 3 offset each other, and because streaming count barely moves churn in the first place.

  - One interaction term reaches significance (band 1, ×2.02), but the other two do not, the gap shows no ordering across bands, and the overall test is marginal (p = 0.042, ΔAIC 2.2). Treat the effect as constant: fiber customers churn about 2.8× as often at any streaming level.

## Contract

- Q1: Does churn rate vary across Contract?
  - customer on month-to-month contracts have a churn rate of `40.7%` against `9.3%` for one year (`29.9pp diff, 2.8x (280%)`) and `2.6%` for a two year contract (`38.1pp diff, 15.6x (1560%)`) higher.

- **Q: Is the contract effect just tenure?**
  - No. Tenure mix accounts for `3.0pp` of the `38.1pp` gap — 8%. At a common tenure mix, month-to-month customers churn `35.2pp` more than two-year customers (95% CI 32.8–37.6).
  - The gap holds at every tenure length, including the shortest: among customers with 4–12 months, month-to-month churns at `47.1%` (910) while no
    two-year customer churned at all (0 of 105; upper bound ≈3%).
  - The advantage does shrink with time — `47.1pp` at 4–12 months falling to
    `26.8pp` at 49+ (Breslow-Day p < 0.001) — consistent with lock-in mattering most when a customer would otherwise leave.
  - Note: contract and tenure are entangled by construction, since a long contract produces long tenure. Neither adjusted figure should be read as a clean causal effect.

## Gender

both genders have a churn rate of around `21.3%`. and a non signicicant difference (`-0.3pp  ± 2pp`) between them. This suggests that gender may not be a significant factor in churn, but further analysis is needed to confirm this finding and determine if it persists when controlling for other variables such as contract type and monthly charge.

male:   21.1%  (19.7, 22.6)   n=3019
female:   21.4%  (19.9, 22.9)   n=2973
diff:    -0.3pp (-2.3, 1.8)
ratio:   0.99x (0.90, 1.09)

## Add-Ons

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
