import pandas as pd
from io import StringIO

csv_text = "id;value\n1;10\n2;20\n3;30\n"

# BUG: sep не указан -> pandas ожидает запятую
df = pd.read_csv(StringIO(csv_text))

print(df.dtypes)
print(df["value"].mean())   # ожидаем 20.0, но будет ошибка