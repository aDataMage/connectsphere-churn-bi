/*
 STAGING LAYER
  The staging layer is the first layer of the data warehouse. It is used to store raw data from the source systems. 
  The staging layer is used to perform rename columns, drop columns, and adjust data type. The staging layer is also used to create views that can be used by the next layer of the data warehouse.

  Read decision log for informaation on the chages made to the source data and the reasons for those changes.

  OUTPUT: VIEWS - stg_demographics, stg_location, stg_population, stg_services, stg_status
*/


CREATE VIEW telco_churn.stg_demographics AS
SELECT
  customer_id,
  gender,
  age,
  married,
  number_of_dependents
FROM `focus-appliance-507309-h8.telco_churn.demographics`;

CREATE VIEW telco_churn.stg_location AS
SELECT
  customer_id,
  city,
  CAST(zip_code AS STRING) AS zip_code,
  latitude,
  longitude
FROM `focus-appliance-507309-h8.telco_churn.location`;

CREATE VIEW telco_churn.stg_population AS
SELECT
  CAST(zip_code AS STRING) AS zip_code,
  population
FROM `focus-appliance-507309-h8.telco_churn.population`;

CREATE VIEW telco_churn.stg_services AS
SELECT
  customer_id,
  referred_a_friend,
  tenure_in_months,
  offer,
  phone_service,
  avg_monthly_long_distance_charges,
  multiple_lines,
  internet_service,
  internet_type,
  avg_monthly_gb_download,
  online_security,
  online_backup,
  device_protection_plan,
  premium_tech_support,
  streaming_tv,
  streaming_movies,
  unlimited_data,
  contract,
  paperless_billing,
  payment_method,
  monthly_charge,
  total_charges,
  total_refunds,
  total_extra_data_charges,
  total_long_distance_charges,
  total_revenue
FROM `focus-appliance-507309-h8.telco_churn.services`;

CREATE VIEW telco_churn.stg_status AS
SELECT
  customer_id,
  customer_status,
  churn_label,
  cltv,
  satisfaction_score,
  churn_score,
  churn_category,
  churn_reason
FROM `focus-appliance-507309-h8.telco_churn.status`