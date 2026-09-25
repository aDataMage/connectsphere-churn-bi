SELECT
  se.internet_type,
  if(d.age < 65, 'non-senior','senior') as age_group,
  COUNT(*) AS customers,
  COUNTIF(st.churn_label) AS churners
FROM
  `dbt_dev.stg_telco__services` se
  JOIN `dbt_dev.stg_telco__status` st USING (customer_id)
  JOIN `dbt_dev.stg_telco__demographics` d USING (customer_id)
WHERE
  se.tenure_in_months > 3
GROUP BY
  internet_type,
  age_group
