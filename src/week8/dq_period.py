import json
import pandas as pd
from pathlib import Path
from datetime import datetime

class DQCheckerPeriod:
    def __init__(self, df, table_name, period):
        self.df = df
        self.table_name = table_name
        self.period = period
        self.results = []
    
    def check_not_empty(self):
        status = "PASS" if len(self.df) > 0 else "WARNING"
        self.results.append({
            "name": "Table not empty",
            "status": status,
            "message": f"Rows: {len(self.df)}"
        })
        return status == "PASS"
    
    def check_not_null(self, column, severity="FAIL"):
        null_count = self.df[column].isna().sum()
        status = "PASS" if null_count == 0 else severity
        self.results.append({
            "name": f"No NULLs in {column}",
            "status": status,
            "message": f"Null count: {null_count}"
        })
        return status == "PASS"
    
    def check_range(self, column, min_val=None, max_val=None, severity="WARNING"):
        out_of_range = 0
        if min_val is not None:
            out_of_range += (self.df[column] < min_val).sum()
        if max_val is not None:
            out_of_range += (self.df[column] > max_val).sum()
        status = "PASS" if out_of_range == 0 else severity
        self.results.append({
            "name": f"Range for {column}",
            "status": status,
            "message": f"Values out of range [{min_val}, {max_val}]: {out_of_range}"
        })
        return status == "PASS"
    
    def run_all_checks(self):
        all_pass = True
        all_pass &= self.check_not_empty()
        all_pass &= self.check_not_null("date", severity="FAIL")
        all_pass &= self.check_not_null("earthquake_count", severity="FAIL")
        all_pass &= self.check_range("max_magnitude", min_val=0, max_val=10, severity="FAIL")
        return all_pass
    
    def print_summary(self):
        print(f"\n=== DQ Report for {self.table_name} (period: {self.period}) ===")
        print(f"Rows: {len(self.df)}")
        for r in self.results:
            print(f"  [{r['status']}] {r['name']}: {r['message']}")
    
    def save_report(self, output_path):
        report = {
            "timestamp": datetime.now().isoformat(),
            "table": self.table_name,
            "period": self.period,
            "rows": len(self.df),
            "checks": self.results
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        return report