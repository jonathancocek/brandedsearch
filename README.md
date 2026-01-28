# 🎯 Darktrace Competitor Intelligence Dashboard

A comprehensive competitor intelligence system that tracks branded keywords across multiple solution categories using SEMRush data and presents insights through an interactive Streamlit dashboard.

## 📊 Overview

This system provides:
- **15 branded keywords per competitor** across 3 solution categories (Cloud, Email, Network Security)
- **Real-time competitive tracking** with momentum indicators
- **Storybook-inspired UI** with clean, professional design
- **Snowflake data warehouse** for historical trending
- **Automated daily refresh** from SEMRush API

### Solution Categories

**Cloud Security**
- Competitors: Wiz, Orca, Crowdstrike, Palo Alto Cortex Cloud

**Email Security**
- Competitors: Abnormal, ProofPoint, Mimecast

**Network Security**
- Competitors: VectraAI, ExtraHop, CoreLight

**Total**: 195 branded keywords tracked (15 keywords × 13 competitors)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- SEMRush API key
- Snowflake account access
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/transmission-agency/darktrace-competitor-intelligence.git
cd darktrace-competitor-intelligence

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

1. **Edit `.env`** with your API keys and Snowflake credentials
2. **Review `config/clients/darktrace.yaml`** to customize:
   - Competitors
   - Semantic indicators
   - Geographic regions
   - Refresh schedule

---

## 📁 Project Structure

```
darktrace-competitor-intelligence/
│
├── config/
│   └── clients/
│       └── darktrace.yaml          # Client configuration
│
├── data_pipeline/
│   ├── semrush_connector.py        # SEMRush API wrapper
│   ├── pipeline.py                 # Main orchestrator
│   ├── snowflake_loader.py         # Snowflake data loader
│   └── scheduler.py                # Automated scheduling
│
├── dashboard/
│   ├── app.py                      # Main Streamlit app
│   ├── pages/
│   │   ├── 01_dashboard.py         # Overview
│   │   ├── 02_brand_analysis.py
│   │   ├── 03_competitor_analysis.py
│   │   ├── 04_category_market.py
│   │   └── 05_keywords.py
│   ├── components/
│   │   ├── charts.py               # Reusable charts
│   │   ├── filters.py              # Filter components
│   │   └── metrics.py              # Metric cards
│   └── styles/
│       └── custom.css              # Storybook theme
│
├── sql/
│   ├── schema/
│   │   └── competitor_intelligence.sql
│   └── queries/
│       └── trending_analysis.sql
│
├── tests/
│   └── test_pipeline.py
│
├── .env.example                    # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔧 Usage

### 1. Run Data Pipeline (First Time)

```bash
python data_pipeline/pipeline.py
```

This will:
- Fetch branded keywords from SEMRush for all competitors
- Classify keywords by solution category
- Calculate metrics and momentum
- Load data to Snowflake

Expected runtime: ~10-15 minutes for first run

### 2. Launch Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

### 3. Schedule Automated Refreshes

```bash
python data_pipeline/scheduler.py
```

Runs daily at 2:00 AM UTC (configurable in `.env`)

---

## 📊 Dashboard Pages

### 1. **Overview Dashboard**
- Key metrics cards (Brand Growth, Share of Search, Category Health)
- Trend charts
- Regional performance summary

### 2. **Brand Analysis**
- Geographic distribution
- Country-level breakdowns
- Regional momentum tracking

### 3. **Competitor Analysis** ⭐
- Multi-competitor comparison charts
- Share of search donut chart
- Competitor momentum tracker with sparklines
- Filterable by solution category

### 4. **Category & Market**
- Overall market trends
- Difference-in-Differences analysis
- Seasonality patterns
- Market contraction risk alerts

### 5. **Keywords**
- Top 15 keywords per competitor/solution
- Keyword momentum tracker
- Trend sparklines
- Search and sort functionality

---

## 🗄️ Database Schema

### Tables

**`COMPETITOR_KEYWORDS`**
```sql
- keyword_id (PK)
- keyword
- competitor_name
- solution_category
- volume
- position
- trend
- fetch_date
- database (region)
```

**`COMPETITOR_METRICS`**
```sql
- metric_id (PK)
- solution_category
- competitor_name
- total_volume
- avg_volume
- keyword_count
- share_of_search
- momentum_pct
- calculation_date
```

**`KEYWORD_HISTORY`**
```sql
- history_id (PK)
- keyword
- competitor_name
- solution_category
- volume
- date
```

---

## 🎨 Customization

### Adding a New Client

1. **Create config file**: `config/clients/new_client.yaml`
2. **Define solution categories** and competitors
3. **Add semantic indicators** for keyword classification
4. **Run pipeline** with new config

### Modifying Storybook Theme

Edit `dashboard/styles/custom.css`:
- Primary color: `#4CAF50` (green)
- Sidebar color: `#1e4d3c` (dark green)
- Accent colors for charts

### Adjusting Keyword Limits

In `darktrace.yaml`:
```yaml
max_keywords_per_competitor: 15  # Change this value
```

---

## 🔐 Security Best Practices

1. **Never commit `.env`** to version control
2. **Use read-only Snowflake role** for dashboard
3. **Rotate API keys** regularly
4. **Enable MFA** on Snowflake account
5. **Review `semantic_indicators`** to avoid capturing sensitive keywords

---

## 📈 Roadmap

### Phase 1: Foundation ✅
- [x] SEMRush API connector
- [x] Keyword classification engine
- [x] Snowflake schema
- [x] Basic data pipeline

### Phase 2: Dashboard (In Progress)
- [ ] Streamlit UI with Storybook theme
- [ ] Interactive charts (Plotly)
- [ ] Filter and date range controls
- [ ] Export functionality

### Phase 3: Advanced Features
- [ ] Predictive trend analysis
- [ ] Automated insights (Claude API)
- [ ] Email alerts for significant changes
- [ ] Multi-region comparison
- [ ] Custom report generation

### Phase 4: Scalability
- [ ] Multi-client support
- [ ] API endpoint for programmatic access
- [ ] Real-time updates
- [ ] Mobile-responsive dashboard

---

## 🐛 Troubleshooting

### SEMRush API Errors

**Issue**: `401 Unauthorized`
- Check API key in `.env`
- Verify API key is active in SEMRush dashboard

**Issue**: `Too Many Requests`
- SEMRush has rate limits (10 requests/second)
- Pipeline includes built-in delays
- Consider upgrading SEMRush plan

### Snowflake Connection Issues

**Issue**: `Connection refused`
- Verify Snowflake account URL format
- Check firewall/network settings
- Ensure IP is whitelisted in Snowflake

**Issue**: `Insufficient privileges`
- Grant necessary permissions to role
- Check database and schema access

### Dashboard Not Loading

**Issue**: `Module not found`
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Issue**: `Port already in use`
- Change port in `.env`: `DASHBOARD_PORT=8502`
- Or stop existing Streamlit process

---

## 📞 Support

**Technical Lead**: Jonathan Cocek  
**Email**: jonathan.cocek@transmissionagency.com  
**Team**: Transmission Agency - Data & Analytics

**GitHub Issues**: https://github.com/transmission-agency/darktrace-competitor-intelligence/issues

---

## 📄 License

Copyright © 2026 Transmission Agency  
All Rights Reserved

This project is proprietary and confidential. Unauthorized copying, modification, or distribution is prohibited.

---

## 🙏 Acknowledgments

- **Storybook Marketing** - Dashboard design inspiration
- **SEMRush** - Keyword data provider
- **Snowflake** - Data warehouse platform
- **Streamlit** - Dashboard framework

---

**Last Updated**: January 28, 2026  
**Version**: 1.0.0
