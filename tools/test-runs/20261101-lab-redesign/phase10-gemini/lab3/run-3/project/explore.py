import pandas as pd

for fname in ['data/line_faults.csv', 'data/line_channels.csv', 'data/line_modes.csv']:
    print(f"=== {fname} ===")
    df = pd.read_csv(fname)
    print("Shape:", df.shape)
    print(df.head(3))
    print(df.info())
    print("-" * 50)
