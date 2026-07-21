"""
Phase B - Hypothesis testing: which candidate features actually relate to the
DAILY TOTAL DEMAND series (the target chosen in Phase A)? Row-level features
are aggregated to daily level first (avg price, avg discount, promo fraction,
dominant weather, etc.), since that is the granularity the forecasting models
will operate at.

Continuous features -> Pearson + Spearman correlation vs daily demand.
Categorical features -> one-way ANOVA (F-test) + eta-squared vs daily demand,
using the day's *dominant* category (mode across that day's 100 rows).

Leakage note: inventory_level, units_ordered and demand_forecast are same-day
/ contemporaneous operational variables entangled with sales on the same day
(inventory is drawn down BY the sale; demand_forecast is a competing forecast,
not a causal input) - reported here for completeness but excluded from the
candidate predictor set regardless of significance.
"""
import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv('data/cleaned/retail_store_inventory_cleaned.csv', parse_dates=['date'])

def mode(s):
    return s.mode().iloc[0]

daily = df.groupby('date').agg(
    units_sold=('units_sold', 'sum'),
    avg_price=('price', 'mean'),
    avg_discount=('discount', 'mean'),
    promo_fraction=('holiday_promotion', 'mean'),
    avg_competitor_pricing=('competitor_pricing', 'mean'),
    dominant_weather=('weather_condition', mode),
    dominant_season=('seasonality', mode),
    weekday=('weekday', 'first'),
    is_weekend=('is_weekend', 'first'),
    # leakage-risk vars, reported not used
    avg_inventory_level=('inventory_level', 'mean'),
    avg_units_ordered=('units_ordered', 'mean'),
    avg_demand_forecast=('demand_forecast', 'mean'),
).reset_index()
daily['month'] = daily['date'].dt.month

daily.to_csv('forecasting/daily_demand.csv', index=False)

print("Daily series shape:", daily.shape)
print(daily.head())

results = []

# --- continuous candidates ---
continuous = ['avg_price', 'avg_discount', 'promo_fraction', 'avg_competitor_pricing']
for col in continuous:
    r_p, p_p = stats.pearsonr(daily[col], daily['units_sold'])
    r_s, p_s = stats.spearmanr(daily[col], daily['units_sold'])
    results.append({'variable': col, 'type': 'continuous', 'stat': r_p, 'p_value': p_p,
                     'effect': r_p**2, 'effect_name': 'r^2', 'spearman_r': r_s, 'spearman_p': p_s})

# --- categorical candidates ---
def eta_squared(groups):
    all_vals = np.concatenate(groups)
    grand_mean = all_vals.mean()
    ss_total = ((all_vals - grand_mean) ** 2).sum()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    return ss_between / ss_total

categorical = ['dominant_weather', 'dominant_season', 'weekday', 'is_weekend']
for col in categorical:
    groups = [g['units_sold'].values for _, g in daily.groupby(col, observed=True)]
    f_stat, p_val = stats.f_oneway(*groups)
    eta2 = eta_squared(groups)
    results.append({'variable': col, 'type': 'categorical', 'stat': f_stat, 'p_value': p_val,
                     'effect': eta2, 'effect_name': 'eta^2', 'spearman_r': np.nan, 'spearman_p': np.nan})

# --- leakage-risk vars: report only ---
leakage = ['avg_inventory_level', 'avg_units_ordered', 'avg_demand_forecast']
for col in leakage:
    r_p, p_p = stats.pearsonr(daily[col], daily['units_sold'])
    results.append({'variable': col + ' [EXCLUDED: leakage risk]', 'type': 'continuous', 'stat': r_p,
                     'p_value': p_p, 'effect': r_p**2, 'effect_name': 'r^2', 'spearman_r': np.nan, 'spearman_p': np.nan})

res_df = pd.DataFrame(results)
pd.set_option('display.width', 160)
pd.set_option('display.max_columns', None)
print()
print(res_df.to_string(index=False))

SIG_P = 0.05
MIN_EFFECT = 0.02  # r^2 or eta^2 threshold for "worth including" (roughly Cohen's small-medium boundary)

print("\nSelection (p < 0.05 AND effect >= 0.02):")
selected = []
for r in results:
    if 'EXCLUDED' in r['variable']:
        print(f"  {r['variable']:<38} -- excluded a priori (leakage), p={r['p_value']:.3f} {r['effect_name']}={r['effect']:.4f}")
        continue
    keep = (r['p_value'] < SIG_P) and (r['effect'] >= MIN_EFFECT)
    tag = 'KEEP' if keep else 'drop'
    print(f"  {r['variable']:<20} p={r['p_value']:.3f}  {r['effect_name']}={r['effect']:.4f}  -> {tag}")
    if keep:
        selected.append(r['variable'])

print("\nSelected features for the multivariate model:", selected if selected else "NONE (univariate only)")

res_df.to_csv('forecasting/feature_hypothesis_results.csv', index=False)
print("\nSaved -> forecasting/feature_hypothesis_results.csv")
print("Saved -> forecasting/daily_demand.csv")
