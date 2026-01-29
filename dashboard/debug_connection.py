"""
Debug script to test Snowflake connection from dashboard context
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env file
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Loaded .env from {env_path}")
else:
    print(f"[WARN] No .env file found at {env_path}")
    # Try loading from current directory
    load_dotenv()

print("\n" + "=" * 60)
print("SNOWFLAKE CONNECTION DEBUG")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables:")
print("-" * 60)
account = os.getenv('SNOWFLAKE_ACCOUNT')
user = os.getenv('SNOWFLAKE_USER')
password = os.getenv('SNOWFLAKE_PASSWORD')
database = os.getenv('SNOWFLAKE_DATABASE', 'BRANDEDSEARCH')
schema = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')

print(f"SNOWFLAKE_ACCOUNT: {account}")
print(f"SNOWFLAKE_USER: {user}")
print(f"SNOWFLAKE_PASSWORD: {'SET' if password else 'NOT SET'}")
print(f"SNOWFLAKE_DATABASE: {database}")
print(f"SNOWFLAKE_SCHEMA: {schema}")
print(f"SNOWFLAKE_WAREHOUSE: {warehouse}")

if not all([account, user, password]):
    print("\n[ERROR] Missing required credentials!")
    exit(1)

# Test Snowflake connector import
print("\n2. Testing Imports:")
print("-" * 60)
try:
    from dashboard.snowflake_connector import SnowflakeDashboardConnector
    print("[OK] SnowflakeDashboardConnector imported")
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test connection
print("\n3. Testing Connection:")
print("-" * 60)
try:
    connector = SnowflakeDashboardConnector()
    print("[OK] Connector created")
    
    connector.connect()
    print("[OK] Connected to Snowflake!")
    
    # Test query
    test_df = connector.execute_query("SELECT CURRENT_VERSION() as version")
    if not test_df.empty:
        print(f"[OK] Test query successful: {test_df.iloc[0]['VERSION']}")
    
    # Check tables
    tables_query = f"""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = '{schema.upper()}'
    AND table_name IN ('COMPETITORS', 'SOLUTION_CATEGORIES', 'COMPETITOR_KEYWORDS', 'COMPETITOR_METRICS')
    ORDER BY table_name
    """
    tables_df = connector.execute_query(tables_query)
    print(f"[OK] Found {len(tables_df)} tables")
    
    connector.disconnect()
    print("\n[SUCCESS] All tests passed!")
    
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
