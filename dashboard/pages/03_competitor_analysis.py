"""
Competitor Analysis Page
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from dashboard.utils import generate_mock_data, get_status_badge
from dashboard.data_loader import DashboardDataLoader
import os

# Page config
st.set_page_config(
    page_title="Competitor Analysis - Darktrace CI",
    page_icon="🏢",
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
        st.title("Competitor Analysis")
        st.markdown("### Multi-competitor Comparison & Share of Search")

st.markdown("---")

# Filters
col1, col2 = st.columns(2)

with col1:
    solution_categories = ['All Categories', 'cloud', 'email', 'network']
    selected_category = st.selectbox("Solution Category", solution_categories)

with col2:
    regions = ['United States', 'United Kingdom', 'Germany', 'Australia']
    selected_region = st.selectbox("Region", regions)

# Filter data by solution category
if selected_category == 'All Categories':
    filtered_metrics = data['competitor_metrics']
else:
    # Load filtered data from loader
    loader = DashboardDataLoader(use_real_data=os.getenv('SNOWFLAKE_ACCOUNT') is not None)
    filtered_metrics = loader.load_competitor_metrics(solution_category=selected_category)

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Multi-Competitor Comparison")
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=filtered_metrics['competitor'],
        y=filtered_metrics['total_volume'],
        marker_color='#FF6B00',
        text=filtered_metrics['total_volume'],
        textposition='auto'
    ))
    fig_bar.update_layout(
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="Competitor",
        yaxis_title="Total Volume",
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("Share of Search")
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=filtered_metrics['competitor'],
        values=filtered_metrics['share_of_search'],
        hole=0.4,
        marker_colors=px.colors.qualitative.Set3
    )])
    fig_pie.update_layout(
        height=350,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# Competitor Momentum Tracker
st.subheader("Competitor Momentum Tracker")

# Display table with metrics
display_df = filtered_metrics[['competitor', 'category', 'total_volume', 'share_of_search', 'momentum_pct']].copy()
display_df['status'] = display_df['momentum_pct'].apply(get_status_badge)
display_df = display_df.sort_values('momentum_pct', ascending=False)

st.dataframe(
    display_df.style.format({
        'total_volume': '{:,.0f}',
        'share_of_search': '{:.1f}%',
        'momentum_pct': '{:.1f}%'
    }),
    use_container_width=True,
    hide_index=True
)
