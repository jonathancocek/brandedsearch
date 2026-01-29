"""
Keywords Page
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from dashboard.utils import generate_mock_data, get_status_badge
from dashboard.data_loader import DashboardDataLoader
import os

# Page config
st.set_page_config(
    page_title="Keywords - Darktrace CI",
    page_icon="🔑",
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
        st.title("Keywords")
        st.markdown("### Top 15 Keywords per Competitor & Solution")

st.markdown("---")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    competitors = ['All Competitors'] + list(data['keywords']['competitor'].unique())
    selected_competitor = st.selectbox("Competitor", competitors)

with col2:
    solution_categories = ['All Categories', 'cloud', 'email', 'network']
    selected_category = st.selectbox("Category", solution_categories)

with col3:
    search_term = st.text_input("Search Keywords", "")

# Filter data - reload with filters if needed
if selected_category != 'All Categories' or selected_competitor != 'All Competitors':
    loader = DashboardDataLoader(use_real_data=os.getenv('SNOWFLAKE_ACCOUNT') is not None)
    filtered_keywords = loader.load_keywords(
        competitor=selected_competitor if selected_competitor != 'All Competitors' else None,
        solution_category=selected_category if selected_category != 'All Categories' else None
    )
else:
    filtered_keywords = data['keywords'].copy()

if search_term:
    filtered_keywords = filtered_keywords[
        filtered_keywords['keyword'].str.contains(search_term, case=False)
    ]

# Add status column
filtered_keywords['status'] = filtered_keywords['momentum'].apply(get_status_badge)

st.markdown("---")

# Keyword Momentum Tracker
st.subheader("Keyword Momentum Tracker")

# Display table
display_cols = ['keyword', 'competitor', 'category', 'volume', 'position', 'momentum', 'status']
display_df = filtered_keywords[display_cols].copy()
display_df = display_df.sort_values('momentum', ascending=False)

st.dataframe(
    display_df.style.format({
        'volume': '{:,.0f}',
        'position': '{:.1f}',
        'momentum': '{:.1f}%'
    }),
    use_container_width=True,
    hide_index=True,
    column_config={
        'keyword': 'Keyword',
        'competitor': 'Competitor',
        'category': 'Category',
        'volume': 'Volume',
        'position': 'Position',
        'momentum': 'Momentum',
        'status': 'Status'
    }
)

# Summary stats
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Keywords", len(filtered_keywords))

with col2:
    avg_momentum = filtered_keywords['momentum'].mean()
    st.metric("Average Momentum", f"{avg_momentum:.1f}%")

with col3:
    total_volume = filtered_keywords['volume'].sum()
    st.metric("Total Volume", f"{total_volume:,.0f}")
