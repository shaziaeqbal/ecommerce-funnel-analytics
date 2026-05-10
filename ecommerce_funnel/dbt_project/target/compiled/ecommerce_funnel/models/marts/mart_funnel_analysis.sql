SELECT
    channel,
    device,
    total_sessions,
    viewed_product,
    added_to_cart,
    reached_checkout,
    purchased,
    view_rate,
    cart_rate,
    checkout_rate,
    purchase_rate,
    ROUND((added_to_cart - purchased)*100.0/NULLIF(added_to_cart,0),2) AS abandonment_rate
FROM "ecommerce"."main"."int_funnel_steps"