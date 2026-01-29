"""
Darktrace Competitor Intelligence Dashboard
Main Streamlit Application Entry Point
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="Darktrace Competitor Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Darktrace theme
def load_css():
    """Load custom CSS styling"""
    css = """
    <style>
        /* Darktrace Color Palette */
        :root {
            --dt-dark: #030D11;
            --dt-orange: #FF6B00;
            --dt-orange-dark: #E66203;
            --dt-orange-light: #FF791B;
            --dt-sun: #FFA52F;
            --dt-m-gray: #B6B6B6;
            --dt-l-gray: #EAEAEA;
            --dt-white: #FFFFFF;
            --dt-active: #27D62E;
            --dt-alert: #D2150F;
            --dt-flow: #38E0F7;
        }
        
        /* Main background */
        .stApp {
            background-color: var(--dt-l-gray);
        }
        
        /* Header styling */
        .main .block-container {
            padding-top: 2rem;
        }
        
        /* Metric cards */
        .metric-card {
            background-color: var(--dt-white);
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid var(--dt-orange);
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Custom button styling */
        .stButton > button {
            background-color: var(--dt-orange);
            color: white;
            border-radius: 4px;
            border: none;
            font-weight: 500;
        }
        
        .stButton > button:hover {
            background-color: var(--dt-orange-dark);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: var(--dt-dark);
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            color: white;
        }
        
        /* Hide default Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    load_css()
    
    # Check data source - load env vars explicitly
    import os
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Load .env file explicitly
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    
    has_snowflake = os.getenv('SNOWFLAKE_ACCOUNT') is not None
    
    # Sidebar with logo and navigation
    with st.sidebar:
        # Logo
        logo_path = Path(__file__).parent.parent / "Logos" / "Darktrace" / "Darktrace_Logo_DarkBG_White.png"
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.title("🎯 Darktrace")
        
        st.markdown("---")
        st.markdown("### Navigation")
        
        # Navigation info
        st.markdown("""
        **Navigate using the pages menu above** or use the sidebar links:
        
        - 📊 Overview Dashboard
        - 🌍 Brand Analysis  
        - 🏢 Competitor Analysis
        - 📈 Category & Market
        - 🔑 Keywords
        """)
        
        st.markdown("---")
        
        # Data source indicator - test actual connection
        import os
        import sys
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 14:
            st.warning("⚠️ **Python 3.14 Detected**")
            st.caption("Snowflake connector not compatible with Python 3.14")
            st.info("💡 **Solution**: Use Python 3.11 or 3.12, or use mock data for demo")
            st.markdown("---")
        
        from dashboard.data_loader import DashboardDataLoader
        
        # Try to create a loader and check if it's using real data
        try:
            test_loader = DashboardDataLoader(use_real_data=True)
            if test_loader.use_real_data and test_loader.snowflake_connector:
                st.success("✅ **Snowflake Connected**")
                st.caption("Using real-time data from Snowflake")
            else:
                st.info("ℹ️ **Mock Data Mode**")
                st.caption("Using realistic sample data")
                with st.expander("Why Mock Data?"):
                    if python_version.major == 3 and python_version.minor >= 14:
                        st.write("**Python 3.14 Compatibility Issue**")
                        st.write("The Snowflake connector doesn't support Python 3.14 yet.")
                        st.write("**Solutions:**")
                        st.write("1. Use Python 3.11 or 3.12")
                        st.write("2. Use mock data for demo (current)")
                        st.write("3. Wait for Snowflake Python 3.14 support")
                    else:
                        st.write("**Connection Issue**")
                        st.write(f"Account: {os.getenv('SNOWFLAKE_ACCOUNT', 'Not set')}")
                        st.write(f"User: {os.getenv('SNOWFLAKE_USER', 'Not set')}")
                        st.write("Check terminal for connection errors")
        except Exception as e:
            error_msg = str(e)
            if "cgi" in error_msg.lower() or "collections" in error_msg.lower():
                st.error("❌ **Python 3.14 Compatibility Issue**")
                st.caption("Snowflake connector not compatible with Python 3.14")
                st.info("💡 Use Python 3.11 or 3.12, or continue with mock data")
            else:
                st.error(f"❌ **Connection Error**: {error_msg[:100]}")
                st.caption("Check terminal for detailed error messages")
        
        st.markdown("---")
        st.markdown("**Darktrace Competitor Intelligence**")
        st.caption("Real-time competitive tracking")
    
    # Main content
    st.title("🎯 Darktrace Competitor Intelligence")
    st.markdown("### Welcome to the Dashboard")
    st.markdown("Select a page from the sidebar to begin exploring competitor intelligence data.")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Brand Growth", "+12.5%", "↑ vs last quarter")
    
    with col2:
        st.metric("Share of Search", "34.2%", "+2.1%")
    
    with col3:
        st.metric("Category Health", "8.2/10", "Strong")
    
    with col4:
        st.metric("Keywords Tracked", "195", "13 competitors")

if __name__ == "__main__":
    main()
