"""
Category & Market Page
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
    page_title="Category & Market - Darktrace CI",
    page_icon="📈",
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
        st.title("Category & Market")
        st.markdown("### Overall Market Trends & Analysis")

st.markdown("---")

# Market Contraction Risk Alerts
st.subheader("Market Contraction Risk Alerts")

col1, col2 = st.columns(2)

with col1:
    st.warning("⚠️ **Network Security Category:** Showing signs of market contraction (-3.2% YoY). Monitor closely for competitive shifts.")

with col2:
    st.info("ℹ️ **Cloud Security Category:** Strong growth trajectory (+18.5% YoY). Market expansion opportunity identified.")

st.markdown("---")

# Overall Market Trends
st.subheader("Overall Market Trends")

# Generate market trend data
dates = pd.date_range(end=pd.Timestamp.now(), periods=24, freq='M')
categories = ['Cloud Security', 'Email Security', 'Network Security']

fig = go.Figure()
colors = ['#FF6B00', '#FF791B', '#FFA52F']

for idx, category in enumerate(categories):
    base = [150000, 120000, 98000][idx]
    values = [base + (i * base * 0.015) + (i % 3) * 2000 for i in range(24)]
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name=category,
        line=dict(color=colors[idx], width=3)
    ))

fig.update_layout(
    height=400,
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis_title="Date",
    yaxis_title="Market Volume",
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Category Performance
st.subheader("Category Performance")

col1, col2, col3 = st.columns(3)

category_stats = [
    {
        'name': 'Cloud Security',
        'volume': 156200,
        'growth': 18.5,
        'share': 34.2,
        'competitors': 4,
        'top': 'Crowdstrike (20.0%)'
    },
    {
        'name': 'Email Security',
        'volume': 121890,
        'growth': 8.3,
        'share': 38.7,
        'competitors': 3,
        'top': 'ProofPoint (18.4%)'
    },
    {
        'name': 'Network Security',
        'volume': 98450,
        'growth': -3.2,
        'share': 29.8,
        'competitors': 3,
        'top': 'VectraAI (12.9%)'
    }
]

for idx, cat in enumerate(category_stats):
    with [col1, col2, col3][idx]:
        st.markdown(f"### ☁️ {cat['name']}" if idx == 0 else 
                    f"### 📧 {cat['name']}" if idx == 1 else
                    f"### 🌐 {cat['name']}")
        st.metric("Total Market Volume", f"{cat['volume']:,.0f}")
        st.metric("YoY Growth", f"{cat['growth']:.1f}%", 
                 delta_color="normal" if cat['growth'] > 0 else "inverse")
        st.metric("Darktrace Share", f"{cat['share']:.1f}%")
        st.metric("Competitors", cat['competitors'])
        st.metric("Top Competitor", cat['top'])

st.markdown("---")

# Difference-in-Differences Analysis
st.subheader("Difference-in-Differences Analysis")

st.info("📊 Comparative Analysis: DiD chart showing treatment vs control groups")

# Placeholder chart
dates_did = pd.date_range(end=pd.Timestamp.now(), periods=12, freq='M')
fig_did = go.Figure()

fig_did.add_trace(go.Scatter(
    x=dates_did,
    y=[100 + i * 2 for i in range(12)],
    mode='lines',
    name='Treatment Group',
    line=dict(color='#FF6B00', width=3)
))

fig_did.add_trace(go.Scatter(
    x=dates_did,
    y=[100 + i * 0.5 for i in range(12)],
    mode='lines',
    name='Control Group',
    line=dict(color='#B6B6B6', width=3)
))

fig_did.update_layout(
    height=300,
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis_title="Date",
    yaxis_title="Index Value"
)

st.plotly_chart(fig_did, use_container_width=True)

st.markdown("---")

# Seasonality Patterns
st.subheader("Seasonality Patterns")

st.info("📅 Seasonal Chart: Monthly patterns and cyclical trends across categories")

# Generate seasonal data
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
seasonal_values = [100 + 10 * abs(6 - i) for i in range(12)]

fig_seasonal = go.Figure()
fig_seasonal.add_trace(go.Bar(
    x=months,
    y=seasonal_values,
    marker_color='#FF6B00'
))

fig_seasonal.update_layout(
    height=300,
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis_title="Month",
    yaxis_title="Search Volume Index"
)

st.plotly_chart(fig_seasonal, use_container_width=True)
