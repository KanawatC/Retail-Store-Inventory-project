"""
Add the CSV's pre-existing `demand_forecast` column as a fourth comparison
point, at the same category-daily grain used for the mean/ARIMA/LSTM models:
sum demand_forecast across all stores and products within a category, per
day, then score it against actual units_sold on the same 90-day test window
used everywhere else in Challenge 1.
"""
import json
import numpy as np
import pandas as pd
from utils import metrics, TEST_SIZE

df = pd.read_csv('data/cleaned/retail_store_inventory_cleaned.csv', parse_dates=['date'])

cat_forecast_daily = df.groupby(['category', 'date'], observed=True).agg(
    units_sold=('units_sold', 'sum'),
    demand_forecast=('demand_forecast', 'sum'),
).reset_index().sort_values(['category', 'date'])

categories = sorted(cat_forecast_daily['category'].unique())

with open('forecasting/comparison_summary_category.json') as f:
    CMP = json.load(f)

results = {}
for cat in categories:
    g = cat_forecast_daily[cat_forecast_daily['category'] == cat].sort_values('date').reset_index(drop=True)
    n = len(g)
    train = g.iloc[:n - TEST_SIZE].reset_index(drop=True)
    test = g.iloc[n - TEST_SIZE:].reset_index(drop=True)

    y_test = test['units_sold'].values.astype(float)
    old_forecast = test['demand_forecast'].values.astype(float)

    # sanity: test dates must line up with the other models' test window
    expected_dates = CMP['by_category_series'][cat]['test_dates']
    actual_dates = test['date'].dt.strftime('%Y-%m-%d').tolist()
    assert actual_dates == expected_dates, f"date mismatch for {cat}"
    expected_y = np.array(CMP['by_category_series'][cat]['y_test'])
    assert np.allclose(y_test, expected_y), f"y_test mismatch for {cat}"

    m = metrics(y_test, old_forecast)

    # bias-corrected version: estimate the mean bias on TRAIN only (no test
    # leakage), then apply that fixed correction to the test-period forecast
    train_bias = (train['units_sold'].values.astype(float) - train['demand_forecast'].values.astype(float)).mean()
    old_forecast_corrected = old_forecast + train_bias
    m_corrected = metrics(y_test, old_forecast_corrected)

    results[cat] = {
        'test_dates': actual_dates,
        'y_test': y_test.tolist(),
        'old_forecast_column': old_forecast.tolist(),
        'old_forecast_corrected': old_forecast_corrected.tolist(),
        'train_bias_correction': float(train_bias),
        'metrics': m,
        'metrics_corrected': m_corrected,
    }
    print(f"{cat:<12} raw: MAE={m['mae']:.1f} bias={m['bias']:+.1f}   |   "
          f"bias-corrected (+{train_bias:.1f}): MAE={m_corrected['mae']:.1f} bias={m_corrected['bias']:+.1f}")

avg_mae = np.mean([results[c]['metrics']['mae'] for c in categories])
avg_rmse = np.mean([results[c]['metrics']['rmse'] for c in categories])
avg_mape = np.mean([results[c]['metrics']['mape'] for c in categories])
avg_bias = np.mean([results[c]['metrics']['bias'] for c in categories])

avg_mae_corr = np.mean([results[c]['metrics_corrected']['mae'] for c in categories])
avg_rmse_corr = np.mean([results[c]['metrics_corrected']['rmse'] for c in categories])
avg_mape_corr = np.mean([results[c]['metrics_corrected']['mape'] for c in categories])
avg_bias_corr = np.mean([results[c]['metrics_corrected']['bias'] for c in categories])

print(f"\n{'Average (raw)':<20} MAE={avg_mae:.1f}  RMSE={avg_rmse:.1f}  MAPE={avg_mape:.2f}%  bias={avg_bias:+.1f}")
print(f"{'Average (corrected)':<20} MAE={avg_mae_corr:.1f}  RMSE={avg_rmse_corr:.1f}  MAPE={avg_mape_corr:.2f}%  bias={avg_bias_corr:+.1f}")

print("\nFor reference, this run's other average MAEs (from comparison_summary_category.json):")
print("  mean baseline:", CMP['avg_mae']['mean_mae'])
print("  ARIMA:        ", CMP['avg_mae']['arima_mae'])
print("  LSTM:         ", CMP['avg_mae']['lstm_mae'])

new_vs_old = {
    'mean_vs_old_raw_pct': (1 - CMP['avg_mae']['mean_mae'] / avg_mae) * 100,
    'arima_vs_old_raw_pct': (1 - CMP['avg_mae']['arima_mae'] / avg_mae) * 100,
    'lstm_vs_old_raw_pct': (1 - CMP['avg_mae']['lstm_mae'] / avg_mae) * 100,
    'mean_vs_old_corrected_pct': (1 - CMP['avg_mae']['mean_mae'] / avg_mae_corr) * 100,
    'arima_vs_old_corrected_pct': (1 - CMP['avg_mae']['arima_mae'] / avg_mae_corr) * 100,
    'lstm_vs_old_corrected_pct': (1 - CMP['avg_mae']['lstm_mae'] / avg_mae_corr) * 100,
}
print("\nMAE change of each new model relative to the existing forecast column (positive = new model is better):")
for k, v in new_vs_old.items():
    print(f"  {k}: {v:+.1f}%")

with open('forecasting/results_old_forecast_category.json', 'w') as f:
    json.dump({
        'by_category': results,
        'avg_mae': avg_mae, 'avg_rmse': avg_rmse, 'avg_mape': avg_mape, 'avg_bias': avg_bias,
        'avg_mae_corrected': avg_mae_corr, 'avg_rmse_corrected': avg_rmse_corr,
        'avg_mape_corrected': avg_mape_corr, 'avg_bias_corrected': avg_bias_corr,
        'comparison_vs_new_models': new_vs_old,
    }, f, indent=2)
print("\nSaved -> forecasting/results_old_forecast_category.json")
