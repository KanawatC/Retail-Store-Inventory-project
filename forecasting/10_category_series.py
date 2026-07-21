"""
Redo of Step 1: instead of one flat aggregate series, forecast demand PER
PRODUCT CATEGORY (summed across all 5 stores). category is used as "product
type" rather than product_id because product_id is not a stable SKU key (it
was already flagged as cycling through all 5 categories within a store over
the two years) - category is the stable, meaningful grouping.

Store is aggregated away (summed, not modeled separately) because both the
global and within-category hypothesis tests showed store has a negligible
effect on units_sold (eta^2 < 0.001 in every category) - so once we have a
category-level forecast, splitting it evenly across the 5 stores is a
statistically defensible stocking rule, not an assumption.
"""
import pandas as pd

df = pd.read_csv('data/cleaned/retail_store_inventory_cleaned.csv', parse_dates=['date'])

def mode(s):
    return s.mode().iloc[0]

cat_daily = df.groupby(['category', 'date'], observed=True).agg(
    units_sold=('units_sold', 'sum'),
    avg_price=('price', 'mean'),
    avg_discount=('discount', 'mean'),
    promo_fraction=('holiday_promotion', 'mean'),
    avg_competitor_pricing=('competitor_pricing', 'mean'),
    dominant_weather=('weather_condition', mode),
    dominant_season=('seasonality', mode),
    weekday=('weekday', 'first'),
    is_weekend=('is_weekend', 'first'),
    n_stores_reporting=('store_id', 'nunique'),
).reset_index().sort_values(['category', 'date'])

print("Shape:", cat_daily.shape)
print(cat_daily.groupby('category', observed=True)['units_sold'].describe())
print("\nAll category-days have all 5 stores reporting:", (cat_daily['n_stores_reporting'] == 5).all())

cat_daily.to_csv('forecasting/daily_demand_by_category.csv', index=False)
print("\nSaved -> forecasting/daily_demand_by_category.csv")
