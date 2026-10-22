-- 1. High-value transactions relative to a customer's typical spend
SELECT t.transaction_id, t.customer_id, t.amount, c.customer_avg_amount_30d,
       ROUND(t.amount / NULLIF(c.customer_avg_amount_30d, 0), 2) AS spend_multiple
FROM transactions t
JOIN customers c USING (customer_id)
WHERE t.amount >= 8 * c.customer_avg_amount_30d
ORDER BY spend_multiple DESC;

-- 2. Card velocity: more than four transactions in a rolling ten-minute window
SELECT transaction_id, card_id, transaction_timestamp,
       COUNT(*) OVER (
         PARTITION BY card_id
         ORDER BY transaction_timestamp
         RANGE BETWEEN INTERVAL '10 minutes' PRECEDING AND CURRENT ROW
       ) AS tx_count_10m
FROM transactions
QUALIFY COUNT(*) OVER (
  PARTITION BY card_id ORDER BY transaction_timestamp
  RANGE BETWEEN INTERVAL '10 minutes' PRECEDING AND CURRENT ROW
) > 4;

-- 3. Daily fraud and alert rates (assuming a decisions table or materialized output)
SELECT DATE(transaction_timestamp) AS tx_date,
       COUNT(*) AS transaction_count,
       SUM(CASE WHEN label_is_fraud THEN 1 ELSE 0 END) AS fraud_count
FROM transactions
GROUP BY DATE(transaction_timestamp)
ORDER BY tx_date;

-- 4. Merchant category exposure
SELECT merchant_category, COUNT(*) AS tx_count,
       AVG(amount) AS average_amount,
       SUM(CASE WHEN label_is_fraud THEN 1 ELSE 0 END) AS labelled_fraud_count
FROM transactions
GROUP BY merchant_category
ORDER BY labelled_fraud_count DESC;

-- Note: QUALIFY is supported by some warehouses (e.g. Snowflake/BigQuery).
-- For PostgreSQL, wrap the window-function query in a CTE and filter in the outer SELECT.
