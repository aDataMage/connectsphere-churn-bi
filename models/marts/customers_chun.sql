/*  
  Date: 2026-06-16

  Created a single customer level table
  dropped leakage columns from the source tables as they are not needed for the churn analysis and are not predictive of churn
*/

with joined_customers as (
    select
      d.customer_id,
      d.gender, 
      d.age, 
      d.married, 
      d.number_of_dependents, 
      l.zip_code,
      s.referred_a_friend,
      s.tenure_in_months,
      s.offer,
      s.phone_service,
      s.avg_monthly_long_distance_charges,
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
      s.unlimited_data,
      s.contract,
      s.paperless_billing,
      s.payment_method,
      s.monthly_charge,
      s.total_charges,
      s.total_refunds,
      s.total_extra_data_charges,
      s.total_long_distance_charges,
      s.total_revenue,
      st.customer_status,
      st.churn_label,
      st.cltv,
      st.churn_category,
      d.age > 64 as is_senior
    from {{ ref('stg_telco__demographics') }} d
    join {{ ref('stg_telco__location') }} l
        using( customer_id)
    join {{ ref('stg_telco__services') }} s
        using( customer_id)
    join {{ ref('stg_telco__status') }} st
        using( customer_id)
)

select * from joined_customers
