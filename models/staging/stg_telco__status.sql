/* 
Date: 2024-06-19
   grain: one row per customer_id
   dropped: Count columns dropped as they were an artefact of the data_source; `churn_value` is an encoding of `churn_label` making it redundant hence it was dropped; `Quarter` is a constant and was dropped
   Columns renamed to be more descriptive and to follow naming conventions
   All string columns are lower-cased at staging for consistency; the Yes/No columns land as booleans from the seed so they are left as-is
*/

with source as (
    select * from {{source('telco', 'status')}}
),

renamed as (
    select
        lower(`Customer ID`) as customer_id,
        lower(`Customer Status`) as customer_status,
        `Satisfaction Score` as satisfaction_score,
        `Churn Label` as churn_label,
        `Churn Score` as churn_score,
        `CLTV` as cltv,
        lower(`Churn Reason`) as churn_reason,
        lower(`Churn Category`) as churn_category

    from source
)

select * from renamed
