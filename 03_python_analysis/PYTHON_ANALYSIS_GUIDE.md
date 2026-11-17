# Python for Data Analysis: Complete Tutorial & Implementation Guide

Welcome to the **Python for Data Analysis Guide**. This document accompanies the Python script [`analysis_script.py`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/03_python_analysis/analysis_script.py) and Jupyter Notebook [`python_data_analysis.ipynb`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/03_python_analysis/python_data_analysis.ipynb).

---

## Table of Contents
1. [Core Python Fundamentals for Analysts](#1-core-python-fundamentals-for-analysts)
2. [NumPy: Vectorized Scientific Computing](#2-numpy-vectorized-scientific-computing)
3. [Pandas: Data Manipulation & Wrangling](#3-pandas-data-manipulation--wrangling)
4. [Business KPI Computations](#4-business-kpi-computations)
5. [Matplotlib & Data Visualization Principles](#5-matplotlib--data-visualization-principles)
6. [Best Practices for Production-Grade Analysis](#6-best-practices-for-production-grade-analysis)

---

## 1. Core Python Fundamentals for Analysts

Before using heavy data libraries like Pandas, a data analyst must master Python's native data structures and control flow.

### 1.1 Variables and Data Types
Python is dynamically typed:
```python
# Integers and Floats
quantity = 5
unit_price = 1099.99
is_corporate = True
customer_name = "Emily Watson"

# Type conversions
total_cost = float(quantity) * unit_price
order_summary = f"Customer {customer_name} ordered {quantity} units at ${unit_price:,.2f} each."
```

### 1.2 Functions & Type Hints
Writing modular, reusable analytical functions:
```python
def calculate_margin(revenue: float, profit: float) -> float:
    """Calculates gross margin percentage, handling edge cases."""
    if revenue <= 0:
        return 0.0
    return round((profit / revenue) * 100, 2)
```

### 1.3 Lists, Dictionaries, and Comprehensions
Data analysts frequently parse JSON payloads and API responses using dictionaries:
```python
# Customer record
customer_profile = {
    "id": "CUST-1001",
    "name": "Emily Watson",
    "segment": "Corporate",
    "orders": [1200.50, 450.00, 3100.20]
}

# List comprehension: Calculate total spend
total_spend = sum([spend for spend in customer_profile["orders"]])
```

### 1.4 File Handling with Context Managers
Always open files using `with` to guarantee automatic resource cleanup:
```python
import csv

with open("data/cleaned_sales_data.csv", mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    first_five = [row for i, row in enumerate(reader) if i < 5]
```

---

## 2. NumPy: Vectorized Scientific Computing

NumPy provides multidimensional arrays (`ndarray`) and vectorized math written in optimized C.

### 2.1 The Vectorization Advantage
In pure Python, multiplying a list of 1,000,000 numbers requires a slow `for` loop. In NumPy, operations are vectorized:
```python
import numpy as np

# Vectorized multiplication across entire column
sales = np.array([100.0, 250.0, 500.0])
discounts = np.array([0.10, 0.05, 0.20])

discounted_sales = sales * (1 - discounts)
# Output: array([ 90., 237.5, 400. ])
```

### 2.2 Key Statistical Functions
```python
np.mean(sales)       # Arithmetic Average
np.median(sales)     # 50th Percentile (robust against extreme outliers)
np.std(sales)        # Standard Deviation (spread of data)
np.percentile(sales, [25, 50, 75, 95])  # Quartiles and percentiles
```

---

## 3. Pandas: Data Manipulation & Wrangling

Pandas is the core workhorse for tabular data (`DataFrame` and `Series`).

### 3.1 Loading and Inspecting Data
```python
import pandas as pd

df = pd.read_csv("data/cleaned_sales_data.csv")

# Quick diagnosis
df.shape         # (1200, 25)
df.info()        # Data types and non-null counts
df.describe()    # Numerical summary statistics (mean, std, min, max, quartiles)
df.head(5)       # First 5 rows
```

### 3.2 Handling Dates and Feature Engineering
```python
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Ship_Date'] = pd.to_datetime(df['Ship_Date'])

# Calculate delivery latency
df['Delivery_Days'] = (df['Ship_Date'] - df['Order_Date']).dt.days

# Extract time components for seasonality analysis
df['Order_Year'] = df['Order_Date'].dt.year
df['Order_Month'] = df['Order_Date'].dt.strftime('%Y-%m')
df['Day_of_Week'] = df['Order_Date'].dt.day_name()
```

### 3.3 Aggregations: `groupby` and `pivot_table`
```python
# Multi-metric aggregation
category_kpis = df.groupby('Category').agg(
    Total_Revenue=('Sales_Amount', 'sum'),
    Total_Profit=('Profit', 'sum'),
    Average_Order_Value=('Sales_Amount', 'mean'),
    Order_Count=('Order_ID', 'nunique')
).reset_index()

# 2D Pivot Table (Customer Segment vs Region)
segment_region_pivot = df.pivot_table(
    index='Customer_Segment',
    columns='Region',
    values='Sales_Amount',
    aggfunc='sum',
    fill_value=0
)
```

---

## 4. Business KPI Computations

From our dataset of 1,200 transactions:
- **Total Gross Revenue:** `df['Sales_Amount'].sum()` = **$1,751,917.60**
- **Total Net Profit:** `df['Profit'].sum()` = **$532,258.60**
- **Overall Gross Margin %:** `(Total_Profit / Total_Revenue) * 100` = **30.38%**
- **Average Order Value (AOV):** `Total_Revenue / Total_Orders` = **$1,459.93**
- **Total Units Sold:** `df['Quantity'].sum()` = **3,108 Units**

---

## 5. Matplotlib & Data Visualization Principles

We generated 6 high-resolution visualizations located in [`03_python_analysis/charts/`](file:///c:/Users/SANTHOSH/Desktop/blue_stocks/03_python_analysis/charts/):

1. **`monthly_revenue_trend.png`**: Dual-line chart illustrating revenue and profit trajectory over 22 months.
2. **`category_sales_profit.png`**: Horizontal clustered bar chart comparing revenue volume against profit margin.
3. **`customer_segment_distribution.png`**: Donut chart detailing revenue share (Corporate 65%, Consumer 20%, Home Office 15%).
4. **`profit_vs_discount_scatter.png`**: Scatter plot exposing margin decay beyond 20% discount rates.
5. **`regional_sales_breakdown.png`**: Bar chart ranking geographic performance.
6. **`executive_kpi_dashboard.png`**: 4-panel executive summary dashboard combining trends, distributions, and bar charts.

---

## 6. Best Practices for Production-Grade Analysis

1. **Avoid in-place mutation (`inplace=True`):** It is deprecated in recent Pandas versions; prefer assignment: `df = df.dropna()`.
2. **Always inspect `.dtypes`:** A numeric column accidentally parsed as `object` will cause mathematical operations to silently fail or concatenate strings.
3. **Use `.loc` and `.iloc` explicitly:** Avoid chained indexing (`df['Col'][0] = 5`), which triggers `SettingWithCopyWarning`.

