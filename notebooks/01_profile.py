import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 160)

df = pd.read_csv('data/raw/retail_store_inventory.csv')

print("=== SHAPE ===")
print(df.shape)

print("\n=== DTYPES ===")
print(df.dtypes)

print("\n=== HEAD ===")
print(df.head())

print("\n=== MISSING VALUES ===")
print(df.isna().sum())

print("\n=== DUPLICATE ROWS (full) ===")
print(df.duplicated().sum())

print("\n=== DUPLICATE ROWS (Date, Store ID, Product ID) ===")
print(df.duplicated(subset=['Date', 'Store ID', 'Product ID']).sum())

print("\n=== UNIQUE COUNTS ===")
for c in df.columns:
    print(c, '->', df[c].nunique())

print("\n=== CATEGORICAL VALUES ===")
for c in ['Category', 'Region', 'Weather Condition', 'Seasonality', 'Holiday/Promotion']:
    print(c, ':', sorted(df[c].dropna().unique().tolist()))

print("\n=== NUMERIC DESCRIBE ===")
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print(df[num_cols].describe().T)

print("\n=== DATE RANGE ===")
d = pd.to_datetime(df['Date'], errors='coerce')
print('min:', d.min(), 'max:', d.max(), 'bad dates:', d.isna().sum())

print("\n=== NEGATIVE / ZERO CHECKS ===")
for c in ['Inventory Level', 'Units Sold', 'Units Ordered', 'Demand Forecast', 'Price', 'Discount', 'Competitor Pricing']:
    neg = (df[c] < 0).sum()
    zero = (df[c] == 0).sum()
    print(f"{c}: negative={neg}, zero={zero}")

print("\n=== STORE / PRODUCT COUNTS ===")
print('Stores:', df['Store ID'].unique())
print('Num products:', df['Product ID'].nunique())

print("\n=== DISCOUNT UNIQUE ===")
print(sorted(df['Discount'].unique()))

print("\n=== HOLIDAY/PROMOTION UNIQUE ===")
print(df['Holiday/Promotion'].unique())
