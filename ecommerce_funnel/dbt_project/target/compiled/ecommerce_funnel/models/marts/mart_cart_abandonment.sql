SELECT
    s.session_id,
    s.user_id,
    s.channel,
    s.device,
    s.country,
    s.page_views,
    s.session_duration,
    s.bounce,
    s.added_to_cart,
    s.reached_checkout,
    s.purchased,
    CASE WHEN s.added_to_cart=1 AND s.purchased=0 THEN 1 ELSE 0 END AS abandoned
FROM "ecommerce"."main"."stg_sessions" s
WHERE s.added_to_cart = 1