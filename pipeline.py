"""
Main Data Pipeline for Competitor Intelligence Dashboard

Orchestrates:
1. Loading client configuration
2. Fetching keywords for all competitors across all solutions
3. Calculating metrics and momentum
4. Loading processed data to Snowflake

Author: Transmission Agency - Data Team
Last Updated: 2026-01-28
"""

import yaml
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_pipeline.semrush_connector import SEMRushConnector, KeywordClassifier
from data_pipeline.snowflake_loader import SnowflakeLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CompetitorIntelligencePipeline:
    """
    Main pipeline class for competitor intelligence data processing
    """
    
    def __init__(self, client_config_path: str, semrush_api_key: str, snowflake_config: Dict):
        """
        Initialize pipeline
        
        Args:
            client_config_path: Path to client YAML config
            semrush_api_key: SEMRush API key
            snowflake_config: Snowflake connection configuration
        """
        self.config_path = client_config_path
        self.config = self._load_config()
        self.semrush = SEMRushConnector(semrush_api_key)
        self.snowflake = SnowflakeLoader(snowflake_config)
        
        logger.info(f"Initialized pipeline for client: {self.config['client_name']}")
    
    def _load_config(self) -> Dict:
        """Load client configuration from YAML"""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    
    def run_full_pipeline(self, database: str = None) -> Dict[str, pd.DataFrame]:
        """
        Run complete data pipeline for all competitors and solutions
        
        Args:
            database: SEMRush database (if None, uses primary_region from config)
            
        Returns:
            Dictionary of DataFrames with processed data
        """
        if database is None:
            database = self.config['primary_region']
        
        logger.info(f"Starting full pipeline run for {database} database")
        
        # Initialize results storage
        all_keywords = []
        
        # Process each solution category
        for solution_key, solution_data in self.config['solution_categories'].items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing Solution: {solution_data['name']}")
            logger.info(f"{'='*60}")
            
            solution_keywords = self._process_solution(
                solution_key=solution_key,
                solution_data=solution_data,
                database=database
            )
            
            all_keywords.extend(solution_keywords)
        
        # Convert to DataFrame
        keywords_df = pd.DataFrame(all_keywords)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Pipeline Complete!")
        logger.info(f"Total Keywords Collected: {len(keywords_df)}")
        logger.info(f"{'='*60}")
        
        # Calculate aggregated metrics
        metrics_df = self._calculate_solution_metrics(keywords_df)
        
        # Prepare results
        results = {
            'keywords': keywords_df,
            'metrics': metrics_df,
            'run_timestamp': datetime.now()
        }
        
        return results
    
    def _process_solution(
        self, 
        solution_key: str, 
        solution_data: Dict,
        database: str
    ) -> List[Dict]:
        """
        Process all competitors for a single solution
        
        Args:
            solution_key: Solution identifier (e.g., 'cloud')
            solution_data: Solution configuration
            database: SEMRush database
            
        Returns:
            List of keyword dictionaries
        """
        solution_keywords = []
        
        # Get semantic indicators for this solution
        indicators = solution_data['semantic_indicators']
        max_keywords = self.config['max_keywords_per_competitor']
        
        # Add client brand as first "competitor"
        all_competitors = [
            {
                'name': self.config['brand_name'],
                'domain': self.config['brand_domain'],
                'is_client': True
            }
        ]
        
        # Add competitors
        for comp in solution_data['competitors']:
            all_competitors.append({
                'name': comp['name'],
                'domain': comp['domain'],
                'is_client': False,
                'priority': comp.get('priority', 99)
            })
        
        # Process each competitor
        for competitor in all_competitors:
            logger.info(f"\nFetching keywords for: {competitor['name']}")
            
            try:
                # Get top N keywords for this competitor/solution
                keywords_df = self.semrush.get_top_keywords_by_solution(
                    domain=competitor['domain'],
                    solution_name=solution_key,
                    solution_indicators=indicators,
                    database=database,
                    top_n=max_keywords
                )
                
                if keywords_df.empty:
                    logger.warning(f"No keywords found for {competitor['name']}")
                    continue
                
                # Add competitor metadata
                keywords_df['competitor_name'] = competitor['name']
                keywords_df['is_client'] = competitor['is_client']
                keywords_df['solution_category'] = solution_key
                keywords_df['solution_name'] = solution_data['name']
                keywords_df['database'] = database
                keywords_df['fetch_date'] = datetime.now()
                
                # Convert to dict records
                keywords_records = keywords_df.to_dict('records')
                solution_keywords.extend(keywords_records)
                
                logger.info(f"✓ Collected {len(keywords_df)} keywords for {competitor['name']}")
                
            except Exception as e:
                logger.error(f"Error processing {competitor['name']}: {e}")
                continue
        
        return solution_keywords
    
    def _calculate_solution_metrics(self, keywords_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate aggregated metrics by solution and competitor
        
        Args:
            keywords_df: DataFrame with all keywords
            
        Returns:
            DataFrame with aggregated metrics
        """
        if keywords_df.empty:
            return pd.DataFrame()
        
        # Group by solution and competitor
        metrics = keywords_df.groupby(
            ['solution_category', 'solution_name', 'competitor_name', 'is_client']
        ).agg({
            'volume': ['sum', 'mean', 'count'],
            'position': 'mean'
        }).reset_index()
        
        # Flatten column names
        metrics.columns = [
            'solution_category', 'solution_name', 'competitor_name', 'is_client',
            'total_volume', 'avg_volume', 'keyword_count', 'avg_position'
        ]
        
        # Calculate share of search within each solution
        solution_totals = metrics.groupby('solution_category')['total_volume'].sum()
        metrics['solution_total_volume'] = metrics['solution_category'].map(solution_totals)
        metrics['share_of_search'] = (
            metrics['total_volume'] / metrics['solution_total_volume'] * 100
        ).round(2)
        
        # Sort by solution and volume
        metrics = metrics.sort_values(
            ['solution_category', 'total_volume'], 
            ascending=[True, False]
        )
        
        return metrics
    
    def load_to_snowflake(self, results: Dict[str, pd.DataFrame]):
        """
        Load processed data to Snowflake
        
        Args:
            results: Dictionary with keywords and metrics DataFrames
        """
        logger.info("\nLoading data to Snowflake...")
        
        # Load keywords
        self.snowflake.load_keywords(results['keywords'])
        
        # Load metrics
        self.snowflake.load_metrics(results['metrics'])
        
        logger.info("✓ Data successfully loaded to Snowflake")
    
    def generate_summary_report(self, results: Dict[str, pd.DataFrame]) -> str:
        """
        Generate summary report of pipeline run
        
        Args:
            results: Pipeline results
            
        Returns:
            Summary report as string
        """
        keywords_df = results['keywords']
        metrics_df = results['metrics']
        
        report = f"""
{'='*80}
COMPETITOR INTELLIGENCE PIPELINE SUMMARY
{'='*80}

Client: {self.config['client_name']}
Run Date: {results['run_timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

KEYWORDS COLLECTED:
------------------
Total Keywords: {len(keywords_df)}

By Solution:
"""
        
        for solution_key, solution_data in self.config['solution_categories'].items():
            solution_keywords = keywords_df[keywords_df['solution_category'] == solution_key]
            report += f"  • {solution_data['name']}: {len(solution_keywords)} keywords\n"
        
        report += f"\nBy Competitor:\n"
        competitor_counts = keywords_df.groupby('competitor_name').size()
        for competitor, count in competitor_counts.items():
            report += f"  • {competitor}: {count} keywords\n"
        
        report += f"""
METRICS SUMMARY:
---------------
Total Competitors: {len(metrics_df['competitor_name'].unique())}
Total Solutions: {len(metrics_df['solution_category'].unique())}

Top Performers by Solution:
"""
        
        for solution in metrics_df['solution_category'].unique():
            solution_metrics = metrics_df[metrics_df['solution_category'] == solution]
            top_competitor = solution_metrics.nlargest(1, 'total_volume').iloc[0]
            
            report += f"\n  {top_competitor['solution_name']}:\n"
            report += f"    Leader: {top_competitor['competitor_name']}\n"
            report += f"    Volume: {top_competitor['total_volume']:,.0f}\n"
            report += f"    Share: {top_competitor['share_of_search']:.1f}%\n"
        
        report += f"\n{'='*80}\n"
        
        return report


def main():
    """
    Main execution function
    """
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Configuration paths
    config_path = Path(__file__).parent.parent / "config" / "clients" / "darktrace.yaml"
    
    # API keys and credentials
    semrush_api_key = os.getenv('SEMRUSH_API_KEY')
    
    snowflake_config = {
        'account': os.getenv('SNOWFLAKE_ACCOUNT'),
        'user': os.getenv('SNOWFLAKE_USER'),
        'password': os.getenv('SNOWFLAKE_PASSWORD'),
        'database': 'QLIK',
        'schema': 'COMPETITOR_INTELLIGENCE',
        'warehouse': 'COMPUTE_WH',
        'role': 'ANALYTICS_ROLE'
    }
    
    # Initialize and run pipeline
    pipeline = CompetitorIntelligencePipeline(
        client_config_path=str(config_path),
        semrush_api_key=semrush_api_key,
        snowflake_config=snowflake_config
    )
    
    # Run for US market
    results = pipeline.run_full_pipeline(database='us')
    
    # Generate summary report
    report = pipeline.generate_summary_report(results)
    print(report)
    
    # Load to Snowflake
    pipeline.load_to_snowflake(results)
    
    # Save results locally as backup
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results['keywords'].to_csv(output_dir / f"keywords_{timestamp}.csv", index=False)
    results['metrics'].to_csv(output_dir / f"metrics_{timestamp}.csv", index=False)
    
    logger.info(f"\n✓ Results saved to {output_dir}")


if __name__ == "__main__":
    main()
