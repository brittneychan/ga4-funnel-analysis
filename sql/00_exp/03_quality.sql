WITH base AS (
  SELECT
    event_name,
    (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS ga_session_id,
    (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'medium')     AS session_medium,
    traffic_source.medium AS first_user_medium,
    device.category       AS device_category,
    ecommerce.transaction_id,
    ecommerce.purchase_revenue_in_usd
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
)
SELECT
  COUNT(*) AS n_events,
  SAFE_DIVIDE(COUNTIF(ga_session_id IS NULL), COUNT(*))  AS pct_events_no_session_id,
  SAFE_DIVIDE(COUNTIF(session_medium IS NOT NULL), COUNT(*)) AS pct_events_with_session_medium,
  SAFE_DIVIDE(COUNTIF(first_user_medium IN ('<Other>', '(data deleted)')), COUNT(*)) AS pct_medium_obfuscated,
  SAFE_DIVIDE(COUNTIF(device_category IS NULL), COUNT(*)) AS pct_no_device,
  COUNTIF(event_name = 'purchase') AS purchase_events,
  COUNT(DISTINCT IF(event_name = 'purchase', transaction_id, NULL)) AS distinct_txn_ids,
  COUNTIF(event_name = 'purchase'
          AND (transaction_id IS NULL OR transaction_id = '(not set)')) AS purchases_missing_txn_id,
  COUNTIF(event_name = 'purchase' AND purchase_revenue_in_usd IS NULL) AS purchases_null_revenue,
  SUM(IF(event_name = 'purchase', purchase_revenue_in_usd, 0))        AS total_revenue_usd
FROM base;