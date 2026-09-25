/*
  Date: 2026-09-25

  grain: one row per estimate_id
  The cost-of-inaction estimates in docs/story.md, section 5: how many churners,
  and how much monthly billing, sit above a comparison group's churn rate.
  Used by the Tableau story (Exhibit 8) and the Power BI cost card.
  - ranges carry the Newcombe 95% interval on the rate gap
  - the bill is the average monthly_charge of the churners the estimate is about
  - 12-month figures multiply by twelve: a horizon assumption, not a measurement
  - senior_over_under_65 sits INSIDE fiber_over_dsl (both are month-to-month
    fiber customers), so the two must never be added together
  - these are associations: read each range as a ceiling on what a targeted fix
    could recover, not a forecast
*/

with fct as (

    select * from {{ ref('fct_customer_churn') }}

),

fiber_over_dsl as (

    select
        'fiber_over_dsl' as estimate_id,
        'fiber over dsl, established month-to-month customers' as estimate_label,
        countif(internet_type = 'fiber optic') as group_customers,
        sum(if(internet_type = 'fiber optic', is_churned, 0)) as group_churners,
        countif(internet_type = 'dsl') as comparison_customers,
        sum(if(internet_type = 'dsl', is_churned, 0)) as comparison_churners,
        -- the story prices fiber churn at the average bill of every fiber churner
        (select avg(monthly_charge) from fct where is_churned = 1 and is_fiber)
            as avg_monthly_bill,
        cast(null as string) as overlaps_with
    from fct
    where is_established and is_month_to_month

),

senior_over_under_65 as (

    select
        'senior_over_under_65' as estimate_id,
        'seniors over under-65s, established month-to-month fiber customers' as estimate_label,
        countif(is_senior) as group_customers,
        sum(if(is_senior, is_churned, 0)) as group_churners,
        countif(not is_senior) as comparison_customers,
        sum(if(not is_senior, is_churned, 0)) as comparison_churners,
        safe_divide(
            sum(if(is_senior and is_churned = 1, monthly_charge, 0)),
            sum(if(is_senior, is_churned, 0))
        ) as avg_monthly_bill,
        'fiber_over_dsl' as overlaps_with
    from fct
    where is_established and is_month_to_month and is_fiber

),

estimates as (

    select * from fiber_over_dsl
    union all
    select * from senior_over_under_65

),

gaps as (

    select
        *,
        safe_divide(group_churners, group_customers) as group_rate,
        safe_divide(comparison_churners, comparison_customers) as comparison_rate,
        safe_divide(group_churners, group_customers)
            - safe_divide(comparison_churners, comparison_customers) as rate_gap,
        {{ newcombe_bound('group_churners', 'group_customers',
                          'comparison_churners', 'comparison_customers', 'lower') }}
            as rate_gap_lower,
        {{ newcombe_bound('group_churners', 'group_customers',
                          'comparison_churners', 'comparison_customers', 'upper') }}
            as rate_gap_upper
    from estimates

)

select
    estimate_id,
    estimate_label,
    overlaps_with,
    group_customers,
    group_churners,
    group_rate,
    comparison_customers,
    comparison_churners,
    comparison_rate,
    rate_gap,
    rate_gap_lower,
    rate_gap_upper,
    avg_monthly_bill,
    group_customers * rate_gap as excess_churners,
    group_customers * rate_gap_lower as excess_churners_lower,
    group_customers * rate_gap_upper as excess_churners_upper,
    group_customers * rate_gap * avg_monthly_bill as excess_monthly_billing,
    group_customers * rate_gap_lower * avg_monthly_bill as excess_monthly_billing_lower,
    group_customers * rate_gap_upper * avg_monthly_bill as excess_monthly_billing_upper,
    12 * group_customers * rate_gap * avg_monthly_bill as excess_12_month_billing,
    12 * group_customers * rate_gap_lower * avg_monthly_bill as excess_12_month_billing_lower,
    12 * group_customers * rate_gap_upper * avg_monthly_bill as excess_12_month_billing_upper
from gaps
