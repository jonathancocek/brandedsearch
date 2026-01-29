# Darktrace Competitor Intelligence Dashboard

## Quick Start

### 1. Set up SEMRush API Key (Optional)

To use real SEMRush data, set your API key as an environment variable:

**Windows PowerShell:**
```powershell
$env:SEMRUSH_API_KEY="your_api_key_here"
```

**Windows Command Prompt:**
```cmd
set SEMRUSH_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export SEMRUSH_API_KEY="your_api_key_here"
```

If no API key is set, the dashboard will use mock data for demonstration.

### 2. Run the Dashboard

```bash
python -m streamlit run dashboard/app.py --server.port 8502
```

The dashboard will be available at: **http://localhost:8502**

### 3. Access Pages

- **Overview Dashboard** - Key metrics and trends
- **Brand Analysis** - Geographic distribution
- **Competitor Analysis** - Multi-competitor comparison
- **Category & Market** - Market trends
- **Keywords** - Keyword tracking

## Features

- ✅ Real-time SEMRush API integration
- ✅ Fallback to mock data if API unavailable
- ✅ Darktrace brand colors and logo
- ✅ Interactive Plotly charts
- ✅ Responsive design

## Troubleshooting

**Port already in use:**
- Use a different port: `--server.port 8503`
- Or kill the process using the port

**API Key Issues:**
- Check that SEMRUSH_API_KEY is set correctly
- Dashboard will automatically use mock data if API fails
