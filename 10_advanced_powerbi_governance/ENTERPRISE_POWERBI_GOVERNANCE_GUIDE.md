# Enterprise Power BI Governance, Calculation Groups & RLS (Week 2)

Welcome to the **Enterprise Power BI Governance Master Guide**. In large-scale enterprises, analytics teams encounter two massive operational bottlenecks:
1. **Measure Explosion:** Multiplying 15 base KPIs by 6 time-intelligence variants yields 90 redundant DAX measures.
2. **Data Security & Privacy:** Regional managers must only see their assigned territory without creating separate duplicate `.pbix` reports.

This guide provides architectural solutions using **Calculation Groups**, **Dynamic Row-Level Security (RLS)**, and **VertiPaq Engine Optimization**.

---

## Table of Contents
1. [Eliminating Measure Explosion with Calculation Groups](#1-calculation-groups)
2. [Dynamic Row-Level Security (RLS)](#2-dynamic-rls)
3. [Field Parameters for Dynamic Slicing](#3-field-parameters)
4. [The VertiPaq Engine & Memory Optimization](#4-vertipaq-engine-optimization)
5. [DAX Performance Profiling with Performance Analyzer](#5-dax-performance-profiling)

---

## 1. Eliminating Measure Explosion with Calculation Groups

### The Problem
If your model contains `[Total Sales]`, `[Total Profit]`, `[Total Orders]`, `[Units Sold]`, and `[COGS]`, calculating **YTD**, **Prior Year**, and **YoY Growth %** for each requires creating:
$$5 \text{ measures} \times 4 \text{ variations} = 20 \text{ measures}$$
In enterprise models with 50 base metrics, this leads to **200+ redundant DAX measures**.

### The Solution: Calculation Groups
Created via **Tabular Editor** or Power BI Desktop modeling view. A Calculation Group defines a single transformation engine (`SELECTEDMEASURE()`) that can be applied dynamically to *any* visual or metric:

```
                                  CALCULATION GROUP: 'Time Calculations'
                                  
                            ┌───────────────────────────────────────────────┐
                            │               SELECTEDMEASURE()               │
                            └───────┬───────────────┬───────────────┬───────┘
                                    │               │               │
                                    ▼               ▼               ▼
                              [ Current ]        [ YTD ]      [ YoY Growth % ]
                                   │                │               │
  Applied to [Total Sales]   ──> $1.76M          $1.76M          +14.2%
  Applied to [Total Profit]  ──> $537K           $537K           +18.5%
  Applied to [Total Orders]  ──> 1,209           1,209           +8.4%
```

---

## 2. Dynamic Row-Level Security (RLS)

Static RLS creates a hardcoded role for every country or region. **Dynamic RLS** uses the logged-in user's Azure Active Directory (Microsoft Entra) identity:

```dax
[Region] = 
LOOKUPVALUE(
    User_Territory_Security[Region],
    User_Territory_Security[User_Email],
    USERPRINCIPALNAME()
)
```

- When `emily.watson@enterprise.com` logs in, `USERPRINCIPALNAME()` returns her email.
- The `LOOKUPVALUE` retrieves `"North America"`.
- The filter context instantly restricts every visual on the dashboard to North American data, without requiring separate reports!

---

## 3. Field Parameters for Dynamic Slicing

Instead of cluttering executive dashboards with three separate charts (Sales by Category, Sales by Region, Sales by Segment), use **Field Parameters**:
- Allows end users to click a slicer: `[ Category | Region | Segment ]`.
- The single visual dynamically swaps its X-axis to the chosen dimension.

---

## 4. The VertiPaq Engine & Memory Optimization

Power BI's underlying storage engine (VertiPaq) is a **columnar, in-memory database**.

### Rules for High-Speed Models:
1. **Column Cardinality is King:** VertiPaq compresses columns using Dictionary Encoding. Columns with low unique counts (e.g., `Category` with 4 values) compress by $99\%$. Columns with high unique counts (e.g., high-precision timestamps like `2024-05-18 14:22:19.482`) destroy compression.
   - *Fix:* Always split datetime columns into separate `Date` and `Time` columns, or remove the time component entirely if not needed.
2. **Never Import Surrogate Keys You Don't Join On:** If a transaction table has an auto-increment integer ID that isn't used for relationships, delete it in Power Query.
3. **Prefer Star Schema over Snowflake:** Flat dimensions with fewer joins allow VertiPaq to scan columns in CPU cache registers without cross-table pointer dereferencing.

