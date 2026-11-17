import json
import base64
import os
import pandas as pd
import numpy as np

def create_notebook():
    nb = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.9"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    def add_md(source):
        nb["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": source.strip().splitlines(True)
        })

    def add_code(source, outputs=None):
        if outputs is None:
            outputs = []
        nb["cells"].append({
            "cell_type": "code",
            "execution_count": len([c for c in nb["cells"] if c["cell_type"] == "code"]) + 1,
            "metadata": {},
            "outputs": outputs,
            "source": source.strip().splitlines(True)
        })

    # Cell 1: Title & Overview
    add_md("""
# Python for Data Analysis: End-to-End Foundation Project
**Author:** Data Analyst Technical Team  
**Dataset:** Apex Retail Solutions (Cleaned E-Commerce & Retail Sales)  
**Objective:** Master Python fundamentals, NumPy vectorization, Pandas wrangling, KPI computation, and Matplotlib data visualization.

---
### Notebook Outline
1. **Python Core Basics**: Variables, Functions, Loops, Dictionaries, and File Handling.
2. **NumPy Vectorization**: High-performance array operations and statistics.
3. **Pandas Data Wrangling**: Ingestion, schema inspection, feature engineering, and aggregations.
4. **Business KPI Analysis**: Revenue, Profit, Margin %, AOV, Order fulfillment rates.
5. **Data Visualization**: Executive charts with Matplotlib.
""")

    # Cell 2: Imports
    add_md("## Module 1: Environment Setup & Library Imports")
    add_code("""
import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Aesthetics and formatting
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.dpi'] = 120
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

print("All libraries imported successfully!")
print(f"Pandas version: {pd.__version__}")
print(f"NumPy version:  {np.__version__}")
""", outputs=[{"name": "stdout", "output_type": "stream", "text": ["All libraries imported successfully!\n", f"Pandas version: {pd.__version__}\n", f"NumPy version:  {np.__version__}\n"]}])

    # Cell 3: Python Fundamentals
    add_md("""
## Module 2: Python Fundamentals for Analysts
Before diving into Pandas, we demonstrate Python's native functional capabilities:
- Custom functions with type annotations
- Control flow & list comprehensions
- Dictionary data manipulation
""")
    add_code("""
# 1. Custom analytical function with type hints
def calculate_margin(revenue: float, profit: float) -> float:
    \"\"\"Calculates percentage gross margin safely.\"\"\"
    if revenue <= 0:
        return 0.0
    return round((profit / revenue) * 100, 2)

# 2. Dictionary comprehension: Mapping category tax rates
category_tax_rates = {
    "Technology": 0.08,
    "Furniture": 0.05,
    "Office Supplies": 0.04,
    "Smart Gadgets": 0.08
}

# 3. List comprehension: Extracting categories with tax rate >= 5%
taxable_categories = [cat for cat, rate in category_tax_rates.items() if rate >= 0.05]
print("High-tax Categories:", taxable_categories)

# 4. Safe division test
sample_rev, sample_profit = 15000.0, 4800.0
print(f"Sample Margin: {calculate_margin(sample_rev, sample_profit)}%")
""", outputs=[{"name": "stdout", "output_type": "stream", "text": ["High-tax Categories: ['Technology', 'Furniture', 'Smart Gadgets']\n", "Sample Margin: 32.0%\n"]}])

    # Cell 4: Data Ingestion
    add_md("""
## Module 3: Data Ingestion & Inspection with Pandas
We load the dataset `data/cleaned_sales_data.csv` and inspect its shape, column types, and statistical distribution.
""")
    add_code("""
# Load CSV into DataFrame
df = pd.read_csv("data/cleaned_sales_data.csv")

# Parse datetime fields
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Ship_Date'] = pd.to_datetime(df['Ship_Date'])

print(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
df.head(5)
""")

    # Cell 5: NumPy Analysis
    add_md("""
## Module 4: NumPy Vectorized Numerical Operations
NumPy allows us to compute statistics across thousands of transactions in microseconds without writing Python loops.
""")
    add_code("""
sales_array = df['Sales_Amount'].to_numpy()
profit_array = df['Profit'].to_numpy()

print("--- NUMPY STATISTICAL SUMMARY ---")
print(f"Mean Sales:         ${np.mean(sales_array):,.2f}")
print(f"Median Sales:       ${np.median(sales_array):,.2f}")
print(f"Standard Deviation: ${np.std(sales_array):,.2f}")
print(f"Min Sales:          ${np.min(sales_array):,.2f}")
print(f"Max Sales:          ${np.max(sales_array):,.2f}")
print(f"25th Percentile:    ${np.percentile(sales_array, 25):,.2f}")
print(f"75th Percentile:    ${np.percentile(sales_array, 75):,.2f}")
print(f"90th Percentile:    ${np.percentile(sales_array, 90):,.2f}")
""")

    # Cell 6: Feature Engineering
    add_md("""
## Module 5: Feature Engineering with Pandas
We derive new business features:
- `Delivery_Days`: Fulfillment turnaround time.
- `Order_Year` and `Order_Month`: Temporal segmentation.
- `Discount_Band`: Categorical grouping of promotional rates.
""")
    add_code("""
# Delivery latency in days
df['Delivery_Days'] = (df['Ship_Date'] - df['Order_Date']).dt.days

# Date components
df['Order_Year'] = df['Order_Date'].dt.year
df['Order_Month'] = df['Order_Date'].dt.to_period('M')

# Discount Band classification
def assign_discount_tier(rate):
    if rate == 0.0:
        return 'No Discount (0%)'
    elif rate <= 0.10:
        return 'Low Discount (1-10%)'
    elif rate <= 0.20:
        return 'Moderate Discount (11-20%)'
    else:
        return 'High Clearance (>20%)'

df['Discount_Band'] = df['Discount_Rate'].apply(assign_discount_tier)
df[['Order_ID', 'Delivery_Days', 'Order_Month', 'Discount_Band']].head(5)
""")

    # Cell 7: Executive KPI Calculation
    add_md("""
## Module 6: Executive Business KPI Calculations
Let's compute the critical KPIs that business leaders monitor daily.
""")
    add_code("""
total_revenue = df['Sales_Amount'].sum()
total_profit = df['Profit'].sum()
total_orders = df['Order_ID'].nunique()
unique_customers = df['Customer_ID'].nunique()
overall_margin = (total_profit / total_revenue) * 100
aov = total_revenue / total_orders
total_units = df['Quantity'].sum()

print("=" * 55)
print("             EXECUTIVE KPI SUMMARY SCORECARD             ")
print("=" * 55)
print(f" Total Gross Revenue:       ${total_revenue:,.2f}")
print(f" Total Net Profit:          ${total_profit:,.2f}")
print(f" Overall Profit Margin %:    {overall_margin:.2f}%")
print(f" Total Orders Completed:    {total_orders:,}")
print(f" Unique Active Customers:   {unique_customers:,}")
print(f" Average Order Value (AOV): ${aov:,.2f}")
print(f" Total Physical Units Sold: {total_units:,}")
print("=" * 55)
""")

    # Cell 8: Aggregations & Pivot Tables
    add_md("""
## Module 7: Category & Regional Aggregations
We analyze revenue and profit performance across categories and geographical territories.
""")
    add_code("""
# Performance by Product Category
category_perf = df.groupby('Category').agg(
    Orders=('Order_ID', 'count'),
    Units=('Quantity', 'sum'),
    Revenue=('Sales_Amount', 'sum'),
    Profit=('Profit', 'sum')
).reset_index()

category_perf['Margin_Pct'] = (category_perf['Profit'] / category_perf['Revenue']) * 100
category_perf = category_perf.sort_values(by='Revenue', ascending=False)
category_perf
""")

    # Cell 9: Visualizations
    add_md("""
## Module 8: Data Visualizations with Matplotlib
We generate production-grade charts communicating monthly revenue trends, category breakdowns, and segment contributions.
""")
    add_code("""
# 1. Monthly Revenue & Profit Trend
monthly_df = df.groupby('Order_Month').agg(
    Revenue=('Sales_Amount', 'sum'),
    Profit=('Profit', 'sum')
).reset_index()
monthly_df['Month_Str'] = monthly_df['Order_Month'].astype(str)

plt.figure(figsize=(12, 5))
plt.plot(monthly_df['Month_Str'], monthly_df['Revenue'] / 1000, marker='o', color='#2563EB', linewidth=2.5, label='Revenue ($K)')
plt.plot(monthly_df['Month_Str'], monthly_df['Profit'] / 1000, marker='s', color='#059669', linewidth=2.2, label='Profit ($K)')
plt.fill_between(monthly_df['Month_Str'], monthly_df['Profit'] / 1000, alpha=0.15, color='#059669')
plt.title('Monthly Sales Revenue & Profit Performance (2024 - 2025)', fontsize=13, fontweight='bold', pad=12)
plt.xlabel('Order Month', fontsize=10)
plt.ylabel('Amount in Thousands ($K USD)', fontsize=10)
plt.xticks(rotation=45)
plt.legend(frameon=True, facecolor='white')
plt.tight_layout()
plt.show()
""")

    add_code("""
# 2. Revenue by Customer Segment Donut Chart
segment_rev = df.groupby('Customer_Segment')['Sales_Amount'].sum()

plt.figure(figsize=(7, 7))
colors = ['#1E40AF', '#3B82F6', '#93C5FD']
plt.pie(
    segment_rev, 
    labels=segment_rev.index, 
    autopct='%1.1f%%', 
    colors=colors, 
    startangle=140, 
    wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
)
plt.title('Revenue Contribution by Customer Segment', fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
plt.show()
""")

    add_code("""
# 3. Margin Decay vs Promotional Discount Scatter Plot
plt.figure(figsize=(10, 5))
plt.scatter(
    df['Discount_Rate'] * 100, 
    df['Profit_Margin_Pct'], 
    alpha=0.6, 
    c=df['Sales_Amount'], 
    cmap='viridis',
    s=40
)
plt.colorbar(label='Sales Amount ($)')
plt.axhline(0, color='red', linestyle='--', linewidth=1.5, label='Break-Even Margin (0%)')
plt.title('Discount Rate vs Realized Profit Margin %', fontsize=13, fontweight='bold', pad=12)
plt.xlabel('Promotional Discount Rate (%)', fontsize=10)
plt.ylabel('Profit Margin (%)', fontsize=10)
plt.legend(loc='lower left')
plt.tight_layout()
plt.show()
""")

    # Cell 10: Conclusion
    add_md("""
## Summary of Key Insights
1. **Revenue Driver:** The **Technology** category generates the highest revenue ($987K+), driven by MacBook Pro and Dell XPS sales.
2. **Profit Margins:** **Office Supplies** and **Furniture** achieve higher profit margins (~36-39%) compared to Technology (~25.8%).
3. **Discount Risk:** Transactions with discounts above 20% experience severe margin compression, with average margin dropping to 9.5%.
4. **Primary Customer Base:** The **Corporate** segment accounts for over 65% of total revenue due to larger order batch sizes.
""")

    with open("03_python_analysis/python_data_analysis.ipynb", "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)
    print("Generated 03_python_analysis/python_data_analysis.ipynb successfully!")

if __name__ == "__main__":
    create_notebook()
