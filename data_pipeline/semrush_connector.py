"""
SEMRush API Connector for Competitor Intelligence Dashboard

This module provides methods to:
1. Connect to SEMRush API
2. Fetch branded keywords for competitors
3. Classify keywords by solution category
4. Return top N keywords per competitor/solution

Author: Transmission Agency - Data Team
Last Updated: 2026-01-28
"""

import requests
import pandas as pd
from typing import List, Dict, Optional
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEMRushConnector:
    """
    Connector class for SEMRush API interactions
    """
    
    BASE_URL = "https://api.semrush.com/"
    
    def __init__(self, api_key: str):
        """
        Initialize SEMRush connector
        
        Args:
            api_key: SEMRush API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        
    def _make_request(self, endpoint: str, params: Dict) -> pd.DataFrame:
        """
        Make API request to SEMRush
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            DataFrame with API response
        """
        params['key'] = self.api_key
        
        try:
            response = self.session.get(f"{self.BASE_URL}{endpoint}", params=params)
            response.raise_for_status()
            
            # Parse response (SEMRush returns semicolon-separated values)
            lines = response.text.strip().split('\n')
            
            if len(lines) == 0:
                logger.warning(f"Empty response for {params.get('domain')}")
                return pd.DataFrame()
            
            # First line is headers
            headers = lines[0].split(';')
            
            # Remaining lines are data
            data = [line.split(';') for line in lines[1:]]
            
            df = pd.DataFrame(data, columns=headers)
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"SEMRush API request failed: {e}")
            raise
    
    def get_domain_organic_keywords(
        self, 
        domain: str, 
        database: str = "us",
        limit: int = 1000,
        filter_type: str = "Br"  # Br = Branded keywords
    ) -> pd.DataFrame:
        """
        Get organic keywords for a domain
        
        Args:
            domain: Target domain (e.g., "darktrace.com")
            database: SEMRush database (us, uk, de, etc.)
            limit: Maximum number of keywords to fetch
            filter_type: Filter type (Br = Branded, Co = Competitor)
            
        Returns:
            DataFrame with columns: Keyword, Position, Search Volume, etc.
        """
        params = {
            'type': 'domain_organic',
            'domain': domain,
            'database': database,
            'display_limit': limit,
            'export_columns': 'Ph,Po,Nq,Cp,Co,Nr,Td',
            'display_filter': f'+|{filter_type}'
        }
        
        logger.info(f"Fetching organic keywords for {domain} in {database} database")
        
        df = self._make_request('', params)
        
        if df.empty:
            return df
        
        # Rename columns for clarity
        column_mapping = {
            'Ph': 'keyword',
            'Po': 'position',
            'Nq': 'volume',
            'Cp': 'cpc',
            'Co': 'competition',
            'Nr': 'results',
            'Td': 'trend'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Convert numeric columns
        numeric_cols = ['position', 'volume', 'cpc', 'competition', 'results']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_branded_keywords(
        self,
        domain: str,
        database: str = "us",
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get only branded keywords for a domain
        
        Args:
            domain: Target domain
            database: SEMRush database
            limit: Max keywords to fetch
            
        Returns:
            DataFrame with branded keywords
        """
        # Extract brand name from domain
        brand_name = self._extract_brand_from_domain(domain)
        
        # Get all organic keywords
        all_keywords = self.get_domain_organic_keywords(domain, database, limit)
        
        if all_keywords.empty:
            logger.warning(f"No keywords found for {domain}")
            return pd.DataFrame()
        
        # Filter for branded keywords (contain brand name)
        branded = all_keywords[
            all_keywords['keyword'].str.lower().str.contains(brand_name.lower(), na=False)
        ].copy()
        
        logger.info(f"Found {len(branded)} branded keywords for {domain}")
        
        return branded
    
    def _extract_brand_from_domain(self, domain: str) -> str:
        """
        Extract brand name from domain
        
        Args:
            domain: Domain name (e.g., "darktrace.com")
            
        Returns:
            Brand name (e.g., "darktrace")
        """
        # Remove TLD and common subdomains
        brand = domain.replace('www.', '').split('.')[0]
        return brand
    
    def classify_keywords_by_solution(
        self,
        keywords_df: pd.DataFrame,
        solution_indicators: Dict[str, List[str]]
    ) -> pd.DataFrame:
        """
        Classify keywords into solution categories based on semantic indicators
        
        Args:
            keywords_df: DataFrame with keyword column
            solution_indicators: Dict mapping solution names to indicator lists
            
        Returns:
            DataFrame with added 'solution' column
        """
        if keywords_df.empty:
            return keywords_df
        
        def classify_keyword(keyword: str) -> str:
            """Classify single keyword"""
            keyword_lower = keyword.lower()
            
            # Check each solution's indicators
            for solution, indicators in solution_indicators.items():
                if any(indicator in keyword_lower for indicator in indicators):
                    return solution
            
            return 'unclassified'
        
        keywords_df['solution'] = keywords_df['keyword'].apply(classify_keyword)
        
        return keywords_df
    
    def get_top_keywords_by_solution(
        self,
        domain: str,
        solution_name: str,
        solution_indicators: List[str],
        database: str = "us",
        top_n: int = 15
    ) -> pd.DataFrame:
        """
        Get top N branded keywords for a specific solution
        
        Args:
            domain: Competitor domain
            solution_name: Solution category name
            solution_indicators: List of semantic indicators for solution
            database: SEMRush database
            top_n: Number of top keywords to return
            
        Returns:
            DataFrame with top N keywords for solution
        """
        # Get all branded keywords
        branded_keywords = self.get_branded_keywords(domain, database, limit=1000)
        
        if branded_keywords.empty:
            logger.warning(f"No branded keywords for {domain}")
            return pd.DataFrame()
        
        # Filter for keywords matching solution indicators
        solution_keywords = branded_keywords[
            branded_keywords['keyword'].str.lower().apply(
                lambda x: any(indicator in x for indicator in solution_indicators)
            )
        ].copy()
        
        # If we have fewer than top_n solution-specific keywords, 
        # include generic brand keyword
        if len(solution_keywords) < top_n:
            brand_name = self._extract_brand_from_domain(domain)
            generic_keywords = branded_keywords[
                branded_keywords['keyword'].str.lower() == brand_name.lower()
            ]
            
            if not generic_keywords.empty:
                solution_keywords = pd.concat([solution_keywords, generic_keywords])
        
        # Sort by volume and take top N
        solution_keywords = solution_keywords.sort_values('volume', ascending=False).head(top_n)
        
        # Add solution label
        solution_keywords['solution'] = solution_name
        solution_keywords['domain'] = domain
        
        logger.info(f"Found {len(solution_keywords)} keywords for {domain} - {solution_name}")
        
        return solution_keywords
    
    def get_historical_keyword_data(
        self,
        domain: str,
        keyword: str,
        database: str = "us",
        months_back: int = 24
    ) -> pd.DataFrame:
        """
        Get historical search volume for a specific keyword
        
        Args:
            domain: Domain
            keyword: Specific keyword
            database: SEMRush database
            months_back: Number of months of history
            
        Returns:
            DataFrame with monthly volume history
        """
        # SEMRush endpoint for historical data
        params = {
            'type': 'phrase_organic',
            'phrase': keyword,
            'database': database,
            'export_columns': 'Ph,Dt,Nq'
        }
        
        df = self._make_request('', params)
        
        if df.empty:
            return df
        
        # Rename columns
        df = df.rename(columns={
            'Ph': 'keyword',
            'Dt': 'date',
            'Nq': 'volume'
        })
        
        # Convert volume to numeric
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        # Parse date
        df['date'] = pd.to_datetime(df['date'], format='%Y%m', errors='coerce')
        
        # Filter to requested time range
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)
        df = df[df['date'] >= cutoff_date]
        
        return df
    
    def calculate_momentum(
        self,
        keywords_df: pd.DataFrame,
        domain: str,
        database: str = "us",
        comparison_months: int = 3
    ) -> pd.DataFrame:
        """
        Calculate momentum for keywords (recent N months vs prior N months)
        
        Args:
            keywords_df: DataFrame with current keywords
            domain: Domain
            database: SEMRush database
            comparison_months: Number of months for comparison period
            
        Returns:
            DataFrame with added momentum columns
        """
        if keywords_df.empty:
            return keywords_df
        
        keywords_with_momentum = []
        
        for _, row in keywords_df.iterrows():
            keyword = row['keyword']
            
            # Get historical data
            historical = self.get_historical_keyword_data(
                domain, keyword, database, months_back=comparison_months * 2
            )
            
            if len(historical) < comparison_months * 2:
                # Not enough data
                row['recent_avg'] = row['volume']
                row['prior_avg'] = row['volume']
                row['momentum_pct'] = 0.0
            else:
                # Calculate averages
                recent_avg = historical.head(comparison_months)['volume'].mean()
                prior_avg = historical.iloc[comparison_months:comparison_months*2]['volume'].mean()
                
                if prior_avg > 0:
                    momentum_pct = ((recent_avg - prior_avg) / prior_avg) * 100
                else:
                    momentum_pct = 0.0
                
                row['recent_avg'] = recent_avg
                row['prior_avg'] = prior_avg
                row['momentum_pct'] = momentum_pct
            
            keywords_with_momentum.append(row)
            
            # Rate limiting
            time.sleep(0.1)
        
        return pd.DataFrame(keywords_with_momentum)
    
    def get_competitor_keyword_overlap(
        self,
        domain1: str,
        domain2: str,
        database: str = "us"
    ) -> pd.DataFrame:
        """
        Find keywords that both competitors rank for
        
        Args:
            domain1: First competitor domain
            domain2: Second competitor domain
            database: SEMRush database
            
        Returns:
            DataFrame with overlapping keywords
        """
        params = {
            'type': 'domain_domains',
            'domains': f'{domain1}|{domain2}',
            'database': database,
            'export_columns': 'Dn,Cr,Np,Or'
        }
        
        df = self._make_request('', params)
        
        return df


class KeywordClassifier:
    """
    Helper class for keyword classification
    """
    
    @staticmethod
    def load_solution_config(config_path: str) -> Dict:
        """
        Load solution configuration from YAML
        
        Args:
            config_path: Path to YAML config file
            
        Returns:
            Configuration dict
        """
        import yaml
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    @staticmethod
    def extract_solution_indicators(config: Dict) -> Dict[str, List[str]]:
        """
        Extract solution indicators from config
        
        Args:
            config: Client configuration dict
            
        Returns:
            Dict mapping solution names to indicator lists
        """
        indicators = {}
        
        for solution_key, solution_data in config['solution_categories'].items():
            indicators[solution_key] = solution_data['semantic_indicators']
        
        return indicators


# Example usage
if __name__ == "__main__":
    # Initialize connector
    api_key = "YOUR_SEMRUSH_API_KEY"
    connector = SEMRushConnector(api_key)
    
    # Example: Get top 15 cloud security keywords for Darktrace
    cloud_indicators = [
        'cloud', 'cspm', 'cwpp', 'container', 'kubernetes', 'aws', 'azure', 'gcp'
    ]
    
    keywords = connector.get_top_keywords_by_solution(
        domain="darktrace.com",
        solution_name="cloud",
        solution_indicators=cloud_indicators,
        database="us",
        top_n=15
    )
    
    print(f"\nTop 15 Cloud Security Keywords for Darktrace:")
    print(keywords[['keyword', 'volume', 'position']])
