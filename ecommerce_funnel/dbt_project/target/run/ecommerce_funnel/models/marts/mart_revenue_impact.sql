
  
    
    

    create  table
      "ecommerce"."main"."mart_revenue_impact__dbt_tmp"
  
    as (
      WITH base AS (
    SELECT
        channel,
        COUNT(*) FILTER (WHERE abandoned=1) AS abandoned_carts,
        COUNT(*) FILTER (WHERE abandoned=0) AS converted_carts,
        COUNT(*)                             AS total_carts
    FROM "ecommerce"."main"."mart_cart_abandonment"
    GROUP BY 1
),
aov AS (
    SELECT ROUND(AVG(revenue),2) AS avg_order_value
    FROM "ecommerce"."main"."stg_transactions"
)
SELECT
    b.channel,
    b.abandoned_carts,
    b.converted_carts,
    b.total_carts,
    a.avg_order_value,
    ROUND(b.abandoned_carts * a.avg_order_value, 2)          AS lost_revenue,
    ROUND(b.abandoned_carts * a.avg_order_value * 0.10, 2)   AS recovery_10pct,
    ROUND(b.abandoned_carts * a.avg_order_value * 0.20, 2)   AS recovery_20pct
FROM base b CROSS JOIN aov a
    );
  
  