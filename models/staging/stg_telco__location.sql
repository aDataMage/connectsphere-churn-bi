/*
Date: 2024-06-19

   grain: one row per customer_id
   Count columns dropped as they were an artefact of the data_source
   Data Limited to `Country` = "United States" and `State` = "California" are both Constants and were dropped
   `lat_long` encodes same information as `latitude` and `longitude` and was dropped from the table
   Columns renamed to follow naming conventions
   cast `Zip Code` as string to ensure it is treated as a string and not a number
   All string columns are lower-cased at staging for consistency; `zip_code` is digits only so no lower() is applied
*/

with source as (

    select * from {{ source('telco', 'location') }}

),

renamed as (

    select
        lower(`Customer ID`) as customer_id,
        lower(`City`) as city,
        cast(`Zip Code` as string) as zip_code,
        `Latitude` as latitude,
        `Longitude` as longitude

    from source

)

select * from renamed
