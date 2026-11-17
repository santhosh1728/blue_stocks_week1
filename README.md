# Data Analyst Technical Foundations: Complete 2-Week Portfolio Suite
**Repository:** Apex Retail Solutions Analytics Suite  
**Author:** Data Analyst Technical Team  
**Tech Stack:** Microsoft Excel, SQL (SQLite / ANSI), Python (Pandas, NumPy, Matplotlib, SciPy, Scikit-Learn), Power BI (DAX, Star Schema, RLS, Calculation Groups), Statistics & A/B Testing

---

## Executive Overview

This repository constitutes a complete, production-grade portfolio project and learning curriculum designed to build both fundamental and advanced technical skills required for working as a professional **Data Analyst**.

- **Week 1:** [Foundational Technical Mastery](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/README.md) (Excel Dashboard, Core SQL & Window Functions, Python Wrangling, Data Cleaning & EDA Report, Power BI Star Schema, Core Statistics).
- **Week 2:** [Advanced Analytics & Predictive Modeling](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/WEEK_2_OVERVIEW.md) (Advanced SQL & Cohort Retention Matrices, A/B Testing & Product Experimentation, Predictive Churn Modeling with Machine Learning, Enterprise Power BI Calculation Groups & Dynamic RLS).

All 6 subject domains are built around a unified, realistic enterprise retail scenario (**Apex Retail Solutions**)—an omnichannel consumer electronics and office technology retailer operating across North America, Europe, APAC, and LATAM.

```
                                  APEX RETAIL ANALYTICS ARCHITECTURE
                                  
  [ Raw Data Ingestion ] ────────> [ Data Cleaning & EDA Pipeline ] ────────> [ Cleaned Master Dataset ]
  data/raw_sales_data.csv          04_data_cleaning_eda/clean_dataset.py        data/cleaned_sales_data.csv
                                                                                       │
                      ┌─────────────────────────────────┬──────────────────────────────┴──────────────────────────────┐
                      ▼                                 ▼                                                             ▼
             [ 01_excel_dashboard ]            [ 02_sql_practice ]                                           [ 03_python_analysis ]
           sales_dashboard.xlsx               retail_sales.db                                                python_data_analysis.ipynb
           • Formulas (XLOOKUP, INDEX/MATCH)  • 18 Practice Queries                                          • NumPy Vectorization
           • Pivot Tables & Summaries         • Joins, CTEs, Window Functions                                • Pandas Wrangling
           • Conditional Formatting           • RFM & MoM Growth Analysis                                    • 6 High-Res Visualizations
                      │                                 │                                                             │
                      └─────────────────────────────────┼─────────────────────────────────────────────────────────────┘
                                                        ▼
                                              [ 05_powerbi_dashboard ]
                                            dashboard_preview.html (Interactive)
                                            • Star Schema Dimensional Model
                                            • 30+ Production DAX Measures
                                            • Time Intelligence & Drillthrough
```

---

## Deliverables Summary Matrix

| Module | Core Deliverable File | Companion Guide & Code | Key Topics Covered |
| :--- | :--- | :--- | :--- |
| **1. Excel / Google Sheets** | [`sales_dashboard.xlsx`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/01_excel_dashboard/sales_dashboard.xlsx) | [`EXCEL_DASHBOARD_GUIDE.md`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/01_excel_dashboard/EXCEL_DASHBOARD_GUIDE.md) | XLOOKUP, INDEX/MATCH, Pivot Tables, Slicers, Conditional Formatting, KPI Cards |
| **2. SQL Analytics** | [`sql_practice_queries.sql`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/02_sql_practice/sql_practice_queries.sql) | [`SQL_PRACTICE_GUIDE.md`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/02_sql_practice/SQL_PRACTICE_GUIDE.md)<br>[`run_sql_exercises.py`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/02_sql_practice/run_sql_exercises.py) | Relational Joins, Aggregations, HAVING, CTEs, Window Functions (DENSE_RANK, LAG, Rolling Averages), RFM Segmentation |
| **3. Python Analysis** | [`python_data_analysis.ipynb`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/03_python_analysis/python_data_analysis.ipynb) | [`PYTHON_ANALYSIS_GUIDE.md`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/03_python_analysis/PYTHON_ANALYSIS_GUIDE.md)<br>[`analysis_script.py`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/03_python_analysis/analysis_script.py) | Python basics, NumPy arrays, Pandas DataFrames, KPI calculation, Matplotlib figures |
| **4. Data Cleaning & EDA** | [`cleaned_sales_data.csv`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/data/cleaned_sales_data.csv) | [`eda_report.md`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/04_data_cleaning_eda/eda_report.md)<br>[`clean_dataset.py`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/04_data_cleaning_eda/clean_dataset.py) | Deduplication, Imputation, Text cleaning, IQR Outlier Detection, Skewness, Correlation Matrix |
| **5. Power BI Dashboard** | [`dashboard_preview.html`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/05_powerbi_dashboard/dashboard_preview.html) | [`POWERBI_DASHBOARD_GUIDE.md`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/05_powerbi_dashboard/POWERBI_DASHBOARD_GUIDE.md)<br>[`powerbi_measures.dax`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/05_powerbi_dashboard/powerbi_measures.dax) | Star Schema, Power Query M code, 30+ DAX measures (YTD, YoY %, Rolling Avg), Interactive Web Preview |
| **6. Statistics Guide** | [`STATISTICS_FOR_DATA_ANALYSTS.md`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/06_statistics_guide/STATISTICS_FOR_DATA_ANALYSTS.md) | Practical Python & SQL statistical code examples | Mean/Median/Mode, Variance, Standard Deviation, Correlation vs Causation, CLT, Hypothesis Testing, OLS Regression |

---

## Directory Structure

```
blue_stocks/
├── README.md                                  <- Master portfolio documentation
├── create_datasets.py                         <- Synthetic master data generation engine
│
├── data/
│   ├── raw_sales_data.csv                     <- Raw uncleaned sales data (with real-world errors)
│   ├── cleaned_sales_data.csv                 <- Standardized, validated master dataset (1,209 rows)
│   ├── customers.csv                          <- Normalized customer dimension table
│   ├── products.csv                           <- Normalized product dimension table
│   ├── orders.csv                             <- Normalized orders header table
│   └── order_items.csv                        <- Normalized line item transactions table
│
├── 01_excel_dashboard/
│   ├── sales_dashboard.xlsx                   <- Native OpenXML multi-tab Excel workbook
│   ├── EXCEL_DASHBOARD_GUIDE.md               <- Comprehensive Excel & Sheets tutorial
│   └── build_excel_dashboard.py               <- Script compiling the .xlsx file
│
├── 02_sql_practice/
│   ├── retail_sales.db                        <- Populated SQLite database
│   ├── sql_practice_queries.sql               <- 18 organized queries from Level 1 to Level 6
│   ├── SQL_PRACTICE_GUIDE.md                  <- Theory, execution orders, and interview guide
│   └── run_sql_exercises.py                   <- Script executing all queries against database
│
├── 03_python_analysis/
│   ├── python_data_analysis.ipynb             <- Master Jupyter Notebook with code & outputs
│   ├── analysis_script.py                     <- Standalone script calculating KPIs and charts
│   ├── PYTHON_ANALYSIS_GUIDE.md               <- Python data science workflow reference
│   └── charts/                                <- Exported high-resolution 300 DPI visualizations
│       ├── monthly_revenue_trend.png
│       ├── category_sales_profit.png
│       ├── customer_segment_distribution.png
│       ├── profit_vs_discount_scatter.png
│       ├── regional_sales_breakdown.png
│       └── executive_kpi_dashboard.png
│
├── 04_data_cleaning_eda/
│   ├── eda_report.md                          <- Executive Exploratory Data Analysis Report
│   ├── clean_dataset.py                       <- 6-stage data cleaning & outlier removal pipeline
│   └── run_eda.py                             <- Statistical computations engine
│
├── 05_powerbi_dashboard/
│   ├── dashboard_preview.html                 <- Interactive web dashboard preview (Chart.js)
│   ├── POWERBI_DASHBOARD_GUIDE.md             <- Power BI blueprint, model, and wireframe
│   ├── powerbi_measures.dax                   <- 30+ production DAX measures
│   └── data_model_schema.json                 <- Relational schema & relationship specifications
│
└── 06_statistics_guide/
    └── STATISTICS_FOR_DATA_ANALYSTS.md        <- Complete statistics guide for analysts
```

---

## Quick-Start Commands

You can run and test every component directly from the terminal:

### 1. Execute SQL Practice Queries
```bash
python 02_sql_practice/run_sql_exercises.py
```
*Executes all 18 SQL queries across 6 progressive tiers and displays formatted ASCII tables.*

### 2. Execute Python Analysis & Regenerate Charts
```bash
python 03_python_analysis/analysis_script.py
```
*Computes all executive KPIs and saves 6 charts to `03_python_analysis/charts/`.*

### 3. Run Data Cleaning & Outlier Detection Pipeline
```bash
python 04_data_cleaning_eda/clean_dataset.py
```
*Audits `raw_sales_data.csv`, removes duplicates, cleans text, and writes `cleaned_sales_data.csv`.*

### 4. Run EDA Statistical Computations
```bash
python 04_data_cleaning_eda/run_eda.py
```
*Computes descriptive statistics, skewness, Pearson correlation matrix, and discount decay tables.*

### 5. Launch the Interactive Power BI Dashboard Preview
Open [`05_powerbi_dashboard/dashboard_preview.html`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/05_powerbi_dashboard/dashboard_preview.html) directly in any web browser to interact with live filters, charts, and drill-down tables.

