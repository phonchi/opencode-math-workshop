import pandas as pd

for fname in ['data/line_channels.csv', 'data/line_modes.csv']:
    df = pd.read_csv(fname)
    print(f"=== {fname} ===")
    print(df.describe())
