/* 
  Date: 2024-06-16

  grain: one row per zip_code
  location table rolled up to `zip_code` grain so it can serve as a look up table
  - verified one `city` per zip
  - one `lat` and `long` set per`zip_code`
  - all customers `zip_code` present with populations
- population column added to zip_code lookup and population table dropped
*/

with zip_location as (
  select
    zip_code,
    city,
    latitude,
    longitude
  from {{ ref('stg_telco__location') }}
  group by zip_code, city, latitude, longitude
)

select l.*, p.population
from zip_location l
left join {{ ref('stg_telco__population') }} p using(zip_code)
