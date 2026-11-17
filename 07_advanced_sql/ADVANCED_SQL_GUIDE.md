# Advanced SQL & Query Optimization Guide (Week 2)

Welcome to the **Advanced SQL Data Analyst Guide**. This guide covers high-level analytical patterns used in product, growth, and business intelligence teams:
1. **Cohort Retention Analysis**: Constructing cohort heatmaps from scratch.
2. **Recursive Common Table Expressions (CTEs)**: Date spine generation and hierarchy traversals.
3. **Advanced Join Optimization**: Semi-Joins (`EXISTS`), Anti-Joins (`NOT EXISTS`), and short-circuit evaluation.
4. **Database Performance Tuning**: `EXPLAIN QUERY PLAN`, B-Tree indexes, covering indexes, and sargable predicates.

---

## 1. Cohort Retention Analysis

Cohort analysis groups users based on a shared characteristic—typically their **Acquisition Date**—and measures their retention over time ($M_0, M_1, M_2, \dots, M_{12}$).

### 1.1 The 4-Step Analytical Pattern
1. **Step 1 (Cohort Definition):** Find the minimum `order_date` for each customer:
   ```sql
   MIN(SUBSTR(order_date, 1, 7)) AS Cohort_Month
   ```
2. **Step 2 (Activity Logging):** Extract every unique subsequent order month and compute the `Month_Index`:
   $$\text{Month\_Index} = (\text{Year}_{\text{order}} - \text{Year}_{\text{cohort}}) \times 12 + (\text{Month}_{\text{order}} - \text{Month}_{\text{cohort}})$$
3. **Step 3 (Baseline Denominator):** Count the total unique customers in Month 0 ($M_0$).
4. **Step 4 (Pivot & Percentage):** Divide active customers in $M_k$ by initial users in $M_0$:
   $$\text{Retention Rate } M_k = \frac{\text{Active Customers in } M_k}{\text{Initial Users in } M_0} \times 100\%$$

---

## 2. Recursive CTEs

A recursive CTE references itself repeatedly until a termination condition is reached.

### Structure of a Recursive CTE
```sql
WITH RECURSIVE Cte_Name AS (
    -- 1. Anchor Member (Initial row / base case)
    SELECT ...
    UNION ALL
    -- 2. Recursive Member (Calculates next row referencing Cte_Name)
    SELECT ... FROM Cte_Name WHERE <termination_condition>
)
SELECT * FROM Cte_Name;
```

### Date Spine Pattern for Missing Gaps
In retail sales, some days have zero transactions (e.g., holidays, system downtime). A standard `GROUP BY order_date` will completely skip those days, creating invisible gaps in time-series charts.
Using a recursive CTE date spine, we generate all consecutive calendar days and `LEFT JOIN` the sales table to ensure every single day appears with `$0.00` sales.

---

## 3. Semi-Joins vs Anti-Joins

| Join Pattern | SQL Syntax | Best Use Case | Performance Characteristic |
| :--- | :--- | :--- | :--- |
| **Semi-Join** | `WHERE EXISTS (SELECT 1 ...)` | Find customers who bought a specific item | Halts on first match (Fast) |
| **Anti-Join** | `WHERE NOT EXISTS (SELECT 1 ...)` | Find churned or inactive users | Clean handling of `NULL`s |
| **Traditional Join** | `JOIN ... GROUP BY` | Aggregating order quantities | Creates large intermediary Cartesian products |

---

## 4. Query Performance Tuning & `EXPLAIN QUERY PLAN`

When queries slow down on tables with millions of rows, data analysts must inspect the execution plan:

```sql
EXPLAIN QUERY PLAN
SELECT o.order_id, c.customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2025-01-01';
```

### Key Execution Terms
- **`SCAN TABLE`:** The engine checks every single row sequentially (Slow, $O(n)$).
- **`SEARCH TABLE USING INDEX`:** The engine traverses a binary B-Tree index (Extremely fast, $O(\log n)$).
- **`COVERING INDEX`:** An index that contains all columns requested by the `SELECT` query, allowing the engine to fulfill the request directly from the index without reading the physical table blocks.

