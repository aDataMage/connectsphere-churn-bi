/*
  Date: 2026-09-25

  grain: one row per customer_id - all 7,043 customers, every tenure
  The BI-ready customer table behind both dashboards. Every band, flag and
  profile score used in the analysis is derived once here, so Tableau and
  Power BI never re-derive them and every figure agrees with docs/story.md.
  - leakage columns (satisfaction_score, churn_score) are excluded, as in customers_chun
  - every band carries a `*_sort` column so BI tools can order it (Power BI: Sort by column)
  - internet_type 'none' is relabelled 'no internet': the staging model stores
    the string 'none', not NULL, so IFNULL-style handling silently misses it
  - is_churned is an integer, so SUM() counts churners and AVG() is the churn rate
  - era splits the book at 3 months: the 0-3 band holds no 'stayed' customers,
    so the story reports it separately from the established book
*/

with customers as (

    select
        d.customer_id,
        l.zip_code,
        d.gender,
        d.age,
        d.married,
        d.number_of_dependents,
        s.number_of_referrals,
        s.tenure_in_months,
        s.offer,
        s.phone_service,
        s.multiple_lines,
        s.internet_service,
        s.internet_type,
        s.avg_monthly_gb_download,
        s.online_security,
        s.online_backup,
        s.device_protection_plan,
        s.premium_tech_support,
        s.streaming_tv,
        s.streaming_movies,
        s.streaming_music,
        s.unlimited_data,
        s.contract,
        s.paperless_billing,
        s.payment_method,
        s.monthly_charge,
        s.total_charges,
        s.total_revenue,
        st.customer_status,
        st.churn_label,
        st.churn_category,
        st.churn_reason,
        st.cltv
    from {{ ref('stg_telco__demographics') }} d
    join {{ ref('stg_telco__location') }} l using (customer_id)
    join {{ ref('stg_telco__services') }} s using (customer_id)
    join {{ ref('stg_telco__status') }} st using (customer_id)

),

counted as (

    select
        *,
        cast(online_security as int64) + cast(online_backup as int64)
            + cast(device_protection_plan as int64) + cast(premium_tech_support as int64)
            as addon_count,
        cast(streaming_tv as int64) + cast(streaming_movies as int64)
            + cast(streaming_music as int64) as streaming_count
    from customers

)

select
    customer_id,
    zip_code,

    -- who: demographics
    gender,
    age,
    if(age >= 65, 'senior (65+)', 'under 65') as age_group,
    if(age >= 65, 1, 2) as age_group_sort,
    age >= 65 as is_senior,
    married,
    number_of_dependents,
    number_of_dependents > 0 as has_dependents,
    number_of_referrals,
    number_of_referrals > 0 as has_referred,

    -- when: lifecycle
    tenure_in_months,
    tenure_in_months > 3 as is_established,
    if(tenure_in_months <= 3, 'new (0-3 months)', 'established (4+ months)') as era,
    if(tenure_in_months <= 3, 1, 2) as era_sort,
    case
        when tenure_in_months <= 3 then '0-3'
        when tenure_in_months <= 12 then '4-12'
        when tenure_in_months <= 24 then '13-24'
        when tenure_in_months <= 48 then '25-48'
        else '49+'
    end as tenure_band,
    case
        when tenure_in_months <= 3 then 1
        when tenure_in_months <= 12 then 2
        when tenure_in_months <= 24 then 3
        when tenure_in_months <= 48 then 4
        else 5
    end as tenure_band_sort,

    -- what: products
    phone_service,
    multiple_lines,
    internet_service,
    if(internet_service, internet_type, 'no internet') as internet_type,
    case
        when not internet_service then 1
        when internet_type = 'dsl' then 2
        when internet_type = 'cable' then 3
        else 4
    end as internet_type_sort,
    internet_type = 'fiber optic' as is_fiber,
    case
        when phone_service and internet_service then 'both'
        when phone_service then 'phone only'
        else 'internet only'
    end as usage,
    offer,
    unlimited_data,
    avg_monthly_gb_download,
    addon_count,
    case
        when not internet_service then 'no internet'
        when addon_count = 0 then '0'
        when addon_count = 1 then '1'
        else '2+'
    end as addon_band,
    case
        when not internet_service then 0
        when addon_count = 0 then 1
        when addon_count = 1 then 2
        else 3
    end as addon_band_sort,
    streaming_count,
    case
        when not internet_service then 'no internet'
        when streaming_count = 0 then '0'
        when streaming_count <= 2 then '1-2'
        else '3'
    end as streaming_band,
    case
        when not internet_service then 0
        when streaming_count = 0 then 1
        when streaming_count <= 2 then 2
        else 3
    end as streaming_band_sort,

    -- how they are held: contract and billing
    contract,
    case contract
        when 'month-to-month' then 1
        when 'one year' then 2
        else 3
    end as contract_sort,
    contract = 'month-to-month' as is_month_to_month,
    payment_method,
    paperless_billing,
    monthly_charge,
    -- price bands are the monthly_charge quintile edges among internet customers
    case
        when monthly_charge < 58 then '<$58'
        when monthly_charge < 75 then '$58-75'
        when monthly_charge < 88 then '$75-88'
        when monthly_charge < 100 then '$88-100'
        else '$100+'
    end as price_band,
    case
        when monthly_charge < 58 then 1
        when monthly_charge < 75 then 2
        when monthly_charge < 88 then 3
        when monthly_charge < 100 then 4
        else 5
    end as price_band_sort,

    -- composite profiles, each 0-2 (see notebooks/Eda.ipynb, Customer profiles)
    cast(married as int64) + if(number_of_dependents > 0, 1, 0) as stability_score,
    if(contract != 'month-to-month', 1, 0) + if(number_of_referrals > 0, 1, 0) as trust_score,
    -- engagement only exists where there is internet; median splits among internet customers
    if(
        internet_service,
        if(streaming_count >= 2, 1, 0) + if(avg_monthly_gb_download >= 21, 1, 0),
        null
    ) as engagement_score,

    -- the story's one segmentation that adds up: 12 leaves, every customer in one
    concat(
        if(tenure_in_months <= 3, 'new', 'established'), ' · ',
        contract, ' · ',
        if(internet_type = 'fiber optic', 'fiber', 'not fiber')
    ) as story_segment,

    -- outcome
    customer_status,
    cast(churn_label as int64) as is_churned,
    churn_category,
    churn_reason,
    cltv,

    -- money: lost_monthly_charge is the billing that left with a churner
    if(churn_label, monthly_charge, 0) as lost_monthly_charge,
    total_charges,
    total_revenue

from counted
