import pandas as pd
import numpy as np
import json

pd.set_option('display.max_columns', None)

df = pd.read_csv('data/cleaned/retail_store_inventory_cleaned.csv', parse_dates=['date'])

out = {}

# --- Overview ---
out['overview'] = {
    'rows': int(len(df)),
    'date_min': df['date'].min().strftime('%Y-%m-%d'),
    'date_max': df['date'].max().strftime('%Y-%m-%d'),
    'n_stores': int(df['store_id'].nunique()),
    'n_categories': int(df['category'].nunique()),
    'n_regions': int(df['region'].nunique()),
    'total_units_sold': int(df['units_sold'].sum()),
    'total_revenue': float(df['revenue'].sum()),
    'avg_daily_revenue': float(df.groupby('date')['revenue'].sum().mean()),
    'overall_stockout_rate': float(df['stockout_flag'].mean()),
    'avg_sell_through_rate': float(df['sell_through_rate'].clip(upper=1).mean()),
}

# --- Monthly trend ---
monthly = df.groupby(df['date'].dt.to_period('M')).agg(
    revenue=('revenue', 'sum'),
    units_sold=('units_sold', 'sum'),
    avg_inventory=('inventory_level', 'mean'),
).reset_index()
monthly['date'] = monthly['date'].astype(str)
out['monthly_trend'] = monthly.to_dict(orient='records')

# --- By category ---
cat = df.groupby('category', observed=True).agg(
    revenue=('revenue', 'sum'),
    units_sold=('units_sold', 'sum'),
    avg_price=('price', 'mean'),
    avg_discount=('discount', 'mean'),
    stockout_rate=('stockout_flag', 'mean'),
    avg_forecast_error=('forecast_error', 'mean'),
    mae=('abs_forecast_error', 'mean'),
).reset_index().sort_values('revenue', ascending=False)
out['by_category'] = cat.to_dict(orient='records')

# --- By region ---
reg = df.groupby('region', observed=True).agg(
    revenue=('revenue', 'sum'),
    units_sold=('units_sold', 'sum'),
    stockout_rate=('stockout_flag', 'mean'),
).reset_index().sort_values('revenue', ascending=False)
out['by_region'] = reg.to_dict(orient='records')

# --- By store ---
store = df.groupby('store_id', observed=True).agg(
    revenue=('revenue', 'sum'),
    units_sold=('units_sold', 'sum'),
    stockout_rate=('stockout_flag', 'mean'),
).reset_index().sort_values('revenue', ascending=False)
out['by_store'] = store.to_dict(orient='records')

# --- Seasonality ---
season_order = ['Spring', 'Summer', 'Autumn', 'Winter']
seas = df.groupby('seasonality', observed=True).agg(
    revenue=('revenue', 'sum'),
    units_sold=('units_sold', 'sum'),
    avg_units_sold=('units_sold', 'mean'),
).reindex(season_order).reset_index()
out['by_season'] = seas.to_dict(orient='records')

# --- Weather ---
weather = df.groupby('weather_condition', observed=True).agg(
    avg_units_sold=('units_sold', 'mean'),
    revenue=('revenue', 'sum'),
).reset_index().sort_values('avg_units_sold', ascending=False)
out['by_weather'] = weather.to_dict(orient='records')

# --- Holiday/Promotion effect ---
holiday = df.groupby('holiday_promotion', observed=True).agg(
    avg_units_sold=('units_sold', 'mean'),
    avg_revenue=('revenue', 'mean'),
    avg_discount=('discount', 'mean'),
).reset_index()
out['by_holiday_promo'] = holiday.to_dict(orient='records')

# --- Discount buckets ---
disc = df.groupby('discount', observed=True).agg(
    avg_units_sold=('units_sold', 'mean'),
    avg_sell_through=('sell_through_rate', lambda x: x.clip(upper=1).mean()),
).reset_index().sort_values('discount')
out['by_discount'] = disc.to_dict(orient='records')

# --- Forecast accuracy overall ---
out['forecast_accuracy'] = {
    'mae': float(df['abs_forecast_error'].mean()),
    'mean_bias': float(df['forecast_error'].mean()),
    'rmse': float(np.sqrt((df['forecast_error']**2).mean())),
    'mape': float((df['abs_forecast_error'] / df['units_sold'].replace(0, np.nan)).mean() * 100),
}

# --- Stockout by category + store cross ---
out['stockout_by_category'] = (
    df.groupby('category', observed=True)['stockout_flag'].mean().reset_index()
    .sort_values('stockout_flag', ascending=False).to_dict(orient='records')
)

# --- Correlation matrix (numeric vars of interest) ---
corr_cols = ['inventory_level', 'units_sold', 'units_ordered', 'demand_forecast',
             'price', 'discount', 'competitor_pricing', 'revenue']
corr = df[corr_cols].corr().round(3)
out['correlation'] = {
    'columns': corr_cols,
    'matrix': corr.values.tolist(),
}

# --- Price vs competitor pricing ---
out['price_competitor'] = {
    'avg_price': float(df['price'].mean()),
    'avg_competitor': float(df['competitor_pricing'].mean()),
    'pct_priced_above_competitor': float((df['price'] > df['competitor_pricing']).mean() * 100),
    'avg_price_diff': float(df['price_vs_competitor'].mean()),
}

# --- Units sold distribution (histogram bins) ---
counts, edges = np.histogram(df['units_sold'], bins=25)
out['units_sold_hist'] = {'counts': counts.tolist(), 'edges': edges.round(1).tolist()}

# --- Weekday pattern ---
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
wd = df.groupby('weekday', observed=True)['units_sold'].mean().reindex(weekday_order).reset_index()
out['by_weekday'] = wd.to_dict(orient='records')

with open('outputs/eda_summary.json', 'w') as f:
    json.dump(out, f, indent=2, default=str)

print(json.dumps(out['overview'], indent=2))
print('\nSaved -> outputs/eda_summary.json')
