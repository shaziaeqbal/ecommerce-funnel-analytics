
  
  create view "ecommerce"."main"."stg_sessions__dbt_tmp" as (
    SELECT
    session_id,
    user_id,
    channel,
    device,
    country,
    session_date,
    page_views,
    session_duration,
    bounce,
    viewed_product,
    added_to_cart,
    reached_checkout,
    purchased
FROM sessions
  );
