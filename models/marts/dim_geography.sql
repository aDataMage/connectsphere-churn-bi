/*
  Date: 2026-09-25

  grain: one row per zip_code
  Geography dimension for the Power BI model, built on zip_lookup so the city,
  coordinate and population rules verified there are kept, not repeated.
  - density_class uses zip population as a density proxy: there is no area
    field, so this is zip size, not people per square mile
  - thresholds match the analysis: rural < 5k, suburban 5k-25k, urban 25k+
*/

select
    zip_code,
    city,
    latitude,
    longitude,
    population,
    case
        when population is null then 'unknown'
        when population < 5000 then 'rural (<5k)'
        when population < 25000 then 'suburban (5k-25k)'
        else 'urban (25k+)'
    end as density_class,
    case
        when population is null then 4
        when population < 5000 then 1
        when population < 25000 then 2
        else 3
    end as density_class_sort
from {{ ref('zip_lookup') }}
