import pandas as pd
from io import StringIO

csv_text = "id;value\n1;10\n2;20\n3;30\n"

df = pd.read_csv(StringIO(csv_text), sep=";") #sep

print(df.head())
print(df.dtypes)
print(df["value"].mean())