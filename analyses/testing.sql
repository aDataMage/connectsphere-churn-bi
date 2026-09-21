WITH
  base AS (
    SELECT
      CASE
        WHEN se.payment_method = 'credit card' THEN 'card'
        ELSE 'non-card'
      END AS pay,
      se.contract,
      st.churn_label
    FROM
      `focus-appliance-507309-h8.dbt_dev.stg_telco__services` se
      JOIN `focus-appliance-507309-h8.dbt_dev.stg_telco__status` st USING (customer_id)
    WHERE
      se.tenure_in_months > 3
  )
-- SELECT
--   contract,
--   pay,
--   COUNT(*) AS customers,
--   COUNTIF(churn_label) AS churners,
--   ROUND(SAFE_DIVIDE(COUNTIF(churn_label), COUNT(*)), 3) AS churn_rate
-- FROM
--   base
-- GROUP BY
--   contract,
--   pay
-- ORDER BY
--   contract,
--   pay


select
  pay,
  count(*) as customers,
  round(countif(contract = 'two year') / count(*), 3) as pct_twoyear,
  round(countif(contract = 'one year') / count(*), 3) as pct_oneyear,
  round(countif(contract = 'month-to-month') / count(*), 3) as pct_m2m
from base
group by pay
