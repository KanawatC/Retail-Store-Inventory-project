"""
Redo of Steps 2-3 at category grain: for each of the 5 category series,
(a) re-check candidate exogenous features against that category's daily
demand, and (b) run the stationarity / trend / autocorrelation diagnostics
that drive model choice.
"""
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller, acf, pacf

cat_daily = pd.read_csv('forecasting/daily_demand_by_category.csv', parse_dates=['date'])
categories = sorted(cat_daily['category'].unique())

def eta_squared(groups):
    all_vals = np.concatenate(groups)
    grand_mean = all_vals.mean()
    ss_total = ((all_vals - grand_mean) ** 2).sum()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    return ss_between / ss_total

feature_rows = []
diag_rows = []

for cat in categories:
    g = cat_daily[cat_daily['category'] == cat].sort_values('date')
    y = g['units_sold'].values.astype(float)

    # --- features ---
    for col in ['avg_price', 'avg_discount', 'promo_fraction', 'avg_competitor_pricing']:
        r, p = stats.pearsonr(g[col].values, y)
        feature_rows.append({'category': cat, 'variable': col, 'type': 'continuous',
                              'p_value': p, 'effect': r**2, 'effect_name': 'r^2'})
    for col in ['dominant_weather', 'dominant_season', 'weekday', 'is_weekend']:
        groups = [gg['units_sold'].values for _, gg in g.groupby(col, observed=True)]
        f, p = stats.f_oneway(*groups)
        eta2 = eta_squared(groups)
        feature_rows.append({'category': cat, 'variable': col, 'type': 'categorical',
                              'p_value': p, 'effect': eta2, 'effect_name': 'eta^2'})

    # --- diagnostics ---
    adf_stat, adf_p, *_ = adfuller(y)
    t = np.arange(len(y))
    slope, intercept, r_trend, p_trend, se = stats.linregress(t, y)
    acf_vals = acf(y, nlags=21, fft=True)
    bound = 1.96 / np.sqrt(len(y))
    sig_lags = [i + 1 for i, v in enumerate(acf_vals[1:]) if abs(v) > bound]
    diag_rows.append({
        'category': cat, 'mean': y.mean(), 'std': y.std(), 'cv': y.std() / y.mean(),
        'adf_p': adf_p, 'stationary': adf_p < 0.05,
        'trend_slope': slope, 'trend_p': p_trend,
        'sig_acf_lags': sig_lags,
    })

feat_df = pd.DataFrame(feature_rows)
diag_df = pd.DataFrame(diag_rows)

pd.set_option('display.width', 160)
pd.set_option('display.max_columns', None)

print("=== Feature significance per category (p<0.05 AND effect>=0.02 required to keep) ===")
feat_df['keep'] = (feat_df['p_value'] < 0.05) & (feat_df['effect'] >= 0.02)
print(feat_df.to_string(index=False))
n_kept = feat_df['keep'].sum()
print(f"\nFeatures kept across all 5 categories x 8 variables = 40 tests: {n_kept}")

print("\n=== Series diagnostics per category ===")
print(diag_df.to_string(index=False))

feat_df.to_csv('forecasting/feature_hypothesis_by_category.csv', index=False)
diag_df.to_csv('forecasting/diagnostics_by_category.csv', index=False)
print("\nSaved -> forecasting/feature_hypothesis_by_category.csv")
print("Saved -> forecasting/diagnostics_by_category.csv")
