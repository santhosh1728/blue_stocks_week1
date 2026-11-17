/* ==============================================================================
   DATA ANALYST ADVANCED SQL REPOSITORY (WEEK 2)
   Database: retail_sales.db
   Focus: Cohort Retention Analysis, Recursive CTEs, Query Optimization & Indexing
   ============================================================================== */

-- ==============================================================================
-- 1. COHORT RETENTION MATRIX (MONTHLY ACQUISITION TO REPEAT PURCHASE RETENTION)
-- ==============================================================================
-- Business Goal: Measure what percentage of customers acquired in a given month
-- continue to purchase in Month 1, Month 2, Month 3, etc.
WITH Customer_Cohort AS (
    -- Step 1: Identify the acquisition month (first purchase) for each customer
    SELECT 
        customer_id,
        MIN(SUBSTR(order_date, 1, 7)) AS Cohort_Month
    FROM orders
    WHERE order_status = 'Completed'
    GROUP BY customer_id
),
Customer_Activities AS (
    -- Step 2: Extract all subsequent purchase months for each customer
    SELECT 
        o.customer_id,
        cc.Cohort_Month,
        SUBSTR(o.order_date, 1, 7) AS Purchase_Month,
        -- Calculate index of activity (months since cohort start)
        (CAST(SUBSTR(o.order_date, 1, 4) AS INT) - CAST(SUBSTR(cc.Cohort_Month, 1, 4) AS INT)) * 12 +
        (CAST(SUBSTR(o.order_date, 6, 2) AS INT) - CAST(SUBSTR(cc.Cohort_Month, 6, 2) AS INT)) AS Month_Index
    FROM orders o
    JOIN Customer_Cohort cc ON o.customer_id = cc.customer_id
    WHERE o.order_status = 'Completed'
    GROUP BY o.customer_id, cc.Cohort_Month, SUBSTR(o.order_date, 1, 7)
),
Cohort_Sizes AS (
    -- Step 3: Count total initial customers in each cohort (Month 0)
    SELECT 
        Cohort_Month,
        COUNT(DISTINCT customer_id) AS Initial_Users
    FROM Customer_Cohort
    GROUP BY Cohort_Month
)
-- Step 4: Pivot and calculate retention rates across Month 0, 1, 2, 3
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
ORDER BY ca.Cohort_Month
LIMIT 10;


-- ==============================================================================
-- 2. RECURSIVE CTE: DYNAMIC DATE SPINE GENERATOR
-- ==============================================================================
-- Business Goal: Create a continuous daily date series to identify days with zero sales
-- (Handling missing dates without gaps in time-series reporting)
WITH RECURSIVE Date_Series AS (
    -- Anchor Member: Start Date
    SELECT DATE('2024-01-01') AS Calendar_Date
    UNION ALL
    -- Recursive Member: Increment by 1 day until boundary
    SELECT DATE(Calendar_Date, '+1 day')
    FROM Date_Series
    WHERE Calendar_Date < '2024-01-15'
)
SELECT 
    ds.Calendar_Date,
    STRFTIME('%w', ds.Calendar_Date) AS Day_Of_Week_Num,
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


-- ==============================================================================
-- 3. RECURSIVE CTE: ORGANIZATIONAL HIERARCHY TREE
-- ==============================================================================
-- Business Goal: Traverse an employee hierarchy (Manager -> Lead -> Analyst) and calculate depth
WITH RECURSIVE Org_Hierarchy AS (
    -- Anchor: Top executive (no manager)
    SELECT 
        1 AS emp_id, 'Sarah Jenkins' AS emp_name, 'VP of Analytics' AS title, NULL AS manager_id, 1 AS org_level, 'Sarah Jenkins' AS hierarchy_path
    UNION ALL
    SELECT 2, 'David Vance', 'Director of BI', 1, 2, 'Sarah Jenkins -> David Vance'
    UNION ALL
    SELECT 3, 'Elena Rostova', 'Data Engineering Lead', 1, 2, 'Sarah Jenkins -> Elena Rostova'
    UNION ALL
    SELECT 4, 'Marcus Brody', 'Senior BI Analyst', 2, 3, 'Sarah Jenkins -> David Vance -> Marcus Brody'
    UNION ALL
    SELECT 5, 'Priya Nair', 'Data Analyst', 2, 3, 'Sarah Jenkins -> David Vance -> Priya Nair'
    UNION ALL
    SELECT 6, 'Kenji Sato', 'Analytics Engineer', 3, 3, 'Sarah Jenkins -> Elena Rostova -> Kenji Sato'
)
SELECT 
    org_level,
    title,
    emp_name,
    hierarchy_path
FROM Org_Hierarchy
ORDER BY org_level, emp_name;


-- ==============================================================================
-- 4. ANTI-JOIN & SEMI-JOIN PATTERNS (EXISTS vs IN vs LEFT JOIN)
-- ==============================================================================
-- Semi-Join: Identify all customers who bought from 'Technology' at least once
-- Concept: EXISTS halts execution as soon as the first match is found (Short-circuit optimization)
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
LIMIT 10;

-- Anti-Join: Customers who have NEVER placed an order using 'Apple Pay'
SELECT 
    c.customer_id,
    c.customer_name,
    c.city,
    c.country
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 
    FROM orders o
    WHERE o.customer_id = c.customer_id
      AND o.payment_method = 'Apple Pay'
)
ORDER BY c.customer_name
LIMIT 10;


-- ==============================================================================
-- 5. ADVANCED QUERY PERFORMANCE TUNING & EXPLAIN QUERY PLAN
-- ==============================================================================
-- Auditing query execution engine decisions:
-- 1. Scan vs Index Search
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

