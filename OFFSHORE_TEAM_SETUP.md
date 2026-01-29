# Branded Search Dashboard - Setup Guide for Offshore Team

## Repository Information

**Repository Name**: `brandedsearch`  
**GitHub URL**: `https://github.com/jonathancocek/brandedsearch.git`  
**Branch**: `main`  
**Latest Commit**: `b57a2af`

## Project Overview

This is a **Streamlit dashboard** for Darktrace competitive intelligence, pulling data from Snowflake tables that are populated by monthly SEMRush API runs.

### Key Components

1. **Streamlit Dashboard** (`dashboard/`)
   - 5 pages: Dashboard, Brand Analysis, Competitor Analysis, Category Market, Keywords
   - Darktrace branding (colors, logo)
   - Solution category filters (cloud, email, network)
   - Snowflake integration with mock data fallback

2. **Data Pipeline** (`data_pipeline/`)
   - SEMRush API connector
   - Snowflake loader
   - Monthly scheduler

3. **Configuration** (`config/clients/darktrace.yaml`)
   - Competitor definitions
   - Solution categories
   - Keyword classification rules

## Quick Start

### Prerequisites

- **Python 3.11 or 3.12** (⚠️ NOT Python 3.14 - see compatibility issue below)
- Git
- Access to Snowflake database: `BRANDEDSEARCH.PUBLIC`

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jonathancocek/brandedsearch.git
   cd brandedsearch
   ```

2. **Create virtual environment** (Python 3.11 or 3.12):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install "snowflake-connector-python<4.0" --only-binary :all:
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_user
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_DATABASE=BRANDEDSEARCH
   SNOWFLAKE_SCHEMA=PUBLIC
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_ROLE=ACCOUNTADMIN
   
   SEMRUSH_API_KEY=your_semrush_api_key
   ```

5. **Run the dashboard**:
   ```bash
   streamlit run dashboard/app.py --server.port 8502
   ```

6. **Access dashboard**: Open `http://localhost:8502` in your browser

## Important Notes

### ⚠️ Python Version Compatibility

**CRITICAL**: The Snowflake connector does NOT support Python 3.14 yet. Use Python 3.11 or 3.12.

If you see "Mock Data Mode" in the dashboard:
- Check Python version: `python --version`
- If Python 3.14, install Python 3.11 or 3.12
- See `PYTHON_VERSION_ISSUE.md` for details

### Data Flow

```
Monthly Pipeline → SEMRush API → Snowflake Tables → Dashboard
```

The dashboard reads from these Snowflake tables:
- `COMPETITORS` - List of competitors
- `SOLUTION_CATEGORIES` - Solution types (cloud, email, network)
- `COMPETITOR_KEYWORDS` - Keywords for each competitor/solution
- `COMPETITOR_METRICS` - Metrics (volume, share of search, momentum)

### Mock Data Mode

If Snowflake connection fails, the dashboard automatically uses realistic mock data. This is perfect for:
- Development
- Testing
- Demos

The mock data accurately represents the structure of real data.

## Project Structure

```
brandedsearch/
├── dashboard/              # Streamlit dashboard
│   ├── app.py            # Main app entry point
│   ├── pages/            # Dashboard pages
│   ├── snowflake_connector.py  # Snowflake connection
│   └── data_loader.py    # Data loading logic
├── data_pipeline/        # ETL pipeline
│   ├── semrush_connector.py
│   ├── pipeline.py
│   └── snowflake_loader.py
├── config/               # Configuration files
│   └── clients/
│       └── darktrace.yaml
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (NOT in git)
```

## Testing

Run tests:
```bash
python -m pytest tests/
```

Test Snowflake connection:
```bash
python dashboard/debug_connection.py
```

## Dashboard Pages

1. **Dashboard** (`/`) - Overview metrics
2. **Brand Analysis** (`/brand-analysis`) - Darktrace brand performance
3. **Competitor Analysis** (`/competitor-analysis`) - Competitive comparison
4. **Category Market** (`/category-market`) - Market by solution category
5. **Keywords** (`/keywords`) - Keyword analysis

## Filters

All pages support filtering by:
- **Solution Category**: Cloud Security, Email Security, Network Security
- **Competitor**: Any of the 11 competitors

## Competitors

- **Cloud Security**: Wiz, Orca, Crowdstrike, Palo Alto Cortex Cloud
- **Email Security**: Abnormal, ProofPoint, Mimecast
- **Network Security**: VectraAI, ExtraHop, CoreLight
- **Client**: Darktrace (appears in all categories)

## Troubleshooting

### Dashboard shows "Mock Data Mode"
- Check Python version (must be 3.11 or 3.12)
- Verify `.env` file exists with Snowflake credentials
- Check terminal for connection errors
- Run `python dashboard/debug_connection.py` for diagnostics

### Port already in use
- Change port: `streamlit run dashboard/app.py --server.port 8503`
- Or kill process using port 8502

### Import errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version compatibility

## Next Steps

1. **Set up Snowflake credentials** in `.env` file
2. **Verify Snowflake tables** have data:
   ```sql
   SELECT COUNT(*) FROM COMPETITOR_KEYWORDS;
   SELECT COUNT(*) FROM COMPETITOR_METRICS;
   ```
3. **Run dashboard** and verify connection
4. **Test filters** on each page
5. **Schedule monthly pipeline** to populate Snowflake tables

## Support

- See `NEXT_STEPS.md` for detailed setup
- See `PYTHON_VERSION_ISSUE.md` for Python compatibility
- Check `dashboard/README.md` for dashboard-specific docs

## Contact

For questions or issues, contact: [Your Contact Info]

---

**Last Updated**: [Current Date]  
**Repository**: https://github.com/jonathancocek/brandedsearch
