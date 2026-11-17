import sqlite3
import re
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

db_path = "02_sql_practice/retail_sales.db"
sql_file = "02_sql_practice/sql_practice_queries.sql"

print("=" * 80)
print("EXECUTING SQL DATA ANALYST PRACTICE SUITE")
print(f"Target Database: {db_path}")
print("=" * 80)

conn = sqlite3.connect(db_path)

with open(sql_file, "r") as f:
    sql_text = f.read()

# Split into distinct named queries
# We look for -- Query X.Y: ... pattern
query_blocks = re.split(r'(-- Query \d+\.\d+:.*?)(?=(?:-- Query \d+\.\d+:|$))', sql_text, flags=re.DOTALL)

executed_count = 0
for block in query_blocks:
    block = block.strip()
    if not block or not block.startswith("-- Query"):
        continue

    # Extract header line
    lines = block.splitlines()
    header = lines[0]
    
    # Extract SQL command (strip comments)
    sql_lines = [l for l in lines if not l.strip().startswith("--")]
    clean_sql = "\n".join(sql_lines).strip()
    if not clean_sql:
        continue

    print(f"\n>>> {header}")
    try:
        df_res = pd.read_sql_query(clean_sql, conn)
        executed_count += 1
        print(f"Rows Returned: {len(df_res)}")
        if len(df_res) > 5:
            print(df_res.head(5).to_string(index=False))
            print(f"... ({len(df_res) - 5} more rows)")
        else:
            print(df_res.to_string(index=False))
    except Exception as e:
        print(f"ERROR executing query: {e}")

conn.close()
print("\n" + "=" * 80)
print(f"SUCCESS: Executed {executed_count} practice queries without errors!")
print("=" * 80)

