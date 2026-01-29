"""Quick test to verify all imports work"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

try:
    import yaml
    print("[OK] PyYAML imported successfully")
except ImportError as e:
    print(f"[FAIL] PyYAML import failed: {e}")

try:
    import streamlit
    print("[OK] Streamlit imported successfully")
except ImportError as e:
    print(f"[FAIL] Streamlit import failed: {e}")

try:
    import plotly
    print("[OK] Plotly imported successfully")
except ImportError as e:
    print(f"[FAIL] Plotly import failed: {e}")

try:
    import pandas
    print("[OK] Pandas imported successfully")
except ImportError as e:
    print(f"[FAIL] Pandas import failed: {e}")

try:
    from dashboard.data_loader import DashboardDataLoader
    print("[OK] DashboardDataLoader imported successfully")
except ImportError as e:
    print(f"[FAIL] DashboardDataLoader import failed: {e}")

try:
    from dashboard.utils import generate_mock_data
    print("[OK] Mock data generator imported successfully")
except ImportError as e:
    print(f"[FAIL] Mock data generator import failed: {e}")

print("\n[SUCCESS] All imports successful! Dashboard should work now.")
