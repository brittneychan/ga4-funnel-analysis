CREATE OR REPLACE TABLE `{project}.{dataset}.funnel_users` AS
WITH u AS (
  SELECT
    user_pseudo_id,
    LOGICAL_OR(o_view_item)      AS view_item,
    LOGICAL_OR(o_add_to_cart)    AS add_to_cart,
    LOGICAL_OR(o_begin_checkout) AS begin_checkout,
    LOGICAL_OR(o_purchase)       AS purchase,
    COUNT(*)                     AS n_sessions
  FROM `{project}.{dataset}.sessions`
  GROUP BY user_pseudo_id
)
SELECT
  COUNT(*)                AS users,
  COUNTIF(view_item)      AS users_view_item,
  COUNTIF(add_to_cart)    AS users_add_to_cart,
  COUNTIF(begin_checkout) AS users_begin_checkout,
  COUNTIF(purchase)       AS users_purchase,
  SAFE_DIVIDE(COUNTIF(purchase), COUNTIF(view_item)) AS user_view_to_purchase,
  AVG(IF(purchase, n_sessions, NULL))                AS avg_sessions_purchasers,
  AVG(IF(NOT purchase, n_sessions, NULL))            AS avg_sessions_non_purchasers
FROM u;