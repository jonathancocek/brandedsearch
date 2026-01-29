"""
Utility functions for the dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_mock_data():
    """Generate mock data for dashboard visualization"""
    
    # Competitors by category
    competitors = {
        'Cloud Security': ['Wiz', 'Orca', 'Crowdstrike', 'Palo Alto Cortex Cloud'],
        'Email Security': ['Abnormal', 'ProofPoint', 'Mimecast'],
        'Network Security': ['VectraAI', 'ExtraHop', 'CoreLight']
    }
    
    # Regions
    regions = ['United States', 'United Kingdom', 'Germany', 'Australia']
    
    # Generate date range (last 12 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate competitor metrics
    competitor_metrics = []
    for category, comp_list in competitors.items():
        for competitor in comp_list:
            base_volume = random.randint(5000, 35000)
            momentum = random.uniform(-15, 25)
            share = random.uniform(5, 25)
            
            competitor_metrics.append({
                'competitor': competitor,
                'category': category,
                'total_volume': base_volume,
                'share_of_search': round(share, 1),
                'momentum_pct': round(momentum, 1),
                'keyword_count': 15
            })
    
    # Generate keyword data
    keywords_data = []
    keywords_list = [
        'cloud security', 'email protection', 'network detection', 'threat detection',
        'security platform', 'cyber defense', 'threat intelligence', 'security monitoring',
        'incident response', 'security analytics', 'threat hunting', 'security operations',
        'cloud workload', 'container security', 'kubernetes security', 'email gateway',
        'phishing protection', 'business email compromise', 'network traffic', 'intrusion detection'
    ]
    
    for category, comp_list in competitors.items():
        for competitor in comp_list:
            for i in range(15):
                keyword = f"{competitor.lower()} {random.choice(keywords_list)}"
                volume = random.randint(100, 10000)
                position = random.uniform(1, 10)
                trend = random.uniform(-20, 30)
                
                keywords_data.append({
                    'keyword': keyword,
                    'competitor': competitor,
                    'category': category,
                    'volume': volume,
                    'position': round(position, 1),
                    'momentum': round(trend, 1)
                })
    
    # Generate regional data
    regional_data = []
    for region in regions:
        base_volume = random.randint(5000, 50000)
        growth = random.uniform(-5, 20)
        share = random.uniform(25, 45)
        
        regional_data.append({
            'region': region,
            'total_volume': base_volume,
            'growth_pct': round(growth, 1),
            'market_share': round(share, 1)
        })
    
    # Generate time series data
    time_series = []
    for date in dates[::7]:  # Weekly data points
        for category, comp_list in competitors.items():
            for competitor in comp_list:
                base = random.randint(1000, 5000)
                trend = np.sin(np.arange(len(dates[::7])) * 0.1) * 500 + base
                volume = max(0, int(trend[len(time_series) % len(dates[::7])] if len(time_series) < len(dates[::7]) else base))
                
                time_series.append({
                    'date': date,
                    'competitor': competitor,
                    'category': category,
                    'volume': volume
                })
    
    return {
        'competitor_metrics': pd.DataFrame(competitor_metrics),
        'keywords': pd.DataFrame(keywords_data),
        'regional': pd.DataFrame(regional_data),
        'time_series': pd.DataFrame(time_series)
    }

def get_status_badge(momentum):
    """Get status badge based on momentum"""
    if momentum >= 20:
        return "🟢 Strong Growth"
    elif momentum >= 10:
        return "🟡 Growth"
    elif momentum >= -5:
        return "🟠 Stable"
    elif momentum >= -10:
        return "🔴 Decline"
    else:
        return "⚫ Major Decline"

def format_number(num):
    """Format number with commas"""
    return f"{num:,.0f}"
