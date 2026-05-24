import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "date": ["2025-01-10", "2025-01-2", "2025-01-3"],
    "value": [10, 2, 3]
})

df = df.sort_values("date")

plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(df["date"], df["value"], marker='o')
plt.title("Bug: String dates (lexicographic sort)")
plt.xlabel("Date (as string)")
plt.ylabel("Value")
plt.xticks(rotation=45)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")

plt.subplot(1, 2, 2)
plt.plot(df["date"], df["value"], marker='o')
plt.title("Fixed: DateTime dates")
plt.xlabel("Date")
plt.ylabel("Value")
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig("docs/figures/week7_diagnostic.png", dpi=150)
plt.show()