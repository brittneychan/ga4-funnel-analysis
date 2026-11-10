ASSERT (
  SELECT COUNT(*) = COUNT(DISTINCT session_key) FROM `{project}.{dataset}.sessions`
) AS 'session_key is not unique';

ASSERT (
  SELECT COUNTIF(c_add_to_cart) <= COUNTIF(c_view_item)
     AND COUNTIF(c_begin_checkout) <= COUNTIF(c_add_to_cart)
     AND COUNTIF(c_purchase) <= COUNTIF(c_begin_checkout)
  FROM `{project}.{dataset}.sessions`
) AS 'closed funnel is not monotonically decreasing';

ASSERT (
  SELECT ABS(
    (SELECT SUM(revenue_usd) FROM `{project}.{dataset}.sessions`) -
    (SELECT SUM(purchase_revenue_usd) FROM `{project}.{dataset}.events_flat`
      WHERE event_name = 'purchase' AND ga_session_id IS NOT NULL)
  ) < 1
) AS 'session revenue does not reconcile to event revenue';