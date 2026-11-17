import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ensure output chart directory exists
os.makedirs("03_python_analysis/charts", exist_ok=True)

# Set clean aesthetic style for Matplotlib
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Segoe UI'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 150

print("=" * 80)
print("PYTHON FOR DATA ANALYSIS PIPELINE: APEX RETAIL SOLUTIONS")
print("=" * 80)

# -------------------------------------------------------------
# 1. Python Basics: Custom Functions & Logic
# -------------------------------------------------------------
def calculate_margin(sales: float, profit: float) -> float:
    """Calculates the percentage profit margin safely avoiding division by zero."""
    if sales <= 0:
        return 0.0
    return round((profit / sales) * 100, 2)

def classify_order_priority(delivery_days: int) -> str:
    """Classifies order fulfillment speed."""
    if delivery_days <= 1:
        return "Express / Priority"
    elif delivery_days <= 3:
        return "Standard Fast"
    else:
        return "Economy Regular"

# -------------------------------------------------------------
# 2. Data Ingestion & Pandas Inspection
# -------------------------------------------------------------
data_path = "data/cleaned_sales_data.csv"
print(f"\n[Step 1] Loading cleaned dataset from {data_path}...")
df = pd.read_csv(data_path)

# Ensure proper datetime parsing
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Ship_Date'] = pd.to_datetime(df['Ship_Date'])
df['Order_Month'] = df['Order_Date'].dt.to_period('M')
df['Delivery_Days'] = (df['Ship_Date'] - df['Order_Date']).dt.days

print(f"Dataset Dimensions: {df.shape[0]} rows, {df.shape[1]} columns")
print("Column Types:\n", df.dtypes.value_counts())

# -------------------------------------------------------------
# 3. NumPy Array Operations
# -------------------------------------------------------------
print("\n[Step 2] Performing NumPy Numerical Operations...")
sales_np = df['Sales_Amount'].to_numpy()
profit_np = df['Profit'].to_numpy()

print(f"NumPy Mean Sales:   ${np.mean(sales_np):,.2f}")
print(f"NumPy Median Sales: ${np.median(sales_np):,.2f}")
print(f"NumPy Std Dev:      ${np.std(sales_np):,.2f}")
print(f"NumPy 90th Pct:     ${np.percentile(sales_np, 90):,.2f}")

# -------------------------------------------------------------
# 4. Executive KPI Calculations
# -------------------------------------------------------------
print("\n[Step 3] Computing Business KPIs...")
total_revenue = df['Sales_Amount'].sum()
total_profit = df['Profit'].sum()
total_orders = df['Order_ID'].nunique()
unique_customers = df['Customer_ID'].nunique()
overall_margin = calculate_margin(total_revenue, total_profit)
aov = total_revenue / total_orders
units_sold = df['Quantity'].sum()

# Cancellation & Return rates
total_transactions = len(df)
cancelled_count = len(df[df['Order_Status'] == 'Cancelled'])
refunded_count = len(df[df['Order_Status'] == 'Refunded'])
cancellation_rate = (cancelled_count / total_transactions) * 100
refund_rate = (refunded_count / total_transactions) * 100

print("-" * 50)
print(f"TOTAL GROSS REVENUE:    ${total_revenue:,.2f}")
print(f"TOTAL NET PROFIT:       ${total_profit:,.2f}")
print(f"OVERALL PROFIT MARGIN:   {overall_margin:.2f}%")
print(f"TOTAL DISTINCT ORDERS:   {total_orders:,}")
print(f"UNIQUE ACTIVE CUSTOMERS: {unique_customers:,}")
print(f"AVERAGE ORDER VALUE:    ${aov:,.2f}")
print(f"TOTAL UNITS SOLD:        {units_sold:,}")
print(f"REFUND RATE:             {refund_rate:.2f}%")
print(f"CANCELLATION RATE:       {cancellation_rate:.2f}%")
print("-" * 50)

# -------------------------------------------------------------
# 5. Visualizations Generation (Matplotlib)
# -------------------------------------------------------------
print("\n[Step 4] Generating High-Resolution Charts...")

# Chart 1: Monthly Revenue & Profit Trend
monthly_summary = df.groupby('Order_Month').agg(
    Revenue=('Sales_Amount', 'sum'),
    Profit=('Profit', 'sum')
).reset_index()
monthly_summary['Month_Str'] = monthly_summary['Order_Month'].astype(str)

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(monthly_summary['Month_Str'], monthly_summary['Revenue'] / 1000, marker='o', linewidth=2.5, color='#2563EB', label='Revenue ($K)')
ax.plot(monthly_summary['Month_Str'], monthly_summary['Profit'] / 1000, marker='s', linewidth=2.2, color='#059669', label='Profit ($K)')
ax.fill_between(monthly_summary['Month_Str'], monthly_summary['Profit'] / 1000, alpha=0.15, color='#059669')
ax.set_title('Monthly Revenue & Profit Performance (2024 - 2025)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Order Month', fontsize=11, labelpad=10)
ax.set_ylabel('Amount in Thousands ($K USD)', fontsize=11, labelpad=10)
ax.tick_params(axis='x', rotation=45)
ax.legend(frameon=True, facecolor='white', loc='upper left')
plt.tight_layout()
fig.savefig('03_python_analysis/charts/monthly_revenue_trend.png', dpi=300)
plt.close(fig)
print("  -> Saved: 03_python_analysis/charts/monthly_revenue_trend.png")

# Chart 2: Category Sales & Profit Breakdown
cat_summary = df.groupby('Category').agg(
    Revenue=('Sales_Amount', 'sum'),
    Profit=('Profit', 'sum')
).sort_values(by='Revenue', ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
y = np.arange(len(cat_summary))
height = 0.35
ax.barh(y + height/2, cat_summary['Revenue'] / 1000, height, label='Revenue ($K)', color='#3B82F6')
ax.barh(y - height/2, cat_summary['Profit'] / 1000, height, label='Profit ($K)', color='#10B981')
ax.set_yticks(y)
ax.set_yticklabels(cat_summary.index, fontsize=11)
ax.set_xlabel('Amount ($K USD)', fontsize=11, labelpad=10)
ax.set_title('Revenue vs Profit by Product Category', fontsize=14, fontweight='bold', pad=15)
ax.legend(frameon=True, facecolor='white')
for i, v in enumerate(cat_summary['Revenue'] / 1000):
    ax.text(v + 10, i + height/2 - 0.08, f"${v:,.1f}K", fontsize=9, color='#1E3A8A', fontweight='bold')
plt.tight_layout()
fig.savefig('03_python_analysis/charts/category_sales_profit.png', dpi=300)
plt.close(fig)
print("  -> Saved: 03_python_analysis/charts/category_sales_profit.png")

# Chart 3: Customer Segment Distribution
seg_summary = df.groupby('Customer_Segment')['Sales_Amount'].sum()
colors = ['#1E40AF', '#3B82F6', '#93C5FD']

fig, ax = plt.subplots(figsize=(8, 6))
wedges, texts, autotexts = ax.pie(
    seg_summary,
    labels=seg_summary.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=colors,
    pctdistance=0.75,
    wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
)
for at in autotexts:
    at.set_color('white')
    at.set_fontweight('bold')
    at.set_fontsize(11)
ax.set_title('Revenue Share by Customer Segment', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
fig.savefig('03_python_analysis/charts/customer_segment_distribution.png', dpi=300)
plt.close(fig)
print("  -> Saved: 03_python_analysis/charts/customer_segment_distribution.png")

# Chart 4: Discount Rate vs Profit Margin (Scatter Plot)
fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(
    df['Discount_Rate'] * 100,
    df['Profit_Margin_Pct'],
    c=df['Sales_Amount'],
    cmap='viridis',
    alpha=0.65,
    edgecolors='none',
    s=45
)
cbar = plt.colorbar(scatter)
cbar.set_label('Sales Amount ($)', fontsize=10, labelpad=10)
ax.axhline(0, color='#DC2626', linestyle='--', linewidth=1.5, label='Break-even (0% Margin)')
ax.set_title('Discount Rate vs Realized Profit Margin %', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Promotional Discount Rate (%)', fontsize=11, labelpad=10)
ax.set_ylabel('Profit Margin (%)', fontsize=11, labelpad=10)
ax.legend(loc='lower left')
plt.tight_layout()
fig.savefig('03_python_analysis/charts/profit_vs_discount_scatter.png', dpi=300)
plt.close(fig)
print("  -> Saved: 03_python_analysis/charts/profit_vs_discount_scatter.png")

# Chart 5: Regional Sales Breakdown
region_summary = df.groupby('Region')['Sales_Amount'].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(region_summary.index, region_summary.values / 1000, color='#6366F1', width=0.55)
ax.set_title('Total Sales Revenue by Geographic Region', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Territory', fontsize=11, labelpad=10)
ax.set_ylabel('Revenue ($K USD)', fontsize=11, labelpad=10)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 10, f"${yval:,.1f}K", ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.tight_layout()
fig.savefig('03_python_analysis/charts/regional_sales_breakdown.png', dpi=300)
plt.close(fig)
print("  -> Saved: 03_python_analysis/charts/regional_sales_breakdown.png")

# Chart 6: 4-Panel Executive Summary Grid
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Top-Left: Monthly Trend
axes[0, 0].plot(monthly_summary['Month_Str'], monthly_summary['Revenue'] / 1000, color='#2563EB', marker='o', label='Revenue')
axes[0, 0].set_title('Monthly Revenue Trend ($K)', fontsize=12, fontweight='bold')
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].grid(True, linestyle=':', alpha=0.6)

# Top-Right: Category Revenue
axes[0, 1].barh(cat_summary.index, cat_summary['Revenue'] / 1000, color='#059669')
axes[0, 1].set_title('Revenue by Product Category ($K)', fontsize=12, fontweight='bold')
axes[0, 1].grid(True, linestyle=':', alpha=0.6)

# Bottom-Left: Customer Segment Donut
axes[1, 0].pie(seg_summary, labels=seg_summary.index, autopct='%1.1f%%', colors=colors, startangle=90, wedgeprops=dict(width=0.4))
axes[1, 0].set_title('Segment Revenue Split', fontsize=12, fontweight='bold')

# Bottom-Right: Region Distribution
axes[1, 1].bar(region_summary.index, region_summary.values / 1000, color='#F59E0B')
axes[1, 1].set_title('Regional Sales Contribution ($K)', fontsize=12, fontweight='bold')
axes[1, 1].grid(True, linestyle=':', alpha=0.6)

plt.suptitle('Apex Retail Solutions - Executive KPI Dashboard', fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()
fig.savefig('03_python_analysis/charts/executive_kpi_dashboard.png', dpi=300)
plt.close(fig)
print("  -> Saved: 03_python_analysis/charts/executive_kpi_dashboard.png")

print("\n" + "=" * 80)
print("PYTHON ANALYSIS PIPELINE COMPLETE: All KPIs computed and charts exported.")
print("=" * 80)

