## September 3rd

### Staging

**RULE: ONLY DROP REDUNDANT COLUMNS, RENAME COLUMNS, CHANGE DATA TYPE**

- ZIP loaded as integer, no data lost given California's range, cast to string in staging because it's an identifier not a quantity.
- 
- `Count` dropped as it is an artifact of the data warehouse
- Converted Column names to snake case
- Data Limited to `quater` = 3 and `Country` = "United States" and `State` = "Califonia" are both Constants and were all 3 columns dropped
- `lat_long` encodes same information as `latitude` and `longitude` and was dropped from the table
- `dependents` is reprodusible from `number_of_dependents` > 0. hence it is redundant and was dropped
- `under_30` and `senior_citizen` dropped at staging. as they are redundant columns needed bands will be derived from `age` at the intermidiate stage.
- `zip_id` has no infomational value and does not connect to any table and was dropped
- `churn_value` is an encoding of `churn_label` making it redundant hence it was dropped
- `zip_code` converted to string as no arimethic operation will be run on it
- kept possible leakage columns to be treated later

### Intermidiate

**Only transformations needed by all analyst**

- Created a single customer level table
- location table rolled up to `zip_code` grain so it can serve as a look up table
  - verified one `city` per zip
  - one `lat` and `long` set per`zip_code`
  - all customers `zip_code` present with populations
- population column added to zip_code lookup and population table dropped
- tenure bands not created due to not distingisable from noise



- no single headline churn rate, and every rate is reported within a band with its base and revenue attached.
- every non-churned customer at tenure ≤3 is Joined, every Stayed is ≥4, tenure divisions at 1-3,
<!-- 
"AI Overview        Domestic long-distance calling charges are mostly eliminated across the United States for modern mobile and VoIP plans, while international long-distance or traditional landlines still incur fees."

meaning long distance refers to leaving the states -->

Satisfaction is deterministic, not merely correlated. Score ≤2 → churned, always. Score ≥4 → stayed, always. Only score 3 contains both, split 429/2,236. There is no overlap anywhere else. That is not a leading indicator with predictive power; that's a field constructed from the outcome.



Joined users max tenure of 3 months would be treated a classifiaction aterfact

Dropped churn score as it is a model output and not useful in analysis

The denominator for churn rate is based on tenure band, dividing into new user(tenure 1 - 3), and mid < 1year, and above 1 year