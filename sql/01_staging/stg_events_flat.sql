CREATE OR REPLACE TABLE `{project}.{dataset}.events_flat`
CLUSTER BY event_name, user_pseudo_id AS
SELECT
  PARSE_DATE('%Y%m%d', event_date)    AS event_date,
  TIMESTAMP_MICROS(event_timestamp)   AS event_ts,
  event_name,
  user_pseudo_id,
  (SELECT value.int_value    FROM UNNEST(event_params) WHERE key = 'ga_session_id')     AS ga_session_id,
  (SELECT value.int_value    FROM UNNEST(event_params) WHERE key = 'ga_session_number') AS ga_session_number,
  (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'source')            AS session_source,
  (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'medium')            AS session_medium,
  device.category            AS device_category,
  device.operating_system    AS operating_system,
  device.web_info.browser    AS browser,
  geo.country                AS country,
  traffic_source.source      AS first_user_source,
  traffic_source.medium      AS first_user_medium,
  ecommerce.transaction_id   AS transaction_id,
  ecommerce.purchase_revenue_in_usd AS purchase_revenue_usd
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131';