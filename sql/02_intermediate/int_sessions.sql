CREATE OR REPLACE TABLE `{project}.{dataset}.sessions`
CLUSTER BY device_category, channel_group AS
WITH ev AS (
  SELECT
    *,
    CONCAT(user_pseudo_id, '-', CAST(ga_session_id AS STRING)) AS session_key
  FROM `{project}.{dataset}.events_flat`
  WHERE ga_session_id IS NOT NULL
),

agg AS (
  SELECT
    session_key,
    ANY_VALUE(user_pseudo_id)   AS user_pseudo_id,
    MIN(event_date)             AS session_date,
    MIN(event_ts)               AS session_start_ts,
    MAX(event_ts)               AS session_end_ts,
    MAX(ga_session_number)      AS ga_session_number,

    ARRAY_AGG(device_category  IGNORE NULLS ORDER BY event_ts LIMIT 1)[SAFE_OFFSET(0)] AS device_category,
    ARRAY_AGG(operating_system IGNORE NULLS ORDER BY event_ts LIMIT 1)[SAFE_OFFSET(0)] AS operating_system,
    ARRAY_AGG(browser          IGNORE NULLS ORDER BY event_ts LIMIT 1)[SAFE_OFFSET(0)] AS browser,
    ARRAY_AGG(country          IGNORE NULLS ORDER BY event_ts LIMIT 1)[SAFE_OFFSET(0)] AS country,
    ARRAY_AGG(session_source   IGNORE NULLS ORDER BY event_ts LIMIT 1)[SAFE_OFFSET(0)] AS session_source,
    ARRAY_AGG(session_medium   IGNORE NULLS ORDER BY event_ts LIMIT 1)[SAFE_OFFSET(0)] AS session_medium,
    ANY_VALUE(first_user_source) AS first_user_source,
    ANY_VALUE(first_user_medium) AS first_user_medium,

    COUNT(*)                          AS n_events,
    COUNTIF(event_name = 'page_view') AS n_pageviews,

    MIN(IF(event_name = 'view_item',      event_ts, NULL)) AS ts_view_item,
    MIN(IF(event_name = 'add_to_cart',    event_ts, NULL)) AS ts_add_to_cart,
    MIN(IF(event_name = 'begin_checkout', event_ts, NULL)) AS ts_begin_checkout,
    MIN(IF(event_name = 'purchase',       event_ts, NULL)) AS ts_purchase,

    COUNT(DISTINCT IF(event_name = 'purchase', transaction_id, NULL)) AS n_transactions,
    SUM(IF(event_name = 'purchase', purchase_revenue_usd, 0))         AS revenue_usd
  FROM ev
  GROUP BY session_key
),

labeled AS (
  SELECT
    *,
    COALESCE(session_source, first_user_source) AS src,
    COALESCE(session_medium, first_user_medium) AS med
  FROM agg
)

SELECT
  * EXCEPT (src, med),
  src AS source_used,
  med AS medium_used,
  CASE
    WHEN med IS NULL OR med IN ('<Other>', '(data deleted)') THEN 'Unknown / obfuscated'
    WHEN med IN ('(none)', '(not set)')                      THEN 'Direct'
    WHEN med = 'organic'                                     THEN 'Organic Search'
    WHEN med IN ('cpc', 'ppc', 'paidsearch')                 THEN 'Paid Search'
    WHEN med = 'referral'                                    THEN 'Referral'
    WHEN med = 'email'                                       THEN 'Email'
    WHEN REGEXP_CONTAINS(med, r'^(display|cpm|banner)$')     THEN 'Display'
    WHEN REGEXP_CONTAINS(med, r'social')                     THEN 'Social'
    ELSE 'Other'
  END AS channel_group,
  IF(ga_session_number = 1, 'New', 'Returning') AS visitor_type,

  -- OPEN funnel: step happened at any point in the session
  ts_view_item      IS NOT NULL AS o_view_item,
  ts_add_to_cart    IS NOT NULL AS o_add_to_cart,
  ts_begin_checkout IS NOT NULL AS o_begin_checkout,
  ts_purchase       IS NOT NULL AS o_purchase,

  -- CLOSED funnel: step happened, at or after the previous closed step
  ts_view_item IS NOT NULL AS c_view_item,
  IFNULL(ts_view_item IS NOT NULL AND ts_add_to_cart >= ts_view_item, FALSE) AS c_add_to_cart,
  IFNULL(ts_view_item IS NOT NULL AND ts_add_to_cart >= ts_view_item
         AND ts_begin_checkout >= ts_add_to_cart, FALSE) AS c_begin_checkout,
  IFNULL(ts_view_item IS NOT NULL AND ts_add_to_cart >= ts_view_item
         AND ts_begin_checkout >= ts_add_to_cart
         AND ts_purchase >= ts_begin_checkout, FALSE) AS c_purchase
FROM labeled;