import json
import pandas as pd

with open('forecasting/results_baselines.json') as f:
    B = json.load(f)
with open('forecasting/results_arima.json') as f:
    A = json.load(f)
with open('forecasting/results_lstm.json') as f:
    L = json.load(f)

rows = []
for name, key in [('Historical mean', 'mean_baseline'), ('Naive (persistence)', 'naive_persistence'),
                   ('Seasonal naive (weekly)', 'seasonal_naive_weekly')]:
    m = B['metrics'][key]
    rows.append({'model': name, **{k: m[k] for k in ['mae', 'rmse', 'mape', 'bias']}})

rows.append({'model': f"ARIMA{tuple(A['order'])}", **{k: A['metrics'][k] for k in ['mae', 'rmse', 'mape', 'bias']}})
rows.append({'model': f"LSTM (lookback={L['lookback']})", **{k: L['metrics'][k] for k in ['mae', 'rmse', 'mape', 'bias']}})

summary = pd.DataFrame(rows).sort_values('mae').reset_index(drop=True)
pd.set_option('display.width', 160)
print(summary.to_string(index=False))

lstm_vs_arima_mae = (1 - L['metrics']['mae'] / A['metrics']['mae']) * 100
lstm_vs_mean_mae = (1 - L['metrics']['mae'] / B['metrics']['mean_baseline']['mae']) * 100
print(f"\nLSTM vs ARIMA: {lstm_vs_arima_mae:+.1f}% MAE change")
print(f"LSTM vs historical-mean baseline: {lstm_vs_mean_mae:+.1f}% MAE change")

with open('forecasting/comparison_summary.json', 'w') as f:
    json.dump({
        'table': summary.to_dict(orient='records'),
        'test_dates': A['test_dates'],
        'y_test': A['y_test'],
        'series': {
            'Historical mean': B['predictions']['mean_baseline'],
            'ARIMA': A['predictions'],
            'LSTM': L['predictions'],
        },
        'lstm_vs_arima_mae_pct': lstm_vs_arima_mae,
        'lstm_vs_mean_mae_pct': lstm_vs_mean_mae,
    }, f, indent=2)
print("\nSaved -> forecasting/comparison_summary.json")
