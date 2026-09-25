/*
  The marts must reproduce the headline numbers in docs/story.md. Any row
  returned is a figure that has drifted from the story - either the data
  changed (update the story) or a model changed (fix the model).

  Severity is warn, not error: a data refresh should flag the story as stale,
  not block the build.
*/

{{ config(severity='warn') }}

with fct as (

    select * from {{ ref('fct_customer_churn') }}

),

est as (

    select * from {{ ref('rpt_story_cost_estimates') }}

),

seg as (

    select * from {{ ref('rpt_story_segments') }}

),

checks as (

    select 'all customers' as check_name, count(*) as actual, 7043 as expected, 0 as tolerance
    from fct
    union all
    select 'all churners', sum(is_churned), 1869, 0 from fct
    union all
    select 'established customers', countif(is_established), 5992, 0 from fct
    union all
    select 'established churners', sum(if(is_established, is_churned, 0)), 1272, 0 from fct
    union all
    select 'monthly billing lost, all churners', sum(lost_monthly_charge), 139131, 1 from fct
    union all
    select 'month-to-month share of all churn (exhibit 05)',
        sum(if(dim_2_value = 'month-to-month', share_of_exhibit_churners, 0)), 0.886, 0.001
    from seg where exhibit_id = '05'
    union all
    select 'senior fiber month-to-month churn rate (exhibit 06)', churn_rate, 0.783, 0.001
    from seg
    where exhibit_id = '06' and dim_1_value = 'month-to-month' and dim_2_value = 'senior (65+)'
    union all
    select 'fiber over dsl: rate gap lower bound', rate_gap_lower, 0.2425, 0.0001
    from est where estimate_id = 'fiber_over_dsl'
    union all
    select 'fiber over dsl: excess monthly billing', excess_monthly_billing, 37378, 1
    from est where estimate_id = 'fiber_over_dsl'
    union all
    select 'senior over under 65: excess monthly billing', excess_monthly_billing, 9837, 1
    from est where estimate_id = 'senior_over_under_65'

)

select *
from checks
where abs(actual - expected) > tolerance
