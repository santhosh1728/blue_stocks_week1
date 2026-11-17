# Comprehensive Guide: Excel & Google Sheets for Data Analysts

Welcome to the **Excel / Google Sheets Data Analyst Master Guide**. This guide accompanies the workbook [`sales_dashboard.xlsx`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/01_excel_dashboard/sales_dashboard.xlsx) and breaks down every core concept required for professional business reporting and data manipulation.

---

## Table of Contents
1. [Data Cleaning in Spreadsheets](#1-data-cleaning-in-spreadsheets)
2. [Sorting & Advanced Filtering](#2-sorting--advanced-filtering)
3. [Conditional Formatting Best Practices](#3-conditional-formatting-best-practices)
4. [Mastering Pivot Tables & Calculated Fields](#4-mastering-pivot-tables--calculated-fields)
5. [Lookup Functions (XLOOKUP, INDEX, MATCH, VLOOKUP)](#5-lookup-functions-xlookup-index-match-vlookup)
6. [Business Charting & Visual Hierarchy](#6-business-charting--visual-hierarchy)
7. [Dashboard Architecture & Layout](#7-dashboard-architecture--layout)
8. [Practical Hands-on Exercises](#8-practical-hands-on-exercises)

---

## 1. Data Cleaning in Spreadsheets

Before any analysis or dashboarding, raw data must be audited and standardized. In our sample dataset (`data/raw_sales_data.csv`), common real-world errors were intentionally introduced. Here is how to fix them in Excel or Google Sheets:

### 1.1 Removing Leading & Trailing Whitespace
Whitespace causes lookup failures and broken aggregations (e.g., `"Technology "` vs `"Technology"`).
```excel
=TRIM(A2)
```
- **Function:** `TRIM(text)` removes all leading, trailing, and repeated interior spaces.
- **Google Sheets:** You can also use **Data > Data cleanup > Trim whitespace**.

### 1.2 Fixing Text Casing
Standardize text capitalization to avoid fragmented groupings in pivot tables.
```excel
=PROPER(B2)   -- Capitalizes first letter of each word (e.g., "John Doe")
=UPPER(C2)    -- All capital letters (e.g., "USA", "ORD-101")
=LOWER(D2)    -- All lowercase (e.g., email addresses)
```

### 1.3 Deduplication
Duplicates artificially inflate revenue and customer counts.
- **Excel Method:** Select table > Go to **Data tab > Remove Duplicates** > Check `Order_ID`.
- **Formula Method:**
  ```excel
  =COUNTIF($A$2:$A$1200, A2)
  ```
  Filter rows where count > 1.
- **Google Sheets:** `=UNIQUE(A2:Y1200)`.

### 1.4 Handling Missing / Null Values
- **Identify Nulls:** Press `Ctrl + G` > **Special... > Blanks** to highlight all empty cells.
- **Imputation Formula:**
  ```excel
  =IF(ISBLANK(G2), "Unknown@customer.com", G2)
  -- Or using modern IFNA / IFERROR:
  =IFNA(XLOOKUP(...), "N/A")
  ```

### 1.5 Text to Columns & Delimited Parsing
Splitting combined fields (e.g., splitting `"New York, NY"` into City and State):
- Select column > **Data > Text to Columns** > Choose **Delimited** > Select **Comma**.
- Formula alternative:
  ```excel
  -- Extract text before comma:
  =TEXTBEFORE(A2, ",")
  -- Extract text after comma:
  =TEXTAFTER(A2, ", ")
  ```

---

## 2. Sorting & Advanced Filtering

### 2.1 Multi-Level Sorting
Business queries often require nested sorting (e.g., Sort by **Region (Ascending)**, then by **Sales Amount (Descending)** to see top transactions per territory).
1. Select the data range.
2. Go to **Data > Sort**.
3. Add **Level 1**: Column `Region`, Order `A to Z`.
4. Click **Add Level**, Column `Sales_Amount`, Order `Largest to Smallest`.

### 2.2 Slicers and Dynamic Filters
Convert the data into an official Excel Table (`Ctrl + T` in Windows, `Cmd + T` in Mac):
- Gives named range capability (e.g., `SalesTable[Sales_Amount]`).
- Auto-expands when new rows are added.
- Enables **Slicers**: Visual click-buttons for interactive filtering by `Region`, `Category`, or `Order_Status`.

---

## 3. Conditional Formatting Best Practices

Conditional formatting turns raw tabular data into intuitive heatmaps and alert systems.

### 3.1 Rules Applied in this Project:
1. **Highlight Negative Profits (Loss Alerts):**
   - Range: `Cleaned_Sales_Data!V2:V1201` (Profit column)
   - Rule Type: **Format cells that contain** < 0
   - Format: Light Red Fill (`#FEE2E2`) with Dark Red Text (`#991B1B`).
2. **Profit Margin Data Bars:**
   - Range: `Cleaned_Sales_Data!W2:W1201`
   - Rule Type: **Data Bars > Gradient Fill (Emerald Green)**
   - Visualizes relative profitability instantly without reading exact decimals.
3. **Top 10% Revenue Transactions:**
   - Range: `Cleaned_Sales_Data!U2:U1201`
   - Rule Type: **Top/Bottom Rules > Top 10%**
   - Format: Soft Gold/Yellow Fill (`#FEF3C7`).

---

## 4. Mastering Pivot Tables & Calculated Fields

Pivot tables aggregate thousands of transaction rows in seconds without writing code.

### 4.1 Structure of a Pivot Table
| Quadrant | Purpose | Example from our Dataset |
| :--- | :--- | :--- |
| **Filters** | High-level dashboard slice | `Order_Status` (e.g., show only Completed) |
| **Columns** | Horizontal grouping dimension | `Category` (Technology, Furniture, etc.) |
| **Rows** | Vertical grouping dimension | `Region` or `Customer_Segment` |
| **Values** | Numeric summary metric | `SUM(Sales_Amount)`, `AVERAGE(Profit_Margin)` |

### 4.2 Adding a Calculated Field
To compute **Gross Profit Margin %** inside a Pivot Table:
1. Click inside the Pivot Table.
2. Go to **PivotTable Analyze > Fields, Items & Sets > Calculated Field**.
3. Name: `Calculated_Margin_Pct`.
4. Formula: `= Profit / Sales_Amount`.
5. Format the field as **Percentage (`0.0%`)**.

### 4.3 Grouping Dates (Year, Quarter, Month)
When `Order_Date` is dragged to the Rows area:
1. Right-click any date cell in the Pivot Table.
2. Select **Group...**
3. Highlight **Years**, **Quarters**, and **Months**.
4. Excel automatically creates time hierarchies for trend analysis.

---

## 5. Lookup Functions (XLOOKUP, INDEX, MATCH, VLOOKUP)

Lookups connect disparate tables and allow dynamic user lookups.

### 5.1 The Modern Standard: `XLOOKUP`
Introduced in Excel 2021 & Microsoft 365, replacing `VLOOKUP` and `HLOOKUP`.
```excel
=XLOOKUP(lookup_value, lookup_array, return_array, [if_not_found], [match_mode], [search_mode])
```
**Live Example from Workbook (`Executive_Dashboard!B17`):**
```excel
=XLOOKUP(B15, Cleaned_Sales_Data!A:A, Cleaned_Sales_Data!F:F, "Not Found")
```
- Searches for `Order_ID` in column `A` and retrieves `Customer_Name` in column `F`.
- If the Order ID doesn't exist, it displays `"Not Found"` without producing an `#N/A` error.

### 5.2 The Universal Powerhouse: `INDEX` + `MATCH`
Works across **every** version of Excel and Google Sheets. Does not break when columns are rearranged.
```excel
=INDEX(return_range, MATCH(lookup_value, lookup_range, 0))
```
**Mechanism:**
1. `MATCH("ORD-2024-1005", Cleaned_Sales_Data!A:A, 0)` scans column A and returns the row number (e.g., row 5).
2. `INDEX(Cleaned_Sales_Data!N:N, 5)` returns the value at row 5 in column N (`Product_Name`).

### 5.3 Feature Comparison Table
| Feature | `XLOOKUP` | `INDEX` + `MATCH` | `VLOOKUP` |
| :--- | :--- | :--- | :--- |
| **Leftward Lookup** | Yes (Native) | Yes (Native) | No (Only searches to right) |
| **Default Match Mode** | Exact Match (`0`) | Requires `0` argument | Approximate (defaults to `TRUE`) |
| **Column Insertion Resilience** | Immune | Immune | Breaks if columns inserted |
| **Built-in Error Handling** | Yes (`[if_not_found]`) | Requires wrapping in `IFNA()` | Requires wrapping in `IFNA()` |
| **Compatibility** | Excel 365 / 2021+ | Universal (All Excel / Sheets) | Universal |

---

## 6. Business Charting & Visual Hierarchy

Data dashboards must communicate insights within 5 seconds.

### 6.1 Selecting the Right Chart Type
- **Monthly Revenue Over Time:** Line Chart with smoothed markers or Area Chart.
- **Category Sales Comparison:** Horizontal Bar Chart (easiest for reading labels).
- **Region vs Segment:** Clustered Column Chart or 100% Stacked Bar Chart.
- **Profit vs Discount Correlation:** Scatter Plot ($X$: Discount %, $Y$: Profit $).

### 6.2 Chart Decluttering Rules (Edward Tufte Principles)
1. **Remove redundant gridlines:** Keep only subtle horizontal gridlines or none at all.
2. **Direct Data Labels:** For bar charts with < 6 categories, remove the vertical axis and put data labels directly above/beside bars.
3. **Format Currency Correctly:** Use `$1.14M` or `$584K` instead of `$584,200.00` in chart callouts.
4. **Intentional Color Palette:**
   - Primary KPI / Revenue: Slate Blue (`#2563EB`)
   - Profits: Emerald Green (`#059669`)
   - Alert / Deficit: Crimson Red (`#DC2626`)
   - Neutral Cards: Light Slate (`#F8FAFC`)

---

## 7. Dashboard Architecture & Layout

The workbook [`sales_dashboard.xlsx`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/01_excel_dashboard/sales_dashboard.xlsx) follows the **Z-Pattern Layout**:

```
+-------------------------------------------------------------------------+
|                  APEX RETAIL SOLUTIONS - EXECUTIVE DASHBOARD             |
+-------------------------------------------------------------------------+
| [ Total Revenue ]  [ Total Profit ]  [ Orders ]  [ Margin % ]  [  AOV  ] |
|   $1,142,580.00      $386,420.00       1,200        33.8%       $952.15 |
+-------------------------------------+-----------------------------------+
|     Category Performance Summary    |      Regional Sales Summary       |
|  Technology:     $584,200 (35.4%)   |  North America: $620,400          |
|  Furniture:      $348,100 (38.1%)   |  Europe:        $325,100          |
|  Smart Gadgets:  $156,300 (32.2%)   |  APAC:          $154,200          |
|  Office Supp.:   $ 53,980 (24.5%)   |  LATAM:         $ 42,880          |
+-------------------------------------+-----------------------------------+
|             Interactive Order Lookup Tool (XLOOKUP & INDEX/MATCH)        |
|  Order ID: [ ORD-2024-1005 ]        |  Customer: Sophia Rodriguez       |
|  Product:  iPhone 15 Pro            |  Sales:    $2,198.00  (Completed) |
+-------------------------------------------------------------------------+
```

---

## 8. Practical Hands-on Exercises

1. **Exercise 1 (Formula Lookup):** In `Executive_Dashboard`, change cell `B15` from `ORD-2024-1005` to `ORD-2024-1010` and observe how the XLOOKUP and INDEX/MATCH formulas instantly re-evaluate.
2. **Exercise 2 (Slicers):** In `Cleaned_Sales_Data`, select the table, insert a Slicer for `Region`, and filter for `Europe`.
3. **Exercise 3 (Conditional Alert):** Create a rule that highlights any order where `Discount_Rate >= 0.20` in amber to audit heavy promotional discounting.

