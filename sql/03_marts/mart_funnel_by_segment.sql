CREATE OR REPLACE TABLE `{project}.{dataset}.funnel_by_segment` AS
WITH s AS (SELECT * FROM `{project}.{dataset}.sessions`),
long AS (
  SELECT 'device' AS dimension, IFNULL(device_category, '(unknown)') AS segment,
         c_view_item, c_add_to_cart, c_begin_checkout, c_purchase, n_transactions, revenue_usd FROM s
  UNION ALL
  SELECT 'channel', channel_group,
         c_view_item, c_add_to_cart, c_begin_checkout, c_purchase, n_transactions, revenue_usd FROM s
  UNION ALL
  SELECT 'visitor_type', visitor_type,
         c_view_item, c_add_to_cart, c_begin_checkout, c_purchase, n_transactions, revenue_usd FROM s
)
SELECT
  dimension,
  segment,
  COUNT(*)                   AS sessions,
  COUNTIF(c_view_item)       AS n_view,
  COUNTIF(c_add_to_cart)     AS n_cart,
  COUNTIF(c_begin_checkout)  AS n_checkout,
  COUNTIF(c_purchase)        AS n_purchase,
  SAFE_DIVIDE(COUNTIF(c_add_to_cart),    COUNTIF(c_view_item))      AS view_to_cart,
  SAFE_DIVIDE(COUNTIF(c_begin_checkout), COUNTIF(c_add_to_cart))    AS cart_to_checkout,
  SAFE_DIVIDE(COUNTIF(c_purchase),       COUNTIF(c_begin_checkout)) AS checkout_to_purchase,
  SAFE_DIVIDE(COUNTIF(c_purchase),       COUNTIF(c_view_item))      AS view_to_purchase,
  SUM(n_transactions)        AS transactions,
  SUM(revenue_usd)           AS revenue_usd,
  SAFE_DIVIDE(SUM(revenue_usd), NULLIF(SUM(n_transactions), 0)) AS aov_usd
FROM long
GROUP BY dimension, segment
HAVING COUNT(*) >= 500   -- drop tiny segments whose rates are mostly noise
ORDER BY dimension, sessions DESC;