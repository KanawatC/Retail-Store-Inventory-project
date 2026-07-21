import json
import numpy as np
import pandas as pd
from utils import metrics, TEST_SIZE, VAL_SIZE

cat_daily = pd.read_csv('forecasting/daily_demand_by_category.csv', parse_dates=['date'])
categories = sorted(cat_daily['category'].unique())

def split(g):
    n = len(g)
    test = g.iloc[n - TEST_SIZE:].reset_index(drop=True)
    train_full = g.iloc[:n - TEST_SIZE].reset_index(drop=True)
    val = train_full.iloc[len(train_full) - VAL_SIZE:].reset_index(drop=True)
    train = train_full.iloc[:len(train_full) - VAL_SIZE].reset_index(drop=True)
    return train, val, train_full, test

all_results = {}
for cat in categories:
    g = cat_daily[cat_daily['category'] == cat].sort_values('date').reset_index(drop=True)
    train, val, train_full, test = split(g)
    y_train_full = train_full['units_sold'].values.astype(float)
    y_test = test['units_sold'].values.astype(float)

    mean_pred = np.full(len(y_test), y_train_full.mean())
    naive_pred = np.full(len(y_test), y_train_full[-1])

    seasonal_pred = []
    history = list(y_train_full)
    for i in range(len(y_test)):
        seasonal_pred.append(history[-7])
        history.append(y_test[i])

    cat_results = {
        'mean_baseline': {**metrics(y_test, mean_pred), 'pred': mean_pred.tolist()},
        'naive_persistence': {**metrics(y_test, naive_pred), 'pred': naive_pred.tolist()},
        'seasonal_naive_weekly': {**metrics(y_test, seasonal_pred), 'pred': [float(x) for x in seasonal_pred]},
    }
    all_results[cat] = {
        'test_dates': test['date'].dt.strftime('%Y-%m-%d').tolist(),
        'y_test': y_test.tolist(),
        'y_train_full_mean': float(y_train_full.mean()),
        'models': cat_results,
    }
    print(f"{cat:<12}", {k: f"MAE={v['mae']:.1f}" for k, v in cat_results.items()})

with open('forecasting/results_baselines_category.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print("\nSaved -> forecasting/results_baselines_category.json")
