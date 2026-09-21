/* 
Date: 2024-06-19
   grain: one row per customer_id
   dropped: Count columns dropped as they were an artefact of the data_source; `Dependents` is reprodusible from `Number of Dependents` > 0. hence it is redundant and was dropped; `Under 30` and `Senior Citizen` dropped at staging. as they are redundant columns needed bands will be derived from `Age` downstream
   Columns renamed to be more descriptive and to follow naming conventions
   All string columns are lower-cased at staging for consistency; the Yes/No columns land as booleans from the seed so they are left as-is
*/

with source as (

    select * from {{ source('telco', 'demographics') }}

),

renamed as (

    select
        lower(`Customer ID`) as customer_id,
        lower(`Gender`) as gender,
        `Age` as age,
        `Married` as married,
        `Number of Dependents` as number_of_dependents

    from source

)

select * from renamed
