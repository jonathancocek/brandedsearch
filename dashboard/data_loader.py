"""
Data Loader for Dashboard
Loads data from Snowflake tables (primary) or falls back to mock data
"""

import os
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    # Python 3.14 compatibility: Add cgi shim before importing
    try:
        import cgi
    except ImportError:
        from pathlib import Path
        cgi_shim_path = Path(__file__).parent.parent / 'cgi_compat.py'
        if cgi_shim_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("cgi_compat", cgi_shim_path)
            cgi_compat = importlib.util.module_from_spec(spec)
            import sys
            sys.modules['cgi'] = cgi_compat
            spec.loader.exec_module(cgi_compat)
    
    from dashboard.snowflake_connector import SnowflakeDashboardConnector
    SNOWFLAKE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import Snowflake connector: {e}")
    import traceback
    traceback.print_exc()
    SNOWFLAKE_AVAILABLE = False
    SnowflakeDashboardConnector = None
except Exception as e:
    print(f"Warning: Error setting up Snowflake connector: {e}")
    import traceback
    traceback.print_exc()
    SNOWFLAKE_AVAILABLE = False
    SnowflakeDashboardConnector = None

from dashboard.utils import generate_mock_data


class DashboardDataLoader:
    """Load data for dashboard from Snowflake tables or use mock data"""
    
    def __init__(self, use_real_data: bool = True):
        """
        Initialize data loader
        
        Args:
            use_real_data: If True, attempt to load from Snowflake
        """
        self.use_real_data = use_real_data
        self.snowflake_connector = None
        
        # Check if Snowflake credentials are available
        has_creds = all([
            os.getenv('SNOWFLAKE_ACCOUNT'),
            os.getenv('SNOWFLAKE_USER'),
            os.getenv('SNOWFLAKE_PASSWORD')
        ])
        
        if use_real_data and has_creds and SNOWFLAKE_AVAILABLE:
            try:
                self.snowflake_connector = SnowflakeDashboardConnector()
                self.snowflake_connector.connect()
                # Test a simple query to verify connection works
                test_df = self.snowflake_connector.execute_query("SELECT 1 as test")
                if not test_df.empty:
                    print("✓ Connected to Snowflake successfully")
                    self.use_real_data = True
                else:
                    raise Exception("Connection test query returned empty")
            except Exception as e:
                import traceback
                error_msg = f"Warning: Could not connect to Snowflake: {e}"
                print(error_msg)
                print(traceback.format_exc())
                print("Falling back to mock data")
                self.use_real_data = False
                self.snowflake_connector = None
        else:
            self.use_real_data = False
            if not has_creds:
                print("Snowflake credentials not found. Using mock data.")
                print(f"Account: {os.getenv('SNOWFLAKE_ACCOUNT')}")
                print(f"User: {os.getenv('SNOWFLAKE_USER')}")
                print(f"Password: {'SET' if os.getenv('SNOWFLAKE_PASSWORD') else 'NOT SET'}")
            elif not SNOWFLAKE_AVAILABLE:
                print("Snowflake connector not available. Using mock data.")
    
    def load_competitor_metrics(self, solution_category: Optional[str] = None) -> pd.DataFrame:
        """Load competitor metrics from Snowflake"""
        if not self.use_real_data or not self.snowflake_connector:
            mock_data = generate_mock_data()
            df = mock_data['competitor_metrics']
            if solution_category:
                # Map solution keys to category names
                category_map = {
                    'cloud': 'Cloud Security',
                    'email': 'Email Security',
                    'network': 'Network Security'
                }
                category_name = category_map.get(solution_category.lower(), solution_category)
                df = df[df['category'].str.contains(category_name, case=False)]
            return df
        
        try:
            df = self.snowflake_connector.get_competitor_metrics(solution_category=solution_category)
            
            # Rename columns to match expected format
            if not df.empty:
                df = df.rename(columns={
                    'SOLUTION_NAME': 'category',
                    'COMPETITOR_NAME': 'competitor',
                    'TOTAL_VOLUME': 'total_volume',
                    'SHARE_OF_SEARCH': 'share_of_search',
                    'MOMENTUM_PCT': 'momentum_pct',
                    'KEYWORD_COUNT': 'keyword_count'
                })
            
            return df
            
        except Exception as e:
            print(f"Error loading competitor metrics from Snowflake: {e}")
            print("Falling back to mock data")
            mock_data = generate_mock_data()
            df = mock_data['competitor_metrics']
            if solution_category:
                category_map = {
                    'cloud': 'Cloud Security',
                    'email': 'Email Security',
                    'network': 'Network Security'
                }
                category_name = category_map.get(solution_category.lower(), solution_category)
                df = df[df['category'].str.contains(category_name, case=False)]
            return df
    
    def load_keywords(self, competitor: Optional[str] = None, solution_category: Optional[str] = None) -> pd.DataFrame:
        """Load keywords data from Snowflake"""
        if not self.use_real_data or not self.snowflake_connector:
            mock_data = generate_mock_data()
            df = mock_data['keywords']
            if competitor:
                df = df[df['competitor'] == competitor]
            if solution_category:
                category_map = {
                    'cloud': 'Cloud Security',
                    'email': 'Email Security',
                    'network': 'Network Security'
                }
                category_name = category_map.get(solution_category.lower(), solution_category)
                df = df[df['category'].str.contains(category_name, case=False)]
            return df
        
        try:
            df = self.snowflake_connector.get_keywords(
                competitor=competitor,
                solution_category=solution_category
            )
            
            # Rename columns to match expected format
            if not df.empty:
                df = df.rename(columns={
                    'COMPETITOR_NAME': 'competitor',
                    'SOLUTION_NAME': 'category',
                    'KEYWORD': 'keyword',
                    'VOLUME': 'volume',
                    'POSITION': 'position'
                })
                # Calculate momentum (simplified)
                df['momentum'] = df.groupby(['competitor', 'category'])['volume'].pct_change().fillna(0) * 100
            
            return df
            
        except Exception as e:
            print(f"Error loading keywords from Snowflake: {e}")
            print("Falling back to mock data")
            mock_data = generate_mock_data()
            df = mock_data['keywords']
            if competitor:
                df = df[df['competitor'] == competitor]
            if solution_category:
                category_map = {
                    'cloud': 'Email Security',
                    'email': 'Email Security',
                    'network': 'Network Security'
                }
                category_name = category_map.get(solution_category.lower(), solution_category)
                df = df[df['category'].str.contains(category_name, case=False)]
            return df
    
    def load_regional_data(self) -> pd.DataFrame:
        """Load regional data from Snowflake"""
        if not self.use_real_data or not self.snowflake_connector:
            mock_data = generate_mock_data()
            return mock_data['regional']
        
        try:
            df = self.snowflake_connector.get_regional_data()
            
            # Rename columns to match expected format
            if not df.empty:
                df = df.rename(columns={
                    'REGION': 'region',
                    'TOTAL_VOLUME': 'total_volume',
                    'GROWTH_PCT': 'growth_pct',
                    'MARKET_SHARE': 'market_share'
                })
            
            return df
            
        except Exception as e:
            print(f"Error loading regional data from Snowflake: {e}")
            print("Falling back to mock data")
            mock_data = generate_mock_data()
            return mock_data['regional']
    
    def load_time_series(self, competitor: Optional[str] = None, solution_category: Optional[str] = None) -> pd.DataFrame:
        """Load time series data from Snowflake"""
        if not self.use_real_data or not self.snowflake_connector:
            mock_data = generate_mock_data()
            return mock_data['time_series']
        
        try:
            df = self.snowflake_connector.get_time_series(
                competitor=competitor,
                solution_category=solution_category
            )
            
            # Rename columns to match expected format
            if not df.empty:
                df = df.rename(columns={
                    'DATE': 'date',
                    'COMPETITOR_NAME': 'competitor',
                    'SOLUTION_NAME': 'category',
                    'VOLUME': 'volume'
                })
            
            return df
            
        except Exception as e:
            print(f"Error loading time series from Snowflake: {e}")
            print("Falling back to mock data")
            mock_data = generate_mock_data()
            return mock_data['time_series']
    
    def load_category_metrics(self) -> pd.DataFrame:
        """Load category-level metrics from Snowflake"""
        if not self.use_real_data or not self.snowflake_connector:
            # Generate mock category metrics
            categories = ['Cloud Security', 'Email Security', 'Network Security']
            return pd.DataFrame({
                'category': categories,
                'total_volume': [156200, 121890, 98450],
                'growth_pct': [18.5, 8.3, -3.2]
            })
        
        try:
            df = self.snowflake_connector.get_category_metrics()
            
            if not df.empty:
                df = df.rename(columns={
                    'SOLUTION_NAME': 'category',
                    'TOTAL_CATEGORY_VOLUME': 'total_volume',
                    'CATEGORY_GROWTH_PCT': 'growth_pct'
                })
            
            return df
            
        except Exception as e:
            print(f"Error loading category metrics from Snowflake: {e}")
            categories = ['Cloud Security', 'Email Security', 'Network Security']
            return pd.DataFrame({
                'category': categories,
                'total_volume': [156200, 121890, 98450],
                'growth_pct': [18.5, 8.3, -3.2]
            })
    
    def load_all_data(self) -> Dict:
        """Load all data"""
        return {
            'competitor_metrics': self.load_competitor_metrics(),
            'keywords': self.load_keywords(),
            'regional': self.load_regional_data(),
            'time_series': self.load_time_series(),
            'category_metrics': self.load_category_metrics()
        }
    
    def __del__(self):
        """Cleanup: close Snowflake connection"""
        if self.snowflake_connector:
            self.snowflake_connector.disconnect()
