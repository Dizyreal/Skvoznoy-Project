import json
import pandas as pd
from pathlib import Path
from datetime import datetime

class DQChecker:
    def __init__(self, df, table_name="unknown"):
        self.df = df
        self.table_name = table_name
        self.results = []
    
    def check_not_empty(self):
        status = "PASS" if len(self.df) > 0 else "FAIL"
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
    
    def check_unique(self, column, severity="FAIL"):
        is_unique = self.df[column].is_unique
        status = "PASS" if is_unique else severity
        duplicates = self.df[column].duplicated().sum() if not is_unique else 0
        self.results.append({
            "name": f"Unique {column}",
            "status": status,
            "message": f"Duplicates: {duplicates}"
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
    
    def check_positive(self, column, severity="WARNING"):
        non_positive = (self.df[column] <= 0).sum()
        status = "PASS" if non_positive == 0 else severity
        self.results.append({
            "name": f"Positive values in {column}",
            "status": status,
            "message": f"Non-positive count: {non_positive}"
        })
        return status == "PASS"
    
    def run_all_checks(self):
        self.check_not_empty()
        self.check_not_null("date", severity="FAIL")
        self.check_not_null("earthquake_count", severity="FAIL")
        self.check_unique("date", severity="FAIL")
        self.check_range("max_magnitude", min_val=0, max_val=10, severity="FAIL")
        self.check_positive("earthquake_count", severity="FAIL")
        return self.results
    
    def save_report(self, output_path):
        report = {
            "timestamp": datetime.now().isoformat(),
            "table": self.table_name,
            "rows": len(self.df),
            "checks": self.results,
            "summary": {
                "total": len(self.results),
                "pass": sum(1 for r in self.results if r["status"] == "PASS"),
                "fail": sum(1 for r in self.results if r["status"] == "FAIL"),
                "warning": sum(1 for r in self.results if r["status"] == "WARNING")
            }
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        return report
    
    def print_summary(self):
        print(f"\n=== DQ Report for {self.table_name} ===")
        print(f"Rows: {len(self.df)}")
        for r in self.results:
            print(f"  [{r['status']}] {r['name']}: {r['message']}")
        summary = {
            "total": len(self.results),
            "pass": sum(1 for r in self.results if r["status"] == "PASS"),
            "fail": sum(1 for r in self.results if r["status"] == "FAIL"),
            "warning": sum(1 for r in self.results if r["status"] == "WARNING")
        }
        print(f"\nSummary: PASS={summary['pass']}, FAIL={summary['fail']}, WARNING={summary['warning']}")
        return summary["fail"] == 0

def run_dq_on_mart():
    mart_files = list(Path("data/mart").glob("*.csv"))
    if not mart_files:
        print("No mart files found")
        return None
    mart_path = mart_files[0]
    df = pd.read_csv(mart_path)
    df['date'] = pd.to_datetime(df['date'])
    checker = DQChecker(df, table_name="mart_earthquakes")
    checker.run_all_checks()
    checker.print_summary()
    checker.save_report(Path("docs/dq_report.json"))
    return checker.results

if __name__ == "__main__":
    run_dq_on_mart()