## Staging

### Date: 2024-06-19

  Input table: demographics: <br>

- grain: one row per customer_id
- dropped: Count columns dropped as they were an artefact of the data_source; `Dependents` is reprodusible from `Number of Dependents` > 0. hence it is redundant and was dropped; `Under 30` and `Senior Citizen` dropped at staging. as they are redundant columns needed bands will be derived from `Age` downstream <br>

  Output view: stg_telco__demographics `models\staging\stg_telco__demographics.sql`

  Input table: services: <br>

- grain: one row per customer_id
- dropped: Count columns dropped as they were an artefact of the data_source; `Quarter` is a constant and was dropped

  Output view: stg_telco__services `models\staging\stg_telco__services.sql`

  Input table: locations: <br>

- grain: one row per customer_id
- dropped: Data Limited to `Country` = "United States" and `State` = "California" are both Constants and were dropped `lat_long` encodes same information as `latitude` and `longitude` and was dropped from the table
- cast `Zip Code` as string to ensure it is treated as a string and not a number

  Output view: stg_telco__locations `models\staging\stg_telco__locations.sql`

  Input table: population: <br>

- grain: one row per zip_code
- dropped: Count columns dropped as they were an artefact of the data_source; `zip_id` has no infomational value and does not connect to any table and was dropped
- cast `Zip Code` as string to ensure it is treated as a string and not a number
  Output view: stg_telco__population `models\staging\stg_telco__population.sql`

  Input table: status: <br>

- grain: one row per customer_id
- dropped: Count columns dropped as they were an artefact of the data_source; `churn_value` is an encoding of `churn_label` making it redundant hence it was dropped; `Quarter` is a constant and was dropped
  
  Output view: stg_telco__status `models\staging\stg_telco__status.sql`

 All Columns renamed to be more descriptive and to follow naming conventions
 Count columns dropped from all tables as they were an artefact of the data_source

### Date: 2026-09-18

  Decision: lower-case all string columns in the staging layer <br>

- Applied across every staging model so downstream filters, joins and group-bys never have to worry about casing from the raw export
- Lowered: `customer_id`, `gender` (demographics); `customer_id`, `country`, `state`, `city` (location); `customer_id`, `offer`, `internet_type`, `contract`, `payment_method` (services); `customer_id`, `customer_status`, `churn_reason`, `churn_category` (status)
- `customer_id` is lowered in all four models that carry it, so ids read as `8779-qrdmv` rather than `8779-QRDMV`; joins in the marts still match because every side is lowered identically
- Not lowered: the Yes/No columns (`married`, `churn_label`, `phone_service`, `multiple_lines`, the security/streaming flags, `paperless_billing`, etc.) land as BOOL from the seed loader, not strings - `lower()` on them fails static analysis with an argument type mismatch
- Not lowered: `zip_code` is cast to string but is digits only, so `lower()` would be a no-op
- population has no string columns beyond `zip_code`, so it is unchanged

  Follow-up: the `senior_citizen` description in `models\staging\_telco__models.yml` still says the raw values are 'Yes'/'No' strings; they are booleans in the warehouse, so that note (and any planned intermediate-layer cast) is stale

## Marts

### Date: 2026-09-25

  Decision: one shared customer fact, with a separate layer for each dashboard <br>

- `fct_customer_churn` (one row per customer, all 7,043) derives every band, flag and profile score once, so neither BI tool re-derives them and both agree with `docs/story.md`
- Power BI reads it as a star schema: `fct_customer_churn` + `dim_geography` (one row per zip, built on `zip_lookup`). Bands stay on the fact rather than in their own dimensions: with a single fact table, separate band dimensions add joins with nothing to share
- The Tableau story reads pre-aggregated exhibits (`rpt_story_segments`, one exhibit per chart in the story) and the cost estimates (`rpt_story_cost_estimates`), because Tableau cannot compute Wilson or Newcombe intervals and the story's numbers must match to the decimal
- Every band carries a `*_sort` column so BI tools order it correctly (Power BI: Sort by column)
- Leakage columns (`satisfaction_score`, `churn_score`) are excluded, as in `customers_chun`
- `internet_type` 'none' is relabelled 'no internet': the staging model stores the string 'none', not NULL, so `IFNULL` handling silently drops those 1,274 customers
- `is_churned` is an integer so `SUM` counts churners and `AVG` is the churn rate
- Intervals come from a macro (`macros/confidence_intervals.sql`) that matches statsmodels exactly (verified: fiber gap lower bound 0.2425, excess billing $37,377.80)
- Exposures (`models/marts/_exposures.yml`) declare both dashboards, so lineage shows what feeds each one
- `tests/assert_story_parity.sql` checks the story's headline figures against the marts; severity is warn, so a data refresh flags the story as stale without blocking the build
- `customers_chun` and `zip_lookup` are left unchanged; `customers_chun` overlaps with `fct_customer_churn` and could be retired once nothing reads it

  Output tables: fct_customer_churn `models\marts\fct_customer_churn.sql`, dim_geography `models\marts\dim_geography.sql`, rpt_story_segments `models\marts\rpt_story_segments.sql`, rpt_story_cost_estimates `models\marts\rpt_story_cost_estimates.sql`
