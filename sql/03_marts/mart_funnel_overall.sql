CREATE OR REPLACE TABLE `{project}.{dataset}.funnel_overall` AS
WITH s AS (SELECT * FROM `{project}.{dataset}.sessions`),
counts AS (
  SELECT 'closed' AS funnel_type, 1 AS step_order, 'view_item' AS step, COUNTIF(c_view_item) AS sessions FROM s
  UNION ALL SELECT 'closed', 2, 'add_to_cart',    COUNTIF(c_add_to_cart)    FROM s
  UNION ALL SELECT 'closed', 3, 'begin_checkout', COUNTIF(c_begin_checkout) FROM s
  UNION ALL SELECT 'closed', 4, 'purchase',       COUNTIF(c_purchase)       FROM s
  UNION ALL SELECT 'open',   1, 'view_item',      COUNTIF(o_view_item)      FROM s
  UNION ALL SELECT 'open',   2, 'add_to_cart',    COUNTIF(o_add_to_cart)    FROM s
  UNION ALL SELECT 'open',   3, 'begin_checkout', COUNTIF(o_begin_checkout) FROM s
  UNION ALL SELECT 'open',   4, 'purchase',       COUNTIF(o_purchase)       FROM s
)
SELECT
  *,
  SAFE_DIVIDE(sessions, FIRST_VALUE(sessions) OVER w) AS pct_of_top,
  SAFE_DIVIDE(sessions, LAG(sessions) OVER w)         AS step_conversion,
  1 - SAFE_DIVIDE(sessions, LAG(sessions) OVER w)     AS step_dropoff
FROM counts
WINDOW w AS (PARTITION BY funnel_type ORDER BY step_order);