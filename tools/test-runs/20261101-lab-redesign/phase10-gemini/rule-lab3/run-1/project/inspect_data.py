import pandas as pd

for name in ["data/line_faults.csv", "data/line_channels.csv", "data/line_modes.csv"]:
    print(f"=== {name} ===")
    df = pd.read_csv(name)
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("Head:")
    print(df.head(3))
    print("Missing values:", df.isna().sum().sum())
    if "fault" in df.columns:
        print("Fault value counts:")
        print(df["fault"].value_counts(dropna=False))
    print("\n")
