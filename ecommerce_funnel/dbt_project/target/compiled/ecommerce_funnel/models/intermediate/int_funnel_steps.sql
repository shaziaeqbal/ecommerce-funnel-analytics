SELECT
    channel,
    device,
    COUNT(*)                          AS total_sessions,
    SUM(viewed_product)               AS viewed_product,
    SUM(added_to_cart)                AS added_to_cart,
    SUM(reached_checkout)             AS reached_checkout,
    SUM(purchased)                    AS purchased,
    ROUND(SUM(viewed_product)*100.0  / COUNT(*),2)        AS view_rate,
    ROUND(SUM(added_to_cart)*100.0   / NULLIF(SUM(viewed_product),0),2)  AS cart_rate,
    ROUND(SUM(reached_checkout)*100.0/ NULLIF(SUM(added_to_cart),0),2)   AS checkout_rate,
    ROUND(SUM(purchased)*100.0       / NULLIF(SUM(reached_checkout),0),2) AS purchase_rate
FROM "ecommerce"."main"."stg_sessions"
GROUP BY 1,2