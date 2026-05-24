import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.week8.dq import DQChecker

df_bad = pd.DataFrame({
    "date": ["2025-01-01", "2025-01-01", None],
    "earthquake_count": [5, 5, -1],
    "max_magnitude": [2.5, 2.5, 15]
})
df_bad['date'] = pd.to_datetime(df_bad['date'])

checker = DQChecker(df_bad, table_name="broken_data")
checker.run_all_checks()
checker.print_summary()