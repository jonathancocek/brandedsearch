"""
Snowflake Connector for Dashboard
Connects to Snowflake and loads data from competitor intelligence tables
Uses SQLAlchemy for Python 3.14 compatibility
"""

import os
import pandas as pd
from typing import Dict, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Load environment variables
load_dotenv()


class SnowflakeDashboardConnector:
    """Connector for loading dashboard data from Snowflake"""
    
    def __init__(self):
        """Initialize Snowflake connection"""
        self.account = os.getenv('SNOWFLAKE_ACCOUNT')
        self.user = os.getenv('SNOWFLAKE_USER')
        self.password = os.getenv('SNOWFLAKE_PASSWORD')
        self.database = os.getenv('SNOWFLAKE_DATABASE', 'BRANDEDSEARCH')
        self.schema = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
        self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
        self.role = os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
        
        self.engine: Optional[Engine] = None
        
    def connect(self):
        """Establish Snowflake connection using SQLAlchemy"""
        if not all([self.account, self.user, self.password]):
            raise ValueError("Missing Snowflake credentials. Set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD")
        
        try:
            # Build connection string for SQLAlchemy
            connection_string = (
                f"snowflake://{self.user}:{self.password}@{self.account}/"
                f"{self.database}/{self.schema}?"
                f"warehouse={self.warehouse}&role={self.role}"
            )
            
            self.engine = create_engine(connection_string)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Snowflake: {e}")
    
    def disconnect(self):
        """Close Snowflake connection"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        if not self.engine:
            self.connect()
        
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(text(query), conn)
            return df
            
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}\nQuery: {query}")
    
    def get_competitor_metrics(self, solution_category: Optional[str] = None) -> pd.DataFrame:
        """Get competitor metrics, optionally filtered by solution category"""
        query = """
        SELECT 
            c.competitor_name,
            s.solution_name,
            s.solution_key,
            m.total_volume,
            m.avg_volume,
            m.keyword_count,
            m.share_of_search,
            m.momentum_pct,
            m.momentum_status,
            m.calculation_date,
            m.database
        FROM COMPETITOR_METRICS m
        JOIN COMPETITORS c ON m.competitor_id = c.competitor_id
        JOIN SOLUTION_CATEGORIES s ON m.solution_id = s.solution_id
        WHERE m.calculation_date = (
            SELECT MAX(calculation_date) 
            FROM COMPETITOR_METRICS m2 
            WHERE m2.competitor_id = m.competitor_id 
            AND m2.solution_id = m.solution_id
        )
        """
        
        if solution_category:
            query += f" AND s.solution_key = '{solution_category}'"
        
        query += " ORDER BY s.solution_name, m.share_of_search DESC"
        
        return self.execute_query(query)
    
    def get_keywords(self, competitor: Optional[str] = None, solution_category: Optional[str] = None) -> pd.DataFrame:
        """Get keywords, optionally filtered by competitor or solution category"""
        query = """
        SELECT 
            c.competitor_name,
            s.solution_name,
            s.solution_key,
            k.keyword,
            k.volume,
            k.position,
            k.fetch_date,
            k.database
        FROM COMPETITOR_KEYWORDS k
        JOIN COMPETITORS c ON k.competitor_id = c.competitor_id
        JOIN SOLUTION_CATEGORIES s ON k.solution_id = s.solution_id
        WHERE k.is_active = TRUE
        AND k.fetch_date = (SELECT MAX(fetch_date) FROM COMPETITOR_KEYWORDS)
        """
        
        if competitor:
            query += f" AND c.competitor_name = '{competitor}'"
        
        if solution_category:
            query += f" AND s.solution_key = '{solution_category}'"
        
        query += " ORDER BY s.solution_name, c.competitor_name, k.volume DESC"
        
        return self.execute_query(query)
    
    def get_regional_data(self) -> pd.DataFrame:
        """Get regional performance data"""
        query = """
        SELECT 
            m.database as region,
            SUM(m.total_volume) as total_volume,
            AVG(m.momentum_pct) as growth_pct,
            SUM(CASE WHEN c.is_client = TRUE THEN m.share_of_search ELSE 0 END) as market_share
        FROM COMPETITOR_METRICS m
        JOIN COMPETITORS c ON m.competitor_id = c.competitor_id
        WHERE m.calculation_date = (SELECT MAX(calculation_date) FROM COMPETITOR_METRICS)
        GROUP BY m.database
        ORDER BY total_volume DESC
        """
        
        df = self.execute_query(query)
        
        # Map database codes to region names
        region_map = {
            'us': 'United States',
            'uk': 'United Kingdom',
            'de': 'Germany',
            'au': 'Australia'
        }
        
        if not df.empty and 'region' in df.columns:
            df['region'] = df['region'].map(region_map).fillna(df['region'])
        
        return df
    
    def get_category_metrics(self) -> pd.DataFrame:
        """Get category-level metrics"""
        query = """
        SELECT 
            s.solution_name,
            s.solution_key,
            SUM(m.total_volume) as total_category_volume,
            AVG(m.momentum_pct) as category_growth_pct,
            COUNT(DISTINCT c.competitor_id) as competitor_count
        FROM COMPETITOR_METRICS m
        JOIN COMPETITORS c ON m.competitor_id = c.competitor_id
        JOIN SOLUTION_CATEGORIES s ON m.solution_id = s.solution_id
        WHERE m.calculation_date = (SELECT MAX(calculation_date) FROM COMPETITOR_METRICS)
        GROUP BY s.solution_name, s.solution_key
        ORDER BY s.solution_key
        """
        
        return self.execute_query(query)
    
    def get_time_series(self, competitor: Optional[str] = None, solution_category: Optional[str] = None) -> pd.DataFrame:
        """Get time series data from keyword history"""
        query = """
        SELECT 
            kh.date,
            c.competitor_name,
            s.solution_name,
            s.solution_key,
            SUM(kh.volume) as volume
        FROM KEYWORD_HISTORY kh
        JOIN COMPETITOR_KEYWORDS k ON kh.keyword_id = k.keyword_id
        JOIN COMPETITORS c ON k.competitor_id = c.competitor_id
        JOIN SOLUTION_CATEGORIES s ON k.solution_id = s.solution_id
        WHERE kh.date >= DATEADD(MONTH, -12, CURRENT_DATE())
        """
        
        if competitor:
            query += f" AND c.competitor_name = '{competitor}'"
        
        if solution_category:
            query += f" AND s.solution_key = '{solution_category}'"
        
        query += """
        GROUP BY kh.date, c.competitor_name, s.solution_name, s.solution_key
        ORDER BY kh.date, c.competitor_name
        """
        
        return self.execute_query(query)
    
    def get_all_competitors(self) -> pd.DataFrame:
        """Get list of all competitors"""
        query = """
        SELECT DISTINCT
            c.competitor_name,
            c.domain,
            c.is_client
        FROM COMPETITORS c
        ORDER BY c.competitor_name
        """
        
        return self.execute_query(query)
    
    def get_solution_categories(self) -> pd.DataFrame:
        """Get list of solution categories"""
        query = """
        SELECT 
            solution_key,
            solution_name,
            display_order
        FROM SOLUTION_CATEGORIES
        ORDER BY display_order
        """
        
        return self.execute_query(query)
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
