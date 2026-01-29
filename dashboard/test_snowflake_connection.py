"""
Quick test to verify Snowflake connection works for dashboard
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

print("=" * 60)
print("SNOWFLAKE CONNECTION TEST FOR DASHBOARD")
print("=" * 60)

# Check environment variables
print("\n1. Checking Environment Variables:")
print("-" * 60)

account = os.getenv('SNOWFLAKE_ACCOUNT')
user = os.getenv('SNOWFLAKE_USER')
password = os.getenv('SNOWFLAKE_PASSWORD')
database = os.getenv('SNOWFLAKE_DATABASE', 'BRANDEDSEARCH')
schema = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
role = os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')

print(f"SNOWFLAKE_ACCOUNT: {account}")
print(f"SNOWFLAKE_USER: {user}")
print(f"SNOWFLAKE_PASSWORD: {'*' * len(password) if password else 'NOT SET'}")
print(f"SNOWFLAKE_DATABASE: {database}")
print(f"SNOWFLAKE_SCHEMA: {schema}")
print(f"SNOWFLAKE_WAREHOUSE: {warehouse}")
print(f"SNOWFLAKE_ROLE: {role}")

if not all([account, user, password]):
    print("\n[ERROR] Missing required environment variables!")
    print("\nCreate a .env file in the project root with:")
    print("SNOWFLAKE_ACCOUNT=your_account")
    print("SNOWFLAKE_USER=your_user")
    print("SNOWFLAKE_PASSWORD=your_password")
    print("SNOWFLAKE_DATABASE=BRANDEDSEARCH")
    print("SNOWFLAKE_SCHEMA=PUBLIC")
    print("SNOWFLAKE_WAREHOUSE=COMPUTE_WH")
    exit(1)

    print("\n[OK] All environment variables are set")

# Test connection
print("\n2. Testing Snowflake Connection:")
print("-" * 60)

try:
    from dashboard.snowflake_connector import SnowflakeDashboardConnector
    
    connector = SnowflakeDashboardConnector()
    connector.connect()
    print("[OK] Successfully connected to Snowflake!")
    
    # Test query - check if tables exist
    print("\n3. Checking Tables:")
    print("-" * 60)
    
    tables_query = f"""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = '{schema.upper()}'
    AND table_name IN ('COMPETITORS', 'SOLUTION_CATEGORIES', 'COMPETITOR_KEYWORDS', 'COMPETITOR_METRICS')
    ORDER BY table_name
    """
    
    tables_df = connector.execute_query(tables_query)
    
    if not tables_df.empty:
        print(f"[OK] Found {len(tables_df)} required tables:")
        for table in tables_df['TABLE_NAME']:
            print(f"  - {table}")
    else:
        print("[WARN] No tables found. You may need to run the SQL schema file.")
    
    # Test data query
    print("\n4. Testing Data Queries:")
    print("-" * 60)
    
    # Check competitors
    competitors_df = connector.get_all_competitors()
    if not competitors_df.empty:
        print(f"[OK] Found {len(competitors_df)} competitors:")
        for _, row in competitors_df.iterrows():
            print(f"  - {row['COMPETITOR_NAME']}")
    else:
        print("[WARN] No competitors found in database")
    
    # Check solution categories
    solutions_df = connector.get_solution_categories()
    if not solutions_df.empty:
        print(f"[OK] Found {len(solutions_df)} solution categories:")
        for _, row in solutions_df.iterrows():
            print(f"  - {row['SOLUTION_NAME']} ({row['SOLUTION_KEY']})")
    else:
        print("[WARN] No solution categories found")
    
    # Check competitor metrics
    metrics_df = connector.get_competitor_metrics()
    if not metrics_df.empty:
        print(f"[OK] Found {len(metrics_df)} competitor metric records")
        print(f"  Sample: {metrics_df.iloc[0]['COMPETITOR_NAME']} - {metrics_df.iloc[0]['SOLUTION_NAME']}")
    else:
        print("[WARN] No competitor metrics found. Data may not be loaded yet.")
    
    connector.disconnect()
    print("\n[SUCCESS] Connection test completed successfully!")
    print("\n[DONE] Dashboard is ready to use Snowflake data!")
    
except Exception as e:
    print(f"\n[ERROR] CONNECTION FAILED!")
    print(f"Error: {e}")
    print("\nCommon issues:")
    print("1. Wrong account identifier format")
    print("2. Incorrect username or password")
    print("3. User doesn't have access to the warehouse/database")
    print("4. Network/firewall blocking connection")
    exit(1)

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
