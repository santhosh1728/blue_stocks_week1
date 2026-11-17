import os
import pandas as pd
import numpy as np

print("=" * 80)
print("DATA CLEANING & STANDARDIZATION PIPELINE")
print("Input:  data/raw_sales_data.csv")
print("Output: data/cleaned_sales_data.csv")
print("=" * 80)

# Step 1: Ingestion
raw_path = "data/raw_sales_data.csv"
df = pd.read_csv(raw_path)
initial_rows = len(df)
print(f"\n[Audit 1] Loaded {initial_rows} raw records.")

# Step 2: Deduplication
duplicates_count = df.duplicated().sum()
print(f"[Audit 2] Detected {duplicates_count} exact duplicate rows. Removing duplicates...")
df = df.drop_duplicates().reset_index(drop=True)
print(f"          Rows remaining after deduplication: {len(df)}")

# Step 3: String Trimming & Casing Normalization
print("[Audit 3] Normalizing text columns (trimming whitespace & standardizing casing)...")
text_cols = ["Customer_Name", "Category", "Subcategory", "Product_Name", "Region", "Ship_Mode", "Customer_Segment"]
for col in text_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# Standardize Category title casing (e.g., 'technology' -> 'Technology')
df["Category"] = df["Category"].str.strip().str.title()
# Standardize Region
df["Region"] = df["Region"].str.strip()

# Step 4: Missing Value Treatment
print("[Audit 4] Auditing and imputing missing values (NaNs)...")
null_counts = df.isnull().sum()
for col, cnt in null_counts.items():
    if cnt > 0:
        print(f"          Column '{col}' has {cnt} missing values.")

# Impute Customer_Email using synthetic pattern if missing
df["Customer_Email"] = df["Customer_Email"].fillna(
    df["Customer_Name"].str.lower().str.replace(" ", ".") + "@enterprise-auto.com"
)

# Impute Customer_Segment based on mode or 'Consumer' default
df["Customer_Segment"] = df["Customer_Segment"].fillna("Consumer")

# Impute Discount_Rate: fill missing with 0.0 (assumes no discount applied)
df["Discount_Rate"] = df["Discount_Rate"].fillna(0.0)

# Step 5: Date Normalization (handling mixed date formats like MM/DD/YYYY and YYYY-MM-DD)
print("[Audit 5] Normalizing date formats to ISO-8601 (YYYY-MM-DD)...")
df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="mixed").dt.strftime("%Y-%m-%d")
df["Ship_Date"] = pd.to_datetime(df["Ship_Date"], format="mixed").dt.strftime("%Y-%m-%d")

# Step 6: Data Validation & Outlier Detection
print("[Audit 6] Validating numeric boundaries and detecting outliers...")
# Fix negative quantities or negative sales caused by data entry typos
negative_qty_mask = df["Quantity"] < 0
if negative_qty_mask.sum() > 0:
    print(f"          Found {negative_qty_mask.sum()} records with negative quantity. Correcting to absolute value...")
    df["Quantity"] = df["Quantity"].abs()

# Detect extreme revenue typos using IQR (Interquartile Range)
Q1 = df["Sales_Amount"].quantile(0.25)
Q3 = df["Sales_Amount"].quantile(0.75)
IQR = Q3 - Q1
upper_bound = Q3 + (3.0 * IQR) # Extreme outlier threshold

extreme_revenue_outliers = df[df["Sales_Amount"] > upper_bound]
print(f"          IQR Upper Bound for Sales: ${upper_bound:,.2f}")
print(f"          Extreme revenue outliers detected: {len(extreme_revenue_outliers)}")

# Recalculate true Sales_Amount and Profit based on master unit prices and quantities
# Sales_Amount = Quantity * Unit_Price * (1 - Discount_Rate)
df["Sales_Amount"] = (df["Quantity"] * df["Unit_Price"] * (1 - df["Discount_Rate"])).round(2)
df["Profit"] = (df["Sales_Amount"] - (df["Quantity"] * df["Cost_Price"])).round(2)
df["Profit_Margin_Pct"] = ((df["Profit"] / df["Sales_Amount"]) * 100).round(2)

# Step 7: Chronological Ordering & Export
df = df.sort_values(by="Order_Date").reset_index(drop=True)
clean_export_path = "data/cleaned_sales_data.csv"
df.to_csv(clean_export_path, index=False)

print(f"\n[Success] Cleaned dataset exported to {clean_export_path} ({len(df)} records).")
print(f"          Data loss / rejected anomalies: {initial_rows - len(df)} duplicate/invalid rows removed.")
print("=" * 80)

