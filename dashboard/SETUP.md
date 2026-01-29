# Dashboard Setup Guide

## Architecture Overview

The dashboard is now configured to pull data from **Snowflake tables** that are populated monthly by the SEMRush API pipeline.

### Data Flow:
1. **Monthly Pipeline** → Runs SEMRush API → Populates Snowflake tables
2. **Dashboard** → Reads from Snowflake → Displays visualizations

## Current Status

✅ **Dashboard Structure Complete**
- All 5 pages created (Overview, Brand Analysis, Competitor Analysis, Category & Market, Keywords)
- Snowflake connector created (`dashboard/snowflake_connector.py`)
- Data loader updated to use Snowflake (`dashboard/data_loader.py`)
- Filters configured for solution categories (cloud, email, network)
- All competitors properly associated with their categories

⚠️ **Snowflake Connector Installation**
- The `snowflake-connector-python` package failed to build (compilation issue)
- Dashboard currently uses mock data
- Once Snowflake is accessible, the dashboard will automatically switch to real data

## Setting Up Snowflake Connection

### 1. Install Snowflake Connector

Try installing a pre-built wheel:
```bash
pip install snowflake-connector-python --only-binary :all:
```

Or use a different version:
```bash
pip install "snowflake-connector-python<4.0"
```

### 2. Set Environment Variables

Create a `.env` file in the project root:
```env
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=BRANDEDSEARCH
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

### 3. Verify Snowflake Tables

Make sure these tables exist in Snowflake:
- `COMPETITORS` - List of all competitors
- `SOLUTION_CATEGORIES` - Cloud, Email, Network Security categories
- `COMPETITOR_KEYWORDS` - Keywords for each competitor/solution
- `COMPETITOR_METRICS` - Aggregated metrics per competitor/solution
- `KEYWORD_HISTORY` - Historical keyword data
- `CATEGORY_METRICS` - Category-level metrics

## Dashboard Features

### Solution Category Filters
All pages support filtering by:
- **cloud** - Cloud Security
- **email** - Email Security  
- **network** - Network Security

### Competitor Associations
Each competitor is properly associated with their solution categories:
- **Cloud Security**: Wiz, Orca, Crowdstrike, Palo Alto Cortex Cloud
- **Email Security**: Abnormal, ProofPoint, Mimecast
- **Network Security**: VectraAI, ExtraHop, CoreLight

### Pages

1. **Overview Dashboard** - Key metrics, trends, regional summary
2. **Brand Analysis** - Geographic distribution, country breakdowns
3. **Competitor Analysis** - Multi-competitor comparison with filters
4. **Category & Market** - Market trends, category performance
5. **Keywords** - Top keywords per competitor/solution with filters

## Running the Dashboard

```bash
python -m streamlit run dashboard/app.py --server.port 8502
```

Access at: **http://localhost:8502**

## Next Steps

1. **Fix Snowflake Connector Installation** - Resolve compilation issues or use pre-built wheels
2. **Run Monthly Pipeline** - Ensure Snowflake tables are populated with latest data
3. **Test Dashboard** - Verify all filters work correctly with real Snowflake data
4. **Verify All Competitors** - Ensure all 11 competitors appear in visualizations

## Troubleshooting

**Dashboard shows mock data:**
- Check if Snowflake credentials are set in environment
- Verify Snowflake connector is installed
- Check connection logs in dashboard sidebar

**Filters not working:**
- Ensure solution_category filter uses keys: 'cloud', 'email', 'network'
- Check that Snowflake tables have proper solution_id associations

**Missing competitors:**
- Verify COMPETITOR_KEYWORDS table has data for all competitors
- Check COMPETITOR_METRICS table has latest calculation_date
