
  
  create view "ecommerce"."main"."stg_transactions__dbt_tmp" as (
    SELECT
    transaction_id,
    session_id,
    user_id,
    category,
    revenue,
    quantity,
    transaction_date
FROM transactions
  );
