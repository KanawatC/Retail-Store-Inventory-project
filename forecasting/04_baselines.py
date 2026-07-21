import json
import numpy as np
from utils import load_daily, make_split, metrics

daily = load_daily()
train, val, train_full, test = make_split(daily)

y_train_full = train_full['units_sold'].values
y_test = test['units_sold'].values

results = {}

# 1. Mean / drift baseline: predict the train_full mean for every test day
mean_pred = np.full(len(y_test), y_train_full.mean())
results['mean_baseline'] = {**metrics(y_test, mean_pred), 'description': 'predict historical mean for every day'}

# 2. Naive / persistence: predict last observed train value for the whole horizon
naive_pred = np.full(len(y_test), y_train_full[-1])
results['naive_persistence'] = {**metrics(y_test, naive_pred), 'description': 'predict last known value (flat) for the whole horizon'}

# 3. Seasonal naive (weekly): predict value from 7 days earlier, cycling
seasonal_pred = []
history = list(y_train_full)
for i in range(len(y_test)):
    seasonal_pred.append(history[-7])
    history.append(y_test[i])  # seasonal naive uses true lag-7, walk-forward
results['seasonal_naive_weekly'] = {**metrics(y_test, seasonal_pred), 'description': 'predict value from 7 days earlier (walk-forward)'}

for name, r in results.items():
    print(f"{name:>22}: MAE={r['mae']:.1f}  RMSE={r['rmse']:.1f}  MAPE={r['mape']:.2f}%  bias={r['bias']:+.1f}")

with open('forecasting/results_baselines.json', 'w') as f:
    json.dump({
        'test_dates': test['date'].dt.strftime('%Y-%m-%d').tolist(),
        'y_test': y_test.tolist(),
        'predictions': {
            'mean_baseline': mean_pred.tolist(),
            'naive_persistence': naive_pred.tolist(),
            'seasonal_naive_weekly': [float(x) for x in seasonal_pred],
        },
        'metrics': results,
    }, f, indent=2)
print("\nSaved -> forecasting/results_baselines.json")
