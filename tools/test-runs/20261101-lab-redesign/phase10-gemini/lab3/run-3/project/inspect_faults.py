import pandas as pd

df = pd.read_csv('data/line_faults.csv')
print("Fault value counts:")
print(df['fault'].value_counts(dropna=False))
print(df['fault'].value_counts(normalize=True))
print("\nMissing values:")
print(df.isnull().sum())
print("\nSummary statistics:")
print(df.describe())
