"""
Overview Dashboard Page
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys
import os

sys.path.append(str(Path(__file__).parent.parent.parent))
from dashboard.utils import generate_mock_data, format_number
from dashboard.data_loader import DashboardDataLoader

# Page config
st.set_page_config(
    page_title="Overview Dashboard - Darktrace CI",
    page_icon="📊",
    layout="wide"
)

# Load environment variables explicitly
from dotenv import load_dotenv
from pathlib import Path
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Load data (real or mock)
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    use_real = os.getenv('SNOWFLAKE_ACCOUNT') is not None
    loader = DashboardDataLoader(use_real_data=use_real)
    return loader.load_all_data()

data = load_data()

# Show data source indicator with connection test
try:
    test_loader = DashboardDataLoader(use_real_data=True)
    if test_loader.use_real_data and test_loader.snowflake_connector:
        st.sidebar.success("✅ Connected to Snowflake")
        st.sidebar.caption("Using real-time data")
    else:
        st.sidebar.warning("⚠️ Using Mock Data")
        st.sidebar.caption("Snowflake connection failed")
        with st.sidebar.expander("Debug Info"):
            st.write(f"Account: {os.getenv('SNOWFLAKE_ACCOUNT', 'Not set')}")
            st.write(f"User: {os.getenv('SNOWFLAKE_USER', 'Not set')}")
            st.write(f"Has Password: {bool(os.getenv('SNOWFLAKE_PASSWORD'))}")
except Exception as e:
    st.sidebar.error(f"❌ Connection Error: {str(e)}")
    st.sidebar.caption("Check terminal for details")

# Header
logo_path = Path(__file__).parent.parent.parent / "Logos" / "Darktrace" / "Darktrace_Logo_LightBG_Black.png"
if logo_path.exists():
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(str(logo_path), width=150)
    with col2:
        st.title("Darktrace Competitor Intelligence")
        st.markdown("### Overview Dashboard")

st.markdown("---")

# Key Metrics
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Brand Growth",
        value="+12.5%",
        delta="vs last quarter",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="Share of Search",
        value="34.2%",
        delta="+2.1% vs last month",
        delta_color="normal"
    )

with col3:
    st.metric(
        label="Category Health",
        value="8.2/10",
        delta="Strong across all categories",
        delta_color="normal"
    )

with col4:
    st.metric(
        label="Total Keywords Tracked",
        value="195",
        delta="13 competitors × 15 keywords"
    )

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Brand Volume Trend (Last 12 Months)")
    
    # Generate sample trend data
    dates = pd.date_range(end=pd.Timestamp.now(), periods=12, freq='M')
    volumes = [45000 + i * 500 + (i % 3) * 1000 for i in range(12)]
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=dates,
        y=volumes,
        fill='tonexty',
        mode='lines',
        name='Brand Volume',
        line=dict(color='#FF6B00', width=3),
        fillcolor='rgba(255, 107, 0, 0.2)'
    ))
    fig_trend.update_layout(
        height=300,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="Date",
        yaxis_title="Search Volume",
        showlegend=False
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.subheader("Share of Search")
    
    # Generate share data
    share_data = {
        'Darktrace': 34.2,
        'Competitors': 65.8
    }
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=list(share_data.keys()),
        values=list(share_data.values()),
        hole=0.5,
        marker_colors=['#FF6B00', '#B6B6B6']
    )])
    fig_donut.update_layout(
        height=300,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

# Regional Performance Table
st.subheader("Regional Performance Summary")

regional_df = data['regional']
st.dataframe(
    regional_df.style.format({
        'total_volume': '{:,.0f}',
        'growth_pct': '{:.1f}%',
        'market_share': '{:.1f}%'
    }),
    use_container_width=True,
    hide_index=True
)
