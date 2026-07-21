import pandas as pd
import numpy as np

df = pd.read_csv('data/raw/retail_store_inventory.csv')

# --- 1. Standardize column names to snake_case ---
df.columns = (
    df.columns.str.strip()
    .str.replace('/', '_', regex=False)
    .str.replace(' ', '_', regex=False)
    .str.lower()
)

# --- 2. Types ---
df['date'] = pd.to_datetime(df['date'])
cat_cols = ['store_id', 'product_id', 'category', 'region', 'weather_condition', 'seasonality']
for c in cat_cols:
    df[c] = df[c].astype('category')
df['holiday_promotion'] = df['holiday_promotion'].astype(bool)

# --- 3. Fix invalid values ---
# Demand cannot be negative; the forecasting model occasionally produced small
# negative values (min -9.99). Clip to 0 and flag which rows were affected
# instead of silently dropping ~0.9% of the data.
df['demand_forecast_was_negative'] = df['demand_forecast'] < 0
df['demand_forecast'] = df['demand_forecast'].clip(lower=0)

# --- 4. Duplicates (none found, but keep as a safety net) ---
before = len(df)
df = df.drop_duplicates(subset=['date', 'store_id', 'product_id', 'category'])
dropped = before - len(df)

# --- 5. Derived columns for analysis ---
df['revenue'] = df['units_sold'] * df['price'] * (1 - df['discount'] / 100)
df['forecast_error'] = df['units_sold'] - df['demand_forecast']
df['abs_forecast_error'] = df['forecast_error'].abs()
df['stockout_flag'] = df['units_sold'] >= df['inventory_level']
df['price_vs_competitor'] = df['price'] - df['competitor_pricing']
df['sell_through_rate'] = df['units_sold'] / df['inventory_level']

df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['month_name'] = df['date'].dt.month_name()
df['weekday'] = df['date'].dt.day_name()
df['is_weekend'] = df['date'].dt.dayofweek >= 5

# --- 6. Sanity re-check after cleaning ---
assert df['date'].isna().sum() == 0
assert (df['demand_forecast'] < 0).sum() == 0
assert df.isna().sum().sum() == 0

print('Dropped exact duplicates:', dropped)
print('Rows with clipped negative demand forecast:', df['demand_forecast_was_negative'].sum())
print('Final shape:', df.shape)
print(df.dtypes)

df.to_csv('data/cleaned/retail_store_inventory_cleaned.csv', index=False)
print('\nSaved -> data/cleaned/retail_store_inventory_cleaned.csv')
