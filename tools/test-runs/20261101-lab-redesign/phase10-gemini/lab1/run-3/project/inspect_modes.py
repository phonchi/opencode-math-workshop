import pandas as pd
df = pd.read_csv('data/line_modes.csv')
print(df.nunique())
print(df.describe())
