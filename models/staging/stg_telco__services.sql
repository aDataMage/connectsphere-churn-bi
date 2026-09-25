/*
Date: 2024-06-19
   grain: one row per customer_id
   dropped: Count columns dropped as they were an artefact of the data_source; `Quarter` is a constant and was dropped; referred_a_friend can be derived from number_of_referrals, hence it is redundant and was dropped
   Columns renamed to be more descriptive and to follow naming conventions
   All string columns are lower-cased at staging for consistency; the Yes/No columns land as booleans from the seed so they are left as-is
*/

with source as (

    select * from {{ source('telco', 'services') }}

),

renamed as (

    select
        lower(`Customer ID`) as customer_id,
        `Number of Referrals` as number_of_referrals,
        `Tenure in Months` as tenure_in_months,
        lower(`Offer`) as offer,
        `Phone Service` as phone_service,
        `Avg Monthly Long Distance Charges` as avg_monthly_long_distance_charges,
        `Multiple Lines` as multiple_lines,
        `Internet Service` as internet_service,
        lower(`Internet Type`) as internet_type,
        `Avg Monthly GB Download` as avg_monthly_gb_download,
        `Online Security` as online_security,
        `Online Backup` as online_backup,
        `Device Protection Plan` as device_protection_plan,
        `Premium Tech Support` as premium_tech_support,
        `Streaming TV` as streaming_tv,
        `Streaming Movies` as streaming_movies,
        `Streaming Music` as streaming_music,
        `Unlimited Data` as unlimited_data,
        lower(`Contract`) as contract,
        `Paperless Billing` as paperless_billing,
        lower(`Payment Method`) as payment_method,
        `Monthly Charge` as monthly_charge,
        `Total Charges` as total_charges,
        `Total Refunds` as total_refunds,
        `Total Extra Data Charges` as total_extra_data_charges,
        `Total Long Distance Charges` as total_long_distance_charges,
        `Total Revenue` as total_revenue
    from source
)

select * from renamed
