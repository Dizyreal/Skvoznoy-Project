import pandas as pd

left = pd.DataFrame({
    "id": [1, 1, 2],
    "value": [10, 11, 20]
})

right = pd.DataFrame({
    "id": [1, 1, 2],
    "name": ["A", "A_dup", "B"]
})

print("Было строк:", len(left))
merged = left.merge(right, on="id", how="left")
print("Стало строк:", len(merged))
print(merged)

right_unique = right.drop_duplicates(subset=["id"])
merged_fixed = left.merge(right_unique, on="id", how="left")
print("\nПосле исправления:", len(merged_fixed))