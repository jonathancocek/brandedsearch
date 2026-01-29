"""
Brand Analysis Page
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from dashboard.utils import generate_mock_data
from dashboard.data_loader import DashboardDataLoader
import os

# Page config
st.set_page_config(
    page_title="Brand Analysis - Darktrace CI",
    page_icon="🌍",
    layout="wide"
)

# Load data (real or mock)
@st.cache_data(ttl=3600)
def load_data():
    use_real = os.getenv('SNOWFLAKE_ACCOUNT') is not None
    loader = DashboardDataLoader(use_real_data=use_real)
    return loader.load_all_data()

data = load_data()

# Header
logo_path = Path(__file__).parent.parent.parent / "Logos" / "Darktrace" / "Darktrace_Logo_LightBG_Black.png"
if logo_path.exists():
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(str(logo_path), width=150)
    with col2:
        st.title("Brand Analysis")
        st.markdown("### Geographic Distribution & Regional Momentum")

st.markdown("---")

# Geographic Distribution
st.subheader("Geographic Distribution")

# Create a simple map visualization placeholder
col1, col2, col3, col4 = st.columns(4)

regions = data['regional']
for i, region in enumerate(regions.iterrows()):
    with [col1, col2, col3, col4][i]:
        st.metric(
            label=region[1]['region'],
            value=f"{region[1]['total_volume']:,.0f}",
            delta=f"{region[1]['growth_pct']:.1f}%"
        )

st.markdown("---")

# Country-Level Breakdowns
st.subheader("Country-Level Breakdowns")

regional_df = data['regional']

for idx, row in regional_df.iterrows():
    with st.expander(f"🇺🇸 {row['region']}" if idx == 0 else 
                     f"🇬🇧 {row['region']}" if idx == 1 else
                     f"🇩🇪 {row['region']}" if idx == 2 else
                     f"🇦🇺 {row['region']}"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Volume", f"{row['total_volume']:,.0f}")
        with col2:
            st.metric("Market Share", f"{row['market_share']:.1f}%")
        with col3:
            st.metric("Growth (QoQ)", f"{row['growth_pct']:.1f}%")
        with col4:
            status = "Strong" if row['growth_pct'] > 10 else "Moderate" if row['growth_pct'] > 0 else "Weak"
            st.metric("Status", status)

st.markdown("---")

# Regional Momentum Tracking
st.subheader("Regional Momentum Tracking")

# Generate time series for regions
dates = pd.date_range(end=pd.Timestamp.now(), periods=12, freq='M')
fig = go.Figure()

colors = ['#FF6B00', '#FF791B', '#FFA52F', '#E66203']
for idx, region in enumerate(regions.iterrows()):
    base = region[1]['total_volume']
    values = [base + (i * base * 0.02) for i in range(12)]
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name=region[1]['region'],
        line=dict(color=colors[idx % len(colors)], width=2)
    ))

fig.update_layout(
    height=400,
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis_title="Date",
    yaxis_title="Search Volume",
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)
