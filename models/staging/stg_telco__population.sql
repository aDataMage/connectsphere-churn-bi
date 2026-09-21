/*  
Date: 2024-06-19
    grain: one row per zip_code
    dropped: Count columns dropped as they were an artefact of the data_source; `zip_id` has no infomational value and does not connect to any table and was dropped
    Columns renamed to be more descriptive and to follow naming conventions
    cast `Zip Code` as string to ensure it is treated as a string and not a number
    All string columns are lower-cased at staging for consistency; `zip_code` is digits only so no lower() is applied
*/

with source as (

    select * from {{ source('telco', 'population') }}

),

renamed as (

    select
        cast(`Zip Code` as string) as zip_code,
        `Population` as population

    from source

)

select * from renamed
