"""
Simple Snowflake Connection Test
Diagnoses the exact connection issue
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("SNOWFLAKE CONNECTION DIAGNOSTIC")
print("=" * 60)

# Step 1: Check environment variables
print("\n1. Checking Environment Variables:")
print("-" * 60)

account = os.getenv('SNOWFLAKE_ACCOUNT')
user = os.getenv('SNOWFLAKE_USER')
password = os.getenv('SNOWFLAKE_PASSWORD')
database = os.getenv('SNOWFLAKE_DATABASE')
schema = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
role = os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')

print(f"SNOWFLAKE_ACCOUNT: {account}")
print(f"SNOWFLAKE_USER: {user}")
print(f"SNOWFLAKE_PASSWORD: {'*' * len(password) if password else 'NOT SET'}")
print(f"SNOWFLAKE_DATABASE: {database}")
print(f"SNOWFLAKE_SCHEMA: {schema}")
print(f"SNOWFLAKE_WAREHOUSE: {warehouse}")
print(f"SNOWFLAKE_ROLE: {role}")

if not all([account, user, password, database, warehouse]):
    print("\n❌ ERROR: Missing required environment variables!")
    print("Make sure all variables are set in .env file")
    exit(1)

print("\n✓ All environment variables are set")

# Step 2: Check if snowflake-connector-python is installed
print("\n2. Checking Snowflake Package:")
print("-" * 60)

try:
    import snowflake.connector
    print("✓ snowflake-connector-python is installed")
except ImportError:
    print("❌ ERROR: snowflake-connector-python not installed")
    print("Run: pip install snowflake-connector-python")
    exit(1)

# Step 3: Test basic connection
print("\n3. Testing Snowflake Connection:")
print("-" * 60)

try:
    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        role=role
    )
    
    print("✓ Successfully connected to Snowflake!")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION()")
    version = cursor.fetchone()[0]
    print(f"✓ Snowflake Version: {version}")
    
    cursor.close()
    
except Exception as e:
    print(f"❌ CONNECTION FAILED!")
    print(f"Error: {e}")
    print("\nCommon issues:")
    print("1. Wrong account identifier (should be like: ZGKGIH-ISA98947)")
    print("2. Incorrect username or password")
    print("3. User doesn't have access to the warehouse")
    print("4. Network/firewall blocking connection")
    conn = None
    exit(1)

# Step 4: Test database access
print("\n4. Testing Database Access:")
print("-" * 60)

try:
    cursor = conn.cursor()
    cursor.execute(f"USE DATABASE {database}")
    print(f"✓ Successfully accessed database: {database}")
    
    cursor.execute(f"USE SCHEMA {schema}")
    print(f"✓ Successfully accessed schema: {schema}")
    
    cursor.close()
    
except Exception as e:
    print(f"❌ DATABASE ACCESS FAILED!")
    print(f"Error: {e}")
    print(f"\nMake sure database '{database}' exists and user has access")
    exit(1)

# Step 5: Check tables
print("\n5. Checking Tables:")
print("-" * 60)

try:
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{schema}'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    
    if tables:
        print(f"✓ Found {len(tables)} tables:")
        for table in tables:
            print(f"  • {table[0]}")
    else:
        print("⚠ No tables found in schema")
        print("You may need to run the SQL schema file")
    
    cursor.close()
    
except Exception as e:
    print(f"❌ ERROR checking tables: {e}")

# Step 6: Check seed data
print("\n6. Checking Seed Data:")
print("-" * 60)

try:
    cursor = conn.cursor()
    
    # Check competitors
    cursor.execute("SELECT COUNT(*) FROM COMPETITORS")
    competitor_count = cursor.fetchone()[0]
    print(f"✓ Competitors: {competitor_count}")
    
    # Check solutions
    cursor.execute("SELECT COUNT(*) FROM SOLUTION_CATEGORIES")
    solution_count = cursor.fetchone()[0]
    print(f"✓ Solutions: {solution_count}")
    
    cursor.close()
    
except Exception as e:
    print(f"⚠ Could not check seed data: {e}")
    print("Tables might not exist yet")

# Close connection
if conn:
    conn.close()
    print("\n✓ Connection closed")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
print("\nIf all tests passed, your Snowflake connection is working!")
print("If any tests failed, check the error messages above.")
