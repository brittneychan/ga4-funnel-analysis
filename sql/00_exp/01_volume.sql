SELECT
    MIN(PARSE_DATE('%Y%m%d', event_date)) AS first_day,
    MAX(PARSE_DATE('%Y%m%d', event_date)) AS last_day,
    COUNT(DISTINCT event_date) AS n_days,
    COUNT(DISTINCT user_pseudo_id) AS n_users,
    COUNT(*) AS n_events
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`

