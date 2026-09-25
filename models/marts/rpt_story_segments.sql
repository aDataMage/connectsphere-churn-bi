/*
  Date: 2026-09-25

  grain: one row per exhibit x segment (exhibit_id + up to three dimension values)
  Pre-aggregated data for the Tableau churn story. One exhibit per chart in
  docs/story.md, so every Story Point reads exactly the numbers in the story
  instead of re-deriving them. Each sheet filters to one exhibit_id.
  - churn rate intervals are Wilson 95%, computed here because Tableau cannot
  - share_of_dim_1_* gives mixes within the first dimension (exhibit 02: what each
    age group buys; exhibit 04: what each product's churners cite)
  - exhibit 04 counts churners only, so its churn_rate is always 1: read the shares
  - exhibit 08 layers overlap by design (each is a subset of the one above), so
    its exhibit-level shares are not meaningful - read lost_monthly_charge
  - exhibits hold no narrative text: titles and captions are authored in Tableau
*/

{#- each dim is (name, value expression, sort expression) -#}
{%- set exhibits = [
    {'id': '01', 'name': 'age x tenure', 'base': 'established customers',
     'where': 'is_established',
     'dims': [('age_group', 'age_group', 'age_group_sort'),
              ('tenure_band', 'tenure_band', 'tenure_band_sort')]},
    {'id': '02', 'name': 'age x product mix', 'base': 'established customers',
     'where': 'is_established',
     'dims': [('age_group', 'age_group', 'age_group_sort'),
              ('product_group', 'product_group', 'product_group_sort')]},
    {'id': '03', 'name': 'fiber vs dsl x price band',
     'base': 'established fiber and dsl customers in the bands where both are sold',
     'where': "is_established and internet_type in ('fiber optic', 'dsl') and price_band in ('$58-75', '$75-88', '$88-100')",
     'dims': [('internet_type', 'internet_type', 'internet_type_sort'),
              ('price_band', 'price_band', 'price_band_sort')]},
    {'id': '04', 'name': 'fiber vs dsl x churn reason', 'base': 'fiber and dsl churners, all tenures',
     'where': "is_churned = 1 and internet_type in ('fiber optic', 'dsl')",
     'dims': [('internet_type', 'internet_type', 'internet_type_sort'),
              ('churn_category', 'churn_category', 'cast(null as int64)')]},
    {'id': '05', 'name': 'era x contract x fiber (additive segmentation)', 'base': 'all customers',
     'where': 'true',
     'dims': [('era', 'era', 'era_sort'),
              ('contract', 'contract', 'contract_sort'),
              ('fiber', 'fiber_label', 'fiber_label_sort')]},
    {'id': '06', 'name': 'fiber customers: contract x age', 'base': 'established fiber customers',
     'where': 'is_established and is_fiber',
     'dims': [('contract', 'contract', 'contract_sort'),
              ('age_group', 'age_group', 'age_group_sort')]},
    {'id': '07', 'name': 'era x internet type', 'base': 'all customers',
     'where': 'true',
     'dims': [('era', 'era', 'era_sort'),
              ('internet_type', 'internet_type', 'internet_type_sort')]},
    {'id': '08', 'name': 'cost layers', 'base': 'all customers',
     'where': 'true',
     'dims': [('cost_layer', "'all billing lost'", '1')]},
    {'id': '08', 'name': 'cost layers', 'base': 'all customers',
     'where': 'is_month_to_month and is_fiber',
     'dims': [('cost_layer', "'month-to-month fiber'", '2')]},
] -%}

with base as (

    select
        *,
        case
            when internet_type = 'no internet' then 'no internet'
            when is_fiber then 'fiber'
            else 'cable or dsl'
        end as product_group,
        case
            when internet_type = 'no internet' then 3
            when is_fiber then 1
            else 2
        end as product_group_sort,
        if(is_fiber, 'fiber', 'not fiber') as fiber_label,
        if(is_fiber, 1, 2) as fiber_label_sort
    from {{ ref('fct_customer_churn') }}

),

exhibit_rows as (

    {% for e in exhibits %}
    select
        '{{ e.id }}' as exhibit_id,
        '{{ e.name }}' as exhibit_name,
        '{{ e.base }}' as base_population,
        {%- for i in range(3) %}
        {%- if i < e.dims | length %}
        '{{ e.dims[i][0] }}' as dim_{{ i + 1 }}_name,
        cast({{ e.dims[i][1] }} as string) as dim_{{ i + 1 }}_value,
        {{ e.dims[i][2] }} as dim_{{ i + 1 }}_sort,
        {%- else %}
        cast(null as string) as dim_{{ i + 1 }}_name,
        cast(null as string) as dim_{{ i + 1 }}_value,
        cast(null as int64) as dim_{{ i + 1 }}_sort,
        {%- endif %}
        {%- endfor %}
        count(*) as customers,
        sum(is_churned) as churners,
        sum(lost_monthly_charge) as lost_monthly_charge
    from base
    where {{ e.where }}
    group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
    {% if not loop.last %}union all{% endif %}
    {% endfor %}

)

select
    concat(
        exhibit_id, '|', coalesce(dim_1_value, ''), '|',
        coalesce(dim_2_value, ''), '|', coalesce(dim_3_value, '')
    ) as segment_key,
    *,
    safe_divide(churners, customers) as churn_rate,
    {{ wilson_bound('churners', 'customers', 'lower') }} as churn_rate_lower,
    {{ wilson_bound('churners', 'customers', 'upper') }} as churn_rate_upper,
    safe_divide(customers, sum(customers) over (partition by exhibit_id))
        as share_of_exhibit_customers,
    safe_divide(churners, sum(churners) over (partition by exhibit_id))
        as share_of_exhibit_churners,
    safe_divide(customers, sum(customers) over (partition by exhibit_id, dim_1_value))
        as share_of_dim_1_customers,
    safe_divide(churners, sum(churners) over (partition by exhibit_id, dim_1_value))
        as share_of_dim_1_churners
from exhibit_rows
