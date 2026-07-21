"""
Phase A - Hypothesis testing: does units_sold depend on store_id / product_id /
category / region? Used to decide the granularity of the demand series we
forecast (aggregate total vs per-store vs per-product).

We report BOTH the classical p-value (one-way ANOVA F-test + Kruskal-Wallis H-test)
AND the effect size (eta-squared), because at n=73,100 even a tiny, practically
meaningless difference between groups will be "statistically significant" by
p-value alone. Cohen's guideline for eta-squared: <0.01 negligible, 0.01-0.06
small, 0.06-0.14 medium, >=0.14 large.
"""
import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv('data/cleaned/retail_store_inventory_cleaned.csv', parse_dates=['date'])

def eta_squared(groups):
    all_vals = np.concatenate(groups)
    grand_mean = all_vals.mean()
    ss_total = ((all_vals - grand_mean) ** 2).sum()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    return ss_between / ss_total

def test_grouping(df, col, target='units_sold'):
    groups = [g[target].values for _, g in df.groupby(col, observed=True)]
    f_stat, p_anova = stats.f_oneway(*groups)
    h_stat, p_kw = stats.kruskal(*groups)
    eta2 = eta_squared(groups)
    group_means = df.groupby(col, observed=True)[target].mean().sort_values(ascending=False)
    spread_pct = (group_means.max() - group_means.min()) / group_means.mean() * 100
    return {
        'variable': col,
        'n_groups': len(groups),
        'f_stat': f_stat,
        'p_anova': p_anova,
        'h_stat': h_stat,
        'p_kruskal': p_kw,
        'eta_squared': eta2,
        'group_mean_spread_pct': spread_pct,
    }

results = []
for col in ['store_id', 'product_id', 'category', 'region']:
    r = test_grouping(df, col)
    results.append(r)

res_df = pd.DataFrame(results)
pd.set_option('display.width', 160)
pd.set_option('display.max_columns', None)
print(res_df.to_string(index=False))

print("\nInterpretation (eta-squared, Cohen's guideline: <0.01 negligible):")
for r in results:
    tag = 'NEGLIGIBLE' if r['eta_squared'] < 0.01 else ('SMALL' if r['eta_squared'] < 0.06 else 'MEDIUM/LARGE')
    sig = 'significant' if r['p_anova'] < 0.05 else 'not significant'
    print(f"  {r['variable']:<12} p={r['p_anova']:.2e} ({sig}, huge n)  eta^2={r['eta_squared']:.5f} -> {tag} practical effect"
          f"  | group means span {r['group_mean_spread_pct']:.2f}% of the overall mean")

res_df.to_csv('forecasting/granularity_hypothesis_results.csv', index=False)
print("\nSaved -> forecasting/granularity_hypothesis_results.csv")
