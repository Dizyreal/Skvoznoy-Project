import pandas as pd

df = pd.DataFrame({"x": [1, None, 3]})

assert df["x"].notna, "x has nulls"

print("Test passed (but incorrectly)")

# import pandas as pd

# df = pd.DataFrame({"x": [1, None, 3]})

# assert df["x"].notna().all(), "x has nulls"

# print("Test failed correctly")