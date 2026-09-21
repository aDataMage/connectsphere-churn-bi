-- Check age distribution
SELECT
    demographics.age,
    COUNT(*) AS count
FROM {{ ref('stg_telco__demographics') }} AS demographics
GROUP BY demographics.age

SELECT
    MIN(demographics.age),
    MEAN(demographics.age),
    MAX(demographics.age),
FROM {{ ref('stg_telco__demographics') }} AS demographics
GROUP BY demographics.age

-- Check gender distribution
SELECT
  demographics.gender,
  COUNT(*) AS count
FROM FROM {{ ref('stg_telco__demographics') }} AS demographics
GROUP BY demographics.age

