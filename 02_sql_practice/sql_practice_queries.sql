/* ==============================================================================
   DATA ANALYST SQL MASTER PRACTICE REPOSITORY
   Database: retail_sales.db (SQLite / ANSI SQL Compliant)
   Tables:
     - customers   (customer_id, customer_name, email, city, state, country, region, segment, signup_date)
     - products    (product_id, product_name, category, subcategory, cost_price, unit_price)
     - orders      (order_id, customer_id, order_date, ship_date, ship_mode, payment_method, order_status)
     - order_items (order_item_id, order_id, product_id, quantity, unit_price, discount_rate, sales_amount, profit)
   ============================================================================== */

-- ==============================================================================
-- LEVEL 1: FOUNDATION QUERYING (SELECT, WHERE, ORDER BY, LIMIT, LOGICAL OPERATORS)
-- ==============================================================================

-- Query 1.1: Select specific customer attributes with alias formatting
-- Concept: Column selection, column alias, LIMIT
SELECT 
    customer_id AS Client_ID,
    customer_name AS Full_Name,
    city AS City,
    country AS Country,
    segment AS Market_Segment
FROM customers
ORDER BY customer_name ASC
LIMIT 10;

-- Query 1.2: Filter high-value completed orders with multiple conditions
-- Concept: WHERE clause, AND operator, equality, comparison
SELECT 
    order_id,
    customer_id,
    order_date,
    ship_mode,
    order_status
FROM orders
WHERE order_status = 'Completed'
  AND ship_mode IN ('First Class', 'Same Day')
  AND order_date >= '2024-06-01'
ORDER BY order_date DESC
LIMIT 10;

-- Query 1.3: Pattern matching and NULL checking
-- Concept: LIKE wildcard, IS NOT NULL
SELECT 
    product_id,
    product_name,
    category,
    unit_price
FROM products
WHERE (product_name LIKE '%Pro%' OR product_name LIKE '%Ultra%')
  AND unit_price BETWEEN 500.0 AND 2500.0
ORDER BY unit_price DESC;

-- Query 1.4: CASE WHEN categorical transformation
-- Concept: Conditional classification into custom business tiers
SELECT 
    product_name,
    category,
    unit_price,
    CASE 
        WHEN unit_price >= 1000 THEN 'Premium / Luxury'
        WHEN unit_price BETWEEN 300 AND 999.99 THEN 'Mid-Tier'
        ELSE 'Budget / Standard'
    END AS Price_Tier
FROM products
ORDER BY unit_price DESC
LIMIT 15;


-- ==============================================================================
-- LEVEL 2: AGGREGATE FUNCTIONS & GROUPING (COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING)
-- ==============================================================================

-- Query 2.1: Executive summary of orders and revenue metrics
-- Concept: Basic aggregate functions
SELECT 
    COUNT(DISTINCT order_id) AS Total_Orders,
    SUM(quantity) AS Total_Units_Sold,
    ROUND(SUM(sales_amount), 2) AS Gross_Revenue,
    ROUND(SUM(profit), 2) AS Net_Profit,
    ROUND(AVG(sales_amount), 2) AS Avg_Item_Revenue,
    ROUND(AVG(profit / NULLIF(sales_amount, 0)) * 100, 2) AS Avg_Profit_Margin_Pct
FROM order_items;

-- Query 2.2: Revenue, profit, and order count by product category
-- Concept: GROUP BY, ORDER BY aggregate
SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) AS Distinct_Orders,
    SUM(oi.quantity) AS Units_Sold,
    ROUND(SUM(oi.sales_amount), 2) AS Total_Revenue,
    ROUND(SUM(oi.profit), 2) AS Total_Profit,
    ROUND((SUM(oi.profit) / SUM(oi.sales_amount)) * 100, 2) AS Profit_Margin_Pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY Total_Revenue DESC;

-- Query 2.3: Identify top cities generating over $25,000 in revenue
-- Concept: HAVING clause to filter aggregated results (WHERE cannot filter SUM)
SELECT 
    c.city,
    c.country,
    c.region,
    COUNT(DISTINCT o.order_id) AS Orders_Count,
    ROUND(SUM(oi.sales_amount), 2) AS Total_Sales,
    ROUND(SUM(oi.profit), 2) AS Total_Profit
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY c.city, c.country, c.region
HAVING SUM(oi.sales_amount) > 25000.00
ORDER BY Total_Sales DESC;


-- ==============================================================================
-- LEVEL 3: RELATIONAL JOINS & MULTI-TABLE DATA ANALYSIS
-- ==============================================================================

-- Query 3.1: Detailed Customer Order Ledger (Joining all 4 normalized tables)
-- Concept: Multi-table INNER JOIN connecting Customers -> Orders -> Order_Items -> Products
SELECT 
    o.order_id,
    o.order_date,
    c.customer_name,
    c.segment AS Customer_Segment,
    c.country,
    p.product_name,
    p.category,
    oi.quantity,
    oi.unit_price,
    oi.discount_rate,
    oi.sales_amount,
    oi.profit
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed'
ORDER BY o.order_date DESC
LIMIT 10;

-- Query 3.2: Customer Inactivity / Acquisition Audit using LEFT JOIN
-- Concept: LEFT JOIN with IS NULL to identify customers who registered but never placed an order
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    c.signup_date,
    c.segment,
    COUNT(o.order_id) AS Total_Orders_Placed
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.email, c.signup_date, c.segment
HAVING COUNT(o.order_id) = 0;

-- Query 3.3: Product performance by customer market segment
-- Concept: Cross-dimensional matrix breakdown using JOINs
SELECT 
    p.category,
    c.segment AS Customer_Segment,
    COUNT(oi.order_item_id) AS Line_Items_Sold,
    ROUND(SUM(oi.sales_amount), 2) AS Segment_Revenue,
    ROUND(SUM(oi.profit), 2) AS Segment_Profit
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'Completed'
GROUP BY p.category, c.segment
ORDER BY p.category, Segment_Revenue DESC;


-- ==============================================================================
-- LEVEL 4: SUBQUERIES & COMMON TABLE EXPRESSIONS (CTEs)
-- ==============================================================================

-- Query 4.1: Scalar Subquery - Find products priced strictly above the catalog average
-- Concept: Scalar subquery in WHERE clause
SELECT 
    product_id,
    product_name,
    category,
    unit_price,
    ROUND((SELECT AVG(unit_price) FROM products), 2) AS Catalog_Avg_Price,
    ROUND(unit_price - (SELECT AVG(unit_price) FROM products), 2) AS Price_Diff_From_Avg
FROM products
WHERE unit_price > (SELECT AVG(unit_price) FROM products)
ORDER BY unit_price DESC;

-- Query 4.2: Correlated Subquery - Find orders that exceed that customer's own average order spend
-- Concept: Correlated subquery referencing the outer query's customer_id
SELECT 
    o.order_id,
    o.customer_id,
    c.customer_name,
    o.order_date,
    ROUND(SUM(oi.sales_amount), 2) AS Order_Total,
    ROUND((
        SELECT AVG(cust_orders.total_sales)
        FROM (
            SELECT o2.order_id, o2.customer_id, SUM(oi2.sales_amount) AS total_sales
            FROM orders o2
            JOIN order_items oi2 ON o2.order_id = oi2.order_id
            WHERE o2.order_status = 'Completed'
            GROUP BY o2.order_id, o2.customer_id
        ) cust_orders
        WHERE cust_orders.customer_id = o.customer_id
    ), 2) AS Customer_Avg_Order_Value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY o.order_id, o.customer_id, c.customer_name, o.order_date
HAVING SUM(oi.sales_amount) > Customer_Avg_Order_Value
ORDER BY Order_Total DESC
LIMIT 15;

-- Query 4.3: Multi-Stage CTE (WITH Clause) - High-Value Customer Profiling
-- Concept: Readable, modular Common Table Expressions for analytical pipelines
WITH Customer_Spend AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.segment,
        c.region,
        COUNT(DISTINCT o.order_id) AS Order_Count,
        ROUND(SUM(oi.sales_amount), 2) AS Lifetime_Spend,
        ROUND(SUM(oi.profit), 2) AS Lifetime_Profit
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, c.customer_name, c.segment, c.region
),
Spend_Thresholds AS (
    SELECT 
        AVG(Lifetime_Spend) AS Avg_Spend,
        AVG(Lifetime_Profit) AS Avg_Profit
    FROM Customer_Spend
)
SELECT 
    cs.customer_name,
    cs.segment,
    cs.region,
    cs.Order_Count,
    cs.Lifetime_Spend,
    cs.Lifetime_Profit,
    CASE 
        WHEN cs.Lifetime_Spend >= (st.Avg_Spend * 1.5) AND cs.Lifetime_Profit >= (st.Avg_Profit * 1.5) THEN 'Platinum VIP'
        WHEN cs.Lifetime_Spend >= st.Avg_Spend THEN 'Gold Core'
        ELSE 'Silver Standard'
    END AS Customer_Tier
FROM Customer_Spend cs
CROSS JOIN Spend_Thresholds st
ORDER BY cs.Lifetime_Spend DESC;


-- ==============================================================================
-- LEVEL 5: WINDOW FUNCTIONS (ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, RUNNING TOTAL)
-- ==============================================================================

-- Query 5.1: Top 3 Best-Selling Products Per Category (DENSE_RANK)
-- Concept: PARTITION BY, ORDER BY inside DENSE_RANK()
WITH Category_Product_Sales AS (
    SELECT 
        p.category,
        p.product_id,
        p.product_name,
        ROUND(SUM(oi.sales_amount), 2) AS Product_Revenue,
        ROUND(SUM(oi.profit), 2) AS Product_Profit,
        DENSE_RANK() OVER (
            PARTITION BY p.category 
            ORDER BY SUM(oi.sales_amount) DESC
        ) AS Revenue_Rank_In_Cat
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT 
    category,
    Revenue_Rank_In_Cat,
    product_name,
    Product_Revenue,
    Product_Profit
FROM Category_Product_Sales
WHERE Revenue_Rank_In_Cat <= 3
ORDER BY category, Revenue_Rank_In_Cat;

-- Query 5.2: Month-over-Month (MoM) Revenue Growth % using LAG()
-- Concept: Window function LAG() to inspect previous period and compute growth
WITH Monthly_Sales AS (
    SELECT 
        SUBSTR(o.order_date, 1, 7) AS Order_Month,
        ROUND(SUM(oi.sales_amount), 2) AS Current_Month_Revenue,
        COUNT(DISTINCT o.order_id) AS Monthly_Orders
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY SUBSTR(o.order_date, 1, 7)
)
SELECT 
    Order_Month,
    Monthly_Orders,
    Current_Month_Revenue,
    LAG(Current_Month_Revenue, 1) OVER (ORDER BY Order_Month) AS Prev_Month_Revenue,
    ROUND(
        (Current_Month_Revenue - LAG(Current_Month_Revenue, 1) OVER (ORDER BY Order_Month)) /
        NULLIF(LAG(Current_Month_Revenue, 1) OVER (ORDER BY Order_Month), 0) * 100, 
        2
    ) AS MoM_Growth_Pct
FROM Monthly_Sales
ORDER BY Order_Month;

-- Query 5.3: Cumulative Running Total and Moving Average of Daily Revenue
-- Concept: Running total with SUM() OVER (ORDER BY ... ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
WITH Daily_Revenue AS (
    SELECT 
        o.order_date,
        ROUND(SUM(oi.sales_amount), 2) AS Daily_Sales
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY o.order_date
)
SELECT 
    order_date,
    Daily_Sales,
    ROUND(SUM(Daily_Sales) OVER (
        ORDER BY order_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS Cumulative_Running_Total,
    ROUND(AVG(Daily_Sales) OVER (
        ORDER BY order_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS Rolling_7Day_Avg_Sales
FROM Daily_Revenue
ORDER BY order_date
LIMIT 20;


-- ==============================================================================
-- LEVEL 6: STRATEGIC BUSINESS INTELLIGENCE CASE STUDIES
-- ==============================================================================

-- Query 6.1: RFM (Recency, Frequency, Monetary) Customer Segmentation
-- Concept: NTILE() window function to generate automated 1-4 customer scores
WITH Customer_RFM_Raw AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.segment,
        -- Recency: Days since last completed purchase (as of 2025-11-01)
        JULIANDAY('2025-11-01') - JULIANDAY(MAX(o.order_date)) AS Recency_Days,
        -- Frequency: Count of distinct completed orders
        COUNT(DISTINCT o.order_id) AS Frequency,
        -- Monetary: Total revenue spend
        ROUND(SUM(oi.sales_amount), 2) AS Monetary
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, c.customer_name, c.segment
),
RFM_Scores AS (
    SELECT 
        customer_id,
        customer_name,
        segment,
        ROUND(Recency_Days, 0) AS Recency_Days,
        Frequency,
        Monetary,
        NTILE(4) OVER (ORDER BY Recency_Days DESC) AS R_Score, -- 4 is most recent
        NTILE(4) OVER (ORDER BY Frequency ASC) AS F_Score,     -- 4 is most frequent
        NTILE(4) OVER (ORDER BY Monetary ASC) AS M_Score       -- 4 is highest spend
    FROM Customer_RFM_Raw
)
SELECT 
    customer_id,
    customer_name,
    segment,
    Recency_Days,
    Frequency,
    Monetary,
    (R_Score + F_Score + M_Score) AS Total_RFM_Score,
    CASE 
        WHEN (R_Score >= 3 AND F_Score >= 3 AND M_Score >= 3) THEN 'Champion / Power Customer'
        WHEN (R_Score >= 3 AND M_Score >= 2) THEN 'Loyal Potential'
        WHEN (R_Score <= 2 AND M_Score >= 3) THEN 'At Risk / Churn Alert'
        ELSE 'Casual / Infrequent Buyer'
    END AS RFM_Segment
FROM RFM_Scores
ORDER BY Total_RFM_Score DESC, Monetary DESC;

-- Query 6.2: Discount Sensitivity & Margin Erosion Analysis
-- Concept: Evaluating how promotional discounts impact profitability
SELECT 
    CASE 
        WHEN discount_rate = 0.00 THEN '0% No Discount'
        WHEN discount_rate <= 0.10 THEN '1% - 10% Low Discount'
        WHEN discount_rate <= 0.20 THEN '11% - 20% Moderate Discount'
        ELSE '> 20% Steep Clearance'
    END AS Discount_Band,
    COUNT(order_item_id) AS Transaction_Count,
    SUM(quantity) AS Units_Sold,
    ROUND(SUM(sales_amount), 2) AS Total_Sales,
    ROUND(SUM(profit), 2) AS Total_Profit,
    ROUND((SUM(profit) / SUM(sales_amount)) * 100, 2) AS Realized_Profit_Margin_Pct
FROM order_items
GROUP BY Discount_Band
ORDER BY Realized_Profit_Margin_Pct DESC;

