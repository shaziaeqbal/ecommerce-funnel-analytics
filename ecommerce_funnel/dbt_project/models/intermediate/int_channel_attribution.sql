SELECT
    s.channel,
    COUNT(DISTINCT s.session_id)  AS sessions,
    COUNT(DISTINCT t.transaction_id) AS transactions,
    ROUND(SUM(t.revenue),2)       AS total_revenue,
    ROUND(AVG(t.revenue),2)       AS avg_order_value
FROM {{ ref('stg_sessions') }} s
LEFT JOIN {{ ref('stg_transactions') }} t USING (session_id)
GROUP BY 1
