import pandas as pd
import numpy as np

df = pd.read_csv("data/cleaned_sales_data.csv")
df['Order_Date'] = pd.to_datetime(df['Order_Date'])

print("=" * 80)
print("EXPLORATORY DATA ANALYSIS (EDA) STATISTICAL COMPUTATIONS")
print("=" * 80)

# 1. Summary Statistics
num_cols = ['Quantity', 'Discount_Rate', 'Sales_Amount', 'Profit', 'Profit_Margin_Pct']
desc = df[num_cols].describe()
print("\n--- DESCRIPTIVE STATISTICS TABLE ---")
print(desc.to_string())

# 2. Skewness and Kurtosis
print("\n--- SKEWNESS & KURTOSIS ---")
for col in ['Sales_Amount', 'Profit', 'Quantity']:
    skew = df[col].skew()
    kurt = df[col].kurtosis()
    print(f"{col:15s} | Skewness: {skew:6.2f} | Kurtosis: {kurt:6.2f}")

# 3. Correlation Matrix
corr = df[['Unit_Price', 'Cost_Price', 'Quantity', 'Discount_Rate', 'Sales_Amount', 'Profit', 'Profit_Margin_Pct']].corr()
print("\n--- CORRELATION MATRIX (PEARSON) ---")
print(corr.round(3).to_string())

# 4. Category Breakdown
cat_stats = df.groupby('Category').agg(
    Orders=('Order_ID', 'count'),
    Total_Sales=('Sales_Amount', 'sum'),
    Total_Profit=('Profit', 'sum'),
    Mean_Sales=('Sales_Amount', 'mean'),
    Median_Sales=('Sales_Amount', 'median')
)
cat_stats['Margin_Pct'] = (cat_stats['Total_Profit'] / cat_stats['Total_Sales']) * 100
print("\n--- CATEGORY PERFORMANCE METRICS ---")
print(cat_stats.round(2).to_string())

# 5. Segment Breakdown
seg_stats = df.groupby('Customer_Segment').agg(
    Orders=('Order_ID', 'count'),
    Total_Sales=('Sales_Amount', 'sum'),
    Total_Profit=('Profit', 'sum')
)
seg_stats['Sales_Share_Pct'] = (seg_stats['Total_Sales'] / df['Sales_Amount'].sum()) * 100
print("\n--- CUSTOMER SEGMENT SHARE ---")
print(seg_stats.round(2).to_string())

# 6. Discount Impact on Profit Margin
disc_bins = pd.cut(df['Discount_Rate'], bins=[-0.01, 0.0, 0.10, 0.20, 0.50], labels=['0%', '1-10%', '11-20%', '>20%'])
disc_impact = df.groupby(disc_bins).agg(
    Tx_Count=('Order_ID', 'count'),
    Avg_Margin=('Profit_Margin_Pct', 'mean'),
    Total_Profit=('Profit', 'sum')
)
print("\n--- DISCOUNT BAND PROFITABILITY EROSION ---")
print(disc_impact.round(2).to_string())

