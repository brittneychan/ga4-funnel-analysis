SELECT
    event_name,
    COUNT(*) AS n_events,
    COUNT(DISTINCT user_pseudo_id) AS n_users,
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
GROUP BY event_name
ORDER BY n_events DESC