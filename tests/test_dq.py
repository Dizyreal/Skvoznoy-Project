import pytest
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.week8.dq import DQChecker

class TestDQChecker:
    def test_not_empty_pass(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        checker = DQChecker(df)
        assert checker.check_not_empty() == True
    
    def test_not_empty_fail(self):
        df = pd.DataFrame()
        checker = DQChecker(df)
        assert checker.check_not_empty() == False
    
    def test_not_null_pass(self):
        df = pd.DataFrame({"x": [1, 2, 3]})
        checker = DQChecker(df)
        assert checker.check_not_null("x") == True
    
    def test_not_null_fail(self):
        df = pd.DataFrame({"x": [1, None, 3]})
        checker = DQChecker(df)
        assert checker.check_not_null("x") == False
    
    def test_unique_pass(self):
        df = pd.DataFrame({"id": [1, 2, 3]})
        checker = DQChecker(df)
        assert checker.check_unique("id") == True
    
    def test_unique_fail(self):
        df = pd.DataFrame({"id": [1, 1, 2]})
        checker = DQChecker(df)
        assert checker.check_unique("id") == False
    
    def test_range_pass(self):
        df = pd.DataFrame({"value": [1, 2, 3]})
        checker = DQChecker(df)
        assert checker.check_range("value", min_val=0, max_val=10) == True
    
    def test_range_fail(self):
        df = pd.DataFrame({"value": [-1, 2, 11]})
        checker = DQChecker(df)
        assert checker.check_range("value", min_val=0, max_val=10) == False
    
    def test_positive_pass(self):
        df = pd.DataFrame({"count": [1, 2, 3]})
        checker = DQChecker(df)
        assert checker.check_positive("count") == True
    
    def test_positive_fail(self):
        df = pd.DataFrame({"count": [0, -1, 2]})
        checker = DQChecker(df)
        assert checker.check_positive("count") == False