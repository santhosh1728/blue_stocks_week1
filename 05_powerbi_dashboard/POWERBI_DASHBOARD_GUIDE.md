# Power BI Dashboard Master Blueprint: Enterprise Retail Analytics

Welcome to the **Power BI Data Analyst Blueprint**. This guide accompanies the DAX measure library [`powerbi_measures.dax`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/05_powerbi_dashboard/powerbi_measures.dax), the star schema specification [`data_model_schema.json`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/05_powerbi_dashboard/data_model_schema.json), and the interactive dashboard visualizer [`dashboard_preview.html`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/05_powerbi_dashboard/dashboard_preview.html).

---

## Table of Contents
1. [Dimensional Modeling: The Star Schema](#1-dimensional-modeling-the-star-schema)
2. [Power Query & ETL Data Ingestion](#2-power-query--etl-data-ingestion)
3. [The DAX Engine: Row Context vs Filter Context](#3-the-dax-engine-row-context-vs-filter-context)
4. [Master DAX Measures Catalog](#4-master-dax-measures-catalog)
5. [Dashboard Architecture & Visual Layout](#5-dashboard-architecture--visual-layout)
6. [Interactive Features: Slicers, Drill-Through, & Bookmarks](#6-interactive-features)
7. [Step-by-Step Build Instructions for Power BI Desktop](#7-step-by-step-build-instructions)

---

## 1. Dimensional Modeling: The Star Schema

In production Business Intelligence, flat tables ("one big sheet") cause slow queries, difficult DAX calculations, and high RAM consumption. We implement a **Star Schema**:

```
                       +-------------------+
                       |    Dim_Date       |
                       +-------------------+
                       | Date (PK)         |
                       | Year, Month, etc. |
                       +---------+---------+
                                 | 1
                                 |
                                 | *
+-------------------+  * +-------+---------+ *  +-------------------+
|   Dim_Customers   +----+   Fact_Sales    +----+   Dim_Products    |
+-------------------+    +-----------------+    +-------------------+
| customer_id (PK)  |    | order_item_id   |    | product_id (PK)   |
| customer_name     |    | order_date (FK) |    | product_name      |
| segment, country  |    | customer_id(FK) |    | category, cost    |
+-------------------+    | product_id (FK) |    +-------------------+
                         | quantity, sales |
                         | profit, status  |
                         +-----------------+
```

### Cardinality & Cross-Filter Direction
- All relationships are **One-to-Many (`1:*`)** from Dimensions to the Fact table.
- **Cross-Filter Direction:** Always set to **Single** (Dimension filters Fact). Avoid bidirectional filtering unless required for specific many-to-many bridge tables to prevent circular calculation paths.

---

## 2. Power Query & ETL Data Ingestion

In Power BI Desktop, open **Transform Data (Power Query)**:

### 2.1 Generating a Dynamic Dim_Date Table (M Code)
Paste this into the Advanced Editor to generate a complete Calendar dimension:
```powerquery
let
    StartDate = #date(2024, 1, 1),
    EndDate = #date(2025, 12, 31),
    DayCount = Duration.Days(Duration.From(EndDate - StartDate)) + 1,
    Source = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    #"Converted to Table" = Table.FromList(Source, Splitter.SplitByNothing(), {"Date"}, null, ExtraValues.Error),
    #"Changed Type" = Table.TransformColumnTypes(#"Converted to Table",{{"Date", type date}}),
    #"Added Year" = Table.AddColumn(#"Changed Type", "Year", each Date.Year([Date]), Int64.Type),
    #"Added Month" = Table.AddColumn(#"Added Year", "MonthNumber", each Date.Month([Date]), Int64.Type),
    #"Added Month Name" = Table.AddColumn(#"Added Month", "MonthName", each Date.MonthName([Date]), type text),
    #"Added Quarter" = Table.AddColumn(#"Added Month Name", "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    #"Added Month-Year" = Table.AddColumn(#"Added Quarter", "MonthYear", each Date.ToText([Date], "yyyy-MM"), type text)
in
    #"Added Month-Year"
```

> [!IMPORTANT]
> In Power BI, select `MonthName` column > go to **Column Tools > Sort by Column** > select `MonthNumber`. This ensures months sort chronologically (`Jan, Feb, Mar...`) rather than alphabetically!

---

## 3. The DAX Engine: Row Context vs Filter Context

Understanding the evaluation engine is the single most critical milestone in mastering Power BI:

### Row Context
- Exists during row-by-row iteration (e.g., in a Calculated Column or inside iterator functions like `SUMX`, `AVERAGEX`).
- Knows only the current row's values. It does **not** know what visual filters are applied on the dashboard.

### Filter Context
- The active set of filters applied by dashboard slicers, visual axes, matrix headers, and page filters.
- If the user clicks "Europe" on a slicer, the Filter Context for `[Total Sales]` restricts calculation to European rows.

### Context Transition via `CALCULATE()`
`CALCULATE()` is the only function in DAX that can **modify** the Filter Context:
$$\text{CALCULATE}(\langle\text{Expression}\rangle,\ \langle\text{Filter}_1\rangle,\ \langle\text{Filter}_2\rangle,\ \dots)$$
When called inside a row context, `CALCULATE()` transforms the current row into an equivalent filter context.

---

## 4. Master DAX Measures Catalog

Here are the primary measures from [`powerbi_measures.dax`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/05_powerbi_dashboard/powerbi_measures.dax):

### 4.1 Base Financial Measures
```dax
Total Sales = SUM(Fact_Sales[Sales_Amount])

Total Cost = SUMX(Fact_Sales, Fact_Sales[Quantity] * RELATED(Dim_Products[Cost_Price]))

Total Profit = [Total Sales] - [Total Cost]

Profit Margin Pct = DIVIDE([Total Profit], [Total Sales], 0.0)

Average Order Value = DIVIDE([Total Sales], DISTINCTCOUNT(Fact_Sales[Order_ID]), 0.0)
```

### 4.2 Time Intelligence (YoY & MoM Growth)
```dax
Sales Prior Year = 
CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Dim_Date[Date]))

Sales YoY Growth Pct = 
DIVIDE([Total Sales] - [Sales Prior Year], [Sales Prior Year], BLANK())

Sales YTD = 
TOTALYTD([Total Sales], Dim_Date[Date])
```

---

## 5. Dashboard Architecture & Visual Layout

The dashboard follows a 3-tier visual hierarchy:

```
+-------------------------------------------------------------------------------+
| TOP BAR: Slicers (Date Range Slider | Region Dropdown | Category Buttons)     |
+-------------------------------------------------------------------------------+
| KPI BANNER:                                                                   |
| [ Revenue: $1.76M ]  [ Profit: $537K ]  [ Margin: 30.5% ]  [ Orders: 1,209 ]  |
+-----------------------------------------------+-------------------------------+
| VISUAL 1 (Area/Line):                         | VISUAL 2 (Donut Chart):       |
| Monthly Revenue & Profit 22-Month Trend       | Revenue by Customer Segment   |
+-----------------------------------------------+-------------------------------+
| VISUAL 3 (Clustered Bar Chart):               | VISUAL 4 (Bar Chart):         |
| Sales vs Profit by Product Category           | Regional Performance Breakdown|
+-----------------------------------------------+-------------------------------+
| VISUAL 5 (Drill-through Table):                                               |
| Transaction-Level Order Detail Matrix with Status Badges                      |
+-------------------------------------------------------------------------------+
```

---

## 6. Interactive Features

### 6.1 Drill-Through Pages
Create a dedicated sub-page titled `Customer Detail`:
1. Drag `Dim_Customers[customer_name]` into the **Drill-through fields** well.
2. When right-clicking any customer on the main dashboard, users can drill directly into their order history, RFM tier, and purchased products.

### 6.2 Bookmark Navigation
Create button toggles for:
- **View by Revenue ($)** vs **View by Units Sold (Qty)**
- Accomplished using Power BI **Bookmarks** and the **Selection Pane** to toggle visual visibility.

---

## 7. Step-by-Step Build Instructions

1. **Import Data:** In Power BI Desktop, click **Get Data > Text/CSV** and select `data/cleaned_sales_data.csv`, `data/customers.csv`, and `data/products.csv`.
2. **Setup Relationships:** In the **Model View**, link:
   - `Dim_Customers[customer_id]` $\rightarrow$ `Fact_Sales[customer_id]`
   - `Dim_Products[product_id]` $\rightarrow$ `Fact_Sales[product_id]`
   - `Dim_Date[Date]` $\rightarrow$ `Fact_Sales[order_date]`
3. **Create Measures Table:** Create a blank table called `_Key_Measures` and paste all measures from `powerbi_measures.dax`.
4. **Build Visuals:** Follow the wireframe above.
5. **Interactive Preview:** Open [`dashboard_preview.html`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/05_powerbi_dashboard/dashboard_preview.html) in your browser to test the interactive slicers, charts, and live tabular drill-down!

