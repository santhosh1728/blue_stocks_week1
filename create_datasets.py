import os
import random
import datetime
import sqlite3
import pandas as pd
import numpy as np

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

# Ensure directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("02_sql_practice", exist_ok=True)

# 1. Master Product Catalog
products_master = [
    # Technology
    ("PROD-TEC-001", "MacBook Pro 16", "Technology", "Laptops", 1800.0, 2499.0),
    ("PROD-TEC-002", "Dell XPS 15", "Technology", "Laptops", 1400.0, 1899.0),
    ("PROD-TEC-003", "ThinkPad X1 Carbon", "Technology", "Laptops", 1200.0, 1650.0),
    ("PROD-TEC-004", "iPhone 15 Pro", "Technology", "Phones", 750.0, 1099.0),
    ("PROD-TEC-005", "Samsung Galaxy S24", "Technology", "Phones", 650.0, 999.0),
    ("PROD-TEC-006", "Google Pixel 8 Pro", "Technology", "Phones", 550.0, 899.0),
    ("PROD-TEC-007", "Logitech MX Master 3S", "Technology", "Accessories", 60.0, 99.0),
    ("PROD-TEC-008", "Keychron K2 Mechanical Keyboard", "Technology", "Accessories", 50.0, 89.0),
    ("PROD-TEC-009", "Dell UltraSharp 27 4K Monitor", "Technology", "Accessories", 350.0, 549.0),
    ("PROD-TEC-010", "Anker 737 Power Bank", "Technology", "Accessories", 80.0, 140.0),

    # Furniture
    ("PROD-FUR-001", "Herman Miller Aeron Chair", "Furniture", "Chairs", 850.0, 1395.0),
    ("PROD-FUR-002", "Steelcase Gesture Chair", "Furniture", "Chairs", 780.0, 1250.0),
    ("PROD-FUR-003", "Ergonomic Mesh Task Chair", "Furniture", "Chairs", 160.0, 299.0),
    ("PROD-FUR-004", "Jarvis Bamboo Standing Desk", "Furniture", "Desks", 420.0, 699.0),
    ("PROD-FUR-005", "Uplift V2 Commercial Desk", "Furniture", "Desks", 480.0, 799.0),
    ("PROD-FUR-006", "Minimalist Oak Writing Desk", "Furniture", "Desks", 180.0, 320.0),
    ("PROD-FUR-007", "Steelcase 3-Drawer Filing Cabinet", "Furniture", "Storage", 140.0, 260.0),
    ("PROD-FUR-008", "Modular Bookshelf 5-Tier", "Furniture", "Storage", 90.0, 179.0),

    # Office Supplies
    ("PROD-OFF-001", "Heavy Duty Desktop Stapler", "Office Supplies", "Supplies", 12.0, 24.0),
    ("PROD-OFF-002", "Premium Multipurpose Copy Paper (5 Reams)", "Office Supplies", "Paper", 22.0, 45.0),
    ("PROD-OFF-003", "Moleskine Classic Hardcover Notebook", "Office Supplies", "Paper", 11.0, 22.0),
    ("PROD-OFF-004", "Pilot G2 Gel Pens (Pack of 12)", "Office Supplies", "Supplies", 8.0, 18.0),
    ("PROD-OFF-005", "Fellowes Powershred Cross-Cut Shredder", "Office Supplies", "Machines", 110.0, 199.0),
    ("PROD-OFF-006", "Epson EcoTank Color Printer", "Office Supplies", "Machines", 180.0, 299.0),

    # Smart Gadgets
    ("PROD-SMT-001", "Apple Watch Series 9", "Smart Gadgets", "Wearables", 260.0, 399.0),
    ("PROD-SMT-002", "Garmin Fenix 7 Pro", "Smart Gadgets", "Wearables", 480.0, 799.0),
    ("PROD-SMT-003", "Sony WH-1000XM5 ANC Headphones", "Smart Gadgets", "Smart Audio", 240.0, 399.0),
    ("PROD-SMT-004", "AirPods Pro (2nd Gen)", "Smart Gadgets", "Smart Audio", 160.0, 249.0),
    ("PROD-SMT-005", "Philips Hue Smart LED Starter Kit", "Smart Gadgets", "Lighting", 110.0, 199.0),
    ("PROD-SMT-006", "BenQ ScreenBar Monitor Light", "Smart Gadgets", "Lighting", 75.0, 139.0)
]

# 2. Master Customer List
customers_master = [
    ("CUST-1001", "Emily Watson", "emily.watson@enterprise.com", "New York", "NY", "USA", "North America", "Corporate", "2023-01-15"),
    ("CUST-1002", "Michael Chen", "mchen@gmail.com", "San Francisco", "CA", "USA", "North America", "Consumer", "2023-02-10"),
    ("CUST-1003", "Sophia Rodriguez", "sophia.r@techcorp.io", "Austin", "TX", "USA", "North America", "Corporate", "2023-03-05"),
    ("CUST-1004", "James Wilson", "jwilson_home@yahoo.com", "Chicago", "IL", "USA", "North America", "Home Office", "2023-03-22"),
    ("CUST-1005", "Emma Dubois", "emma.dubois@paris-design.fr", "Paris", "IDF", "France", "Europe", "Corporate", "2023-04-12"),
    ("CUST-1006", "Lukas Schmidt", "lukas.schmidt@berlin-tech.de", "Berlin", "BE", "Germany", "Europe", "Corporate", "2023-05-01"),
    ("CUST-1007", "Liam O'Connor", "liam.oconnor@dublin-net.ie", "Dublin", "L", "Ireland", "Europe", "Consumer", "2023-05-18"),
    ("CUST-1008", "Yuki Tanaka", "tanaka.yuki@tokyo-ventures.jp", "Tokyo", "13", "Japan", "APAC", "Corporate", "2023-06-08"),
    ("CUST-1009", "Oliver Brown", "oliver.brown@sydney-solutions.au", "Sydney", "NSW", "Australia", "APAC", "Corporate", "2023-06-25"),
    ("CUST-1010", "Chloe Martin", "chloe.m@creatives.co.uk", "London", "ENG", "UK", "Europe", "Home Office", "2023-07-14"),
    ("CUST-1011", "David Miller", "dmiller88@gmail.com", "Seattle", "WA", "USA", "North America", "Consumer", "2023-08-02"),
    ("CUST-1012", "Jessica Taylor", "jessica.taylor@toronto-biz.ca", "Toronto", "ON", "Canada", "North America", "Corporate", "2023-08-19"),
    ("CUST-1013", "Alexander Wright", "alex.wright@consulting.com", "Boston", "MA", "USA", "North America", "Corporate", "2023-09-04"),
    ("CUST-1014", "Ananya Sharma", "ananya.sharma@bangalore-tech.in", "Bangalore", "KA", "India", "APAC", "Corporate", "2023-09-20"),
    ("CUST-1015", "Lucas Silva", "lucas.silva@saopaulo-hub.br", "Sao Paulo", "SP", "Brazil", "LATAM", "Consumer", "2023-10-11"),
    ("CUST-1016", "Hannah Abbott", "hannah.a@freelance.org", "Denver", "CO", "USA", "North America", "Home Office", "2023-10-29"),
    ("CUST-1017", "Daniel Garcia", "daniel.garcia@madrid-trade.es", "Madrid", "MD", "Spain", "Europe", "Corporate", "2023-11-15"),
    ("CUST-1018", "Grace Kim", "grace.kim@seoul-dynamics.kr", "Seoul", "11", "South Korea", "APAC", "Corporate", "2023-12-01"),
    ("CUST-1019", "Noah Anderson", "noah.anderson@cloudops.com", "Atlanta", "GA", "USA", "North America", "Corporate", "2023-12-18"),
    ("CUST-1020", "Zoe Jenkins", "zoe.jenkins@gmail.com", "Miami", "FL", "USA", "North America", "Consumer", "2024-01-08"),
    ("CUST-1021", "Matteo Rossi", "matteo.rossi@milan-design.it", "Milan", "MI", "Italy", "Europe", "Corporate", "2024-01-22"),
    ("CUST-1022", "Charlotte Lee", "charlotte.lee@vancouver-tech.ca", "Vancouver", "BC", "Canada", "North America", "Home Office", "2024-02-14"),
    ("CUST-1023", "Benjamin Scott", "bscott@gmail.com", "Dallas", "TX", "USA", "North America", "Consumer", "2024-02-28"),
    ("CUST-1024", "Amelie Fontana", "amelie.fontana@geneva-finance.ch", "Geneva", "GE", "Switzerland", "Europe", "Corporate", "2024-03-15"),
    ("CUST-1025", "Rajesh Patel", "rpatel@mumbai-tech.in", "Mumbai", "MH", "India", "APAC", "Corporate", "2024-03-30")
]

ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]
ship_mode_weights = [0.55, 0.25, 0.15, 0.05]
payment_methods = ["Credit Card", "PayPal", "Direct Debit", "Apple Pay"]
order_statuses = ["Completed", "Shipped", "Refunded", "Cancelled"]
status_weights = [0.82, 0.12, 0.04, 0.02]

# Generate transactions
start_date = datetime.date(2024, 1, 1)
end_date = datetime.date(2025, 10, 31)
date_range_days = (end_date - start_date).days

clean_rows = []
order_id_counter = 1000

for i in range(1200):
    order_id_counter += 1
    order_id = f"ORD-2024-{order_id_counter}" if order_id_counter < 1600 else f"ORD-2025-{order_id_counter}"
    
    # Date logic (with slight seasonality boost in Q4)
    days_offset = random.randint(0, date_range_days)
    order_date = start_date + datetime.timedelta(days=days_offset)
    
    # Shipping date (1 to 7 days later based on ship mode)
    ship_mode = random.choices(ship_modes, weights=ship_mode_weights)[0]
    if ship_mode == "Same Day":
        ship_delay = 0
    elif ship_mode == "First Class":
        ship_delay = random.randint(1, 2)
    elif ship_mode == "Second Class":
        ship_delay = random.randint(2, 4)
    else:
        ship_delay = random.randint(3, 7)
    ship_date = order_date + datetime.timedelta(days=ship_delay)
    
    # Customer selection
    cust = random.choice(customers_master)
    cust_id, cust_name, email, city, state, country, region, segment, signup_date = cust
    
    # Product selection (1 to 3 items per order, let's keep 1 row per order-item for the main table)
    prod = random.choice(products_master)
    prod_id, prod_name, category, subcat, cost_price, unit_price = prod
    
    # Quantity (corporate buys more)
    if segment == "Corporate":
        quantity = random.choices([1, 2, 3, 4, 5, 8, 10], weights=[0.2, 0.25, 0.25, 0.15, 0.08, 0.04, 0.03])[0]
    elif segment == "Home Office":
        quantity = random.choices([1, 2, 3, 4], weights=[0.4, 0.35, 0.15, 0.1])[0]
    else:
        quantity = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
        
    # Discount (0%, 5%, 10%, 15%, 20%, occasionally 30% for clearances)
    discount_rate = random.choices([0.0, 0.05, 0.10, 0.15, 0.20, 0.30], weights=[0.45, 0.20, 0.15, 0.10, 0.07, 0.03])[0]
    
    gross_sales = round(quantity * unit_price, 2)
    discount_amount = round(gross_sales * discount_rate, 2)
    sales_amount = round(gross_sales - discount_amount, 2)
    total_cost = round(quantity * cost_price, 2)
    profit = round(sales_amount - total_cost, 2)
    profit_margin = round((profit / sales_amount) * 100, 2) if sales_amount > 0 else 0.0
    
    payment = random.choice(payment_methods)
    status = random.choices(order_statuses, weights=status_weights)[0]
    
    clean_rows.append({
        "Order_ID": order_id,
        "Order_Date": order_date.strftime("%Y-%m-%d"),
        "Ship_Date": ship_date.strftime("%Y-%m-%d"),
        "Ship_Mode": ship_mode,
        "Customer_ID": cust_id,
        "Customer_Name": cust_name,
        "Customer_Email": email,
        "Customer_Segment": segment,
        "City": city,
        "State": state,
        "Country": country,
        "Region": region,
        "Product_ID": prod_id,
        "Product_Name": prod_name,
        "Category": category,
        "Subcategory": subcat,
        "Cost_Price": cost_price,
        "Unit_Price": unit_price,
        "Quantity": quantity,
        "Discount_Rate": discount_rate,
        "Sales_Amount": sales_amount,
        "Profit": profit,
        "Profit_Margin_Pct": profit_margin,
        "Payment_Method": payment,
        "Order_Status": status
    })

df_clean = pd.DataFrame(clean_rows)

# Sort clean data chronologically
df_clean = df_clean.sort_values(by="Order_Date").reset_index(drop=True)
df_clean.to_csv("data/cleaned_sales_data.csv", index=False)
print(f"Generated data/cleaned_sales_data.csv with {len(df_clean)} clean records.")

# -------------------------------------------------------------
# Generate Raw Data with Intentional Real-World Imperfections
# -------------------------------------------------------------
df_raw = df_clean.copy()

# 1. Add ~30 Duplicate rows
duplicates = df_raw.sample(n=30, random_state=42)
df_raw = pd.concat([df_raw, duplicates], ignore_index=True)

# 2. Add Missing Values (NaN) in Customer_Email, Customer_Segment, Discount_Rate, Ship_Mode
missing_idx_email = random.sample(range(len(df_raw)), 45)
df_raw.loc[missing_idx_email, "Customer_Email"] = np.nan

missing_idx_seg = random.sample(range(len(df_raw)), 20)
df_raw.loc[missing_idx_seg, "Customer_Segment"] = np.nan

missing_idx_disc = random.sample(range(len(df_raw)), 30)
df_raw.loc[missing_idx_disc, "Discount_Rate"] = np.nan

# 3. Inconsistent Casing & Whitespace in Category / Region / Product_Name
dirty_cat_idx = random.sample(range(len(df_raw)), 40)
for idx in dirty_cat_idx:
    cat = df_raw.loc[idx, "Category"]
    if idx % 3 == 0:
        df_raw.loc[idx, "Category"] = f"  {cat.lower()} "
    elif idx % 3 == 1:
        df_raw.loc[idx, "Category"] = cat.upper()
    else:
        df_raw.loc[idx, "Category"] = cat + "  "

# 4. Inconsistent Date formats (some as DD/MM/YYYY or MM/DD/YYYY)
dirty_date_idx = random.sample(range(len(df_raw)), 35)
for idx in dirty_date_idx:
    d = datetime.datetime.strptime(df_raw.loc[idx, "Order_Date"], "%Y-%m-%d")
    df_raw.loc[idx, "Order_Date"] = d.strftime("%m/%d/%Y")

# 5. Outliers / Data Entry Glitches (e.g., negative quantity, extreme unit price typo)
outlier_idx1 = random.sample(range(len(df_raw)), 3)
for idx in outlier_idx1:
    df_raw.loc[idx, "Quantity"] = -abs(int(df_raw.loc[idx, "Quantity"])) # Negative qty typo

outlier_idx2 = random.sample(range(len(df_raw)), 2)
for idx in outlier_idx2:
    df_raw.loc[idx, "Sales_Amount"] = df_raw.loc[idx, "Sales_Amount"] * 50 # Extreme revenue outlier typo

# Drop calculated profit margin from raw data so analyst has to calculate it
df_raw = df_raw.drop(columns=["Profit_Margin_Pct"])

# Shuffle raw data slightly
df_raw = df_raw.sample(frac=1.0, random_state=99).reset_index(drop=True)
df_raw.to_csv("data/raw_sales_data.csv", index=False)
print(f"Generated data/raw_sales_data.csv with {len(df_raw)} raw records (including anomalies).")

# -------------------------------------------------------------
# Generate Normalized Relational Tables for SQL Practice
# -------------------------------------------------------------
# 1. Customers Table
df_customers = pd.DataFrame(customers_master, columns=[
    "customer_id", "customer_name", "email", "city", "state", "country", "region", "segment", "signup_date"
])
df_customers.to_csv("data/customers.csv", index=False)

# 2. Products Table
df_products = pd.DataFrame(products_master, columns=[
    "product_id", "product_name", "category", "subcategory", "cost_price", "unit_price"
])
df_products.to_csv("data/products.csv", index=False)

# 3. Orders Table
df_orders = df_clean[["Order_ID", "Customer_ID", "Order_Date", "Ship_Date", "Ship_Mode", "Payment_Method", "Order_Status"]].drop_duplicates(subset=["Order_ID"]).copy()
df_orders.columns = ["order_id", "customer_id", "order_date", "ship_date", "ship_mode", "payment_method", "order_status"]
df_orders.to_csv("data/orders.csv", index=False)

# 4. Order_Items Table
df_order_items = df_clean.copy()
df_order_items["order_item_id"] = [f"ITEM-{i+10001}" for i in range(len(df_order_items))]
df_order_items = df_order_items[[
    "order_item_id", "Order_ID", "Product_ID", "Quantity", "Unit_Price", "Discount_Rate", "Sales_Amount", "Profit"
]]
df_order_items.columns = [
    "order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_rate", "sales_amount", "profit"
]
df_order_items.to_csv("data/order_items.csv", index=False)

# -------------------------------------------------------------
# Populate SQLite Database for SQL Practice
# -------------------------------------------------------------
db_path = "02_sql_practice/retail_sales.db"
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
df_customers.to_sql("customers", conn, if_exists="replace", index=False)
df_products.to_sql("products", conn, if_exists="replace", index=False)
df_orders.to_sql("orders", conn, if_exists="replace", index=False)
df_order_items.to_sql("order_items", conn, if_exists="replace", index=False)

# Create indices for realistic querying
cursor = conn.cursor()
cursor.execute("CREATE INDEX idx_orders_customer ON orders(customer_id);")
cursor.execute("CREATE INDEX idx_orders_date ON orders(order_date);")
cursor.execute("CREATE INDEX idx_items_order ON order_items(order_id);")
cursor.execute("CREATE INDEX idx_items_product ON order_items(product_id);")
conn.commit()
conn.close()

print(f"Populated SQLite database '{db_path}' successfully with tables: customers, products, orders, order_items.")

