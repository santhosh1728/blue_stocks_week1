import sqlite3
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

db_path = "02_sql_practice/retail_sales.db"
conn = sqlite3.connect(db_path)

print("=" * 80)
print("WEEK 2: EXECUTING ADVANCED SQL & COHORT ANALYTICS SUITE")
print(f"Target Database: {db_path}")
print("=" * 80)

# 1. Cohort Retention Matrix
q_cohort = """
WITH Customer_Cohort AS (
    SELECT 
        customer_id,
        MIN(SUBSTR(order_date, 1, 7)) AS Cohort_Month
    FROM orders
    WHERE order_status = 'Completed'
    GROUP BY customer_id
),
Customer_Activities AS (
    SELECT 
        o.customer_id,
        cc.Cohort_Month,
        SUBSTR(o.order_date, 1, 7) AS Purchase_Month,
        (CAST(SUBSTR(o.order_date, 1, 4) AS INT) - CAST(SUBSTR(cc.Cohort_Month, 1, 4) AS INT)) * 12 +
        (CAST(SUBSTR(o.order_date, 6, 2) AS INT) - CAST(SUBSTR(cc.Cohort_Month, 6, 2) AS INT)) AS Month_Index
    FROM orders o
    JOIN Customer_Cohort cc ON o.customer_id = cc.customer_id
    WHERE o.order_status = 'Completed'
    GROUP BY o.customer_id, cc.Cohort_Month, SUBSTR(o.order_date, 1, 7)
),
Cohort_Sizes AS (
    SELECT 
        Cohort_Month,
        COUNT(DISTINCT customer_id) AS Initial_Users
    FROM Customer_Cohort
    GROUP BY Cohort_Month
)
SELECT 
    ca.Cohort_Month,
    cs.Initial_Users,
    COUNT(DISTINCT CASE WHEN ca.Month_Index = 0 THEN ca.customer_id END) AS M0_Active,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ca.Month_Index = 1 THEN ca.customer_id END) / cs.Initial_Users, 1) AS M1_Retention_Pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ca.Month_Index = 2 THEN ca.customer_id END) / cs.Initial_Users, 1) AS M2_Retention_Pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ca.Month_Index = 3 THEN ca.customer_id END) / cs.Initial_Users, 1) AS M3_Retention_Pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ca.Month_Index = 6 THEN ca.customer_id END) / cs.Initial_Users, 1) AS M6_Retention_Pct
FROM Customer_Activities ca
JOIN Cohort_Sizes cs ON ca.Cohort_Month = cs.Cohort_Month
GROUP BY ca.Cohort_Month, cs.Initial_Users
ORDER BY ca.Cohort_Month;
"""

print("\n>>> [Query 1] Customer Retention Cohort Matrix:")
df_cohort = pd.read_sql_query(q_cohort, conn)
print(df_cohort.to_string(index=False))

# 2. Date Spine Generator
q_spine = """
WITH RECURSIVE Date_Series AS (
    SELECT DATE('2024-01-01') AS Calendar_Date
    UNION ALL
    SELECT DATE(Calendar_Date, '+1 day')
    FROM Date_Series
    WHERE Calendar_Date < '2024-01-10'
)
SELECT 
    ds.Calendar_Date,
    CASE STRFTIME('%w', ds.Calendar_Date)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        ELSE 'Saturday'
    END AS Day_Name,
    COUNT(o.order_id) AS Orders_Placed,
    COALESCE(ROUND(SUM(oi.sales_amount), 2), 0.00) AS Daily_Revenue
FROM Date_Series ds
LEFT JOIN orders o ON ds.Calendar_Date = o.order_date AND o.order_status = 'Completed'
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY ds.Calendar_Date
ORDER BY ds.Calendar_Date;
"""
print("\n>>> [Query 2] Recursive Date Spine (Gap Detection):")
df_spine = pd.read_sql_query(q_spine, conn)
print(df_spine.to_string(index=False))

# 3. Semi-Join with EXISTS
q_exists = """
SELECT 
    c.customer_id,
    c.customer_name,
    c.segment,
    c.country
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.customer_id = c.customer_id
      AND p.category = 'Technology'
      AND o.order_status = 'Completed'
)
ORDER BY c.customer_name
LIMIT 5;
"""
print("\n>>> [Query 3] Semi-Join (EXISTS Short-Circuit):")
df_exists = pd.read_sql_query(q_exists, conn)
print(df_exists.to_string(index=False))

# 4. EXPLAIN QUERY PLAN
q_explain = """
EXPLAIN QUERY PLAN
SELECT 
    o.order_id, 
    c.customer_name, 
    SUM(oi.sales_amount) AS total_spent
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_date >= '2025-01-01'
GROUP BY o.order_id, c.customer_name;
"""
print("\n>>> [Query 4] EXPLAIN QUERY PLAN (Index Evaluation):")
df_explain = pd.read_sql_query(q_explain, conn)
print(df_explain.to_string(index=False))

conn.close()
print("\n" + "=" * 80)
print("WEEK 2 ADVANCED SQL EXECUTION SUCCESSFUL!")
print("=" * 80)

