import json
import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from utils import metrics, TEST_SIZE, VAL_SIZE

warnings.filterwarnings('ignore')

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
    y_train = train['units_sold'].values.astype(float)
    y_val = val['units_sold'].values.astype(float)
    y_train_full = train_full['units_sold'].values.astype(float)
    y_test = test['units_sold'].values.astype(float)

    candidates = []
    for d in [0, 1]:
        for p in range(0, 4):
            for q in range(0, 4):
                try:
                    fit = ARIMA(y_train, order=(p, d, q), enforce_stationarity=False, enforce_invertibility=False).fit()
                    val_fc = fit.forecast(steps=len(y_val))
                    val_mae = np.mean(np.abs(y_val - val_fc))
                    candidates.append({'p': p, 'd': d, 'q': q, 'aic': fit.aic, 'val_mae': val_mae})
                except Exception:
                    continue
    cand_df = pd.DataFrame(candidates).sort_values('val_mae')
    best = cand_df.iloc[0]
    order = (int(best['p']), int(best['d']), int(best['q']))

    final_fit = ARIMA(y_train_full, order=order, enforce_stationarity=False, enforce_invertibility=False).fit()
    test_fc = final_fit.get_forecast(steps=len(y_test))
    test_pred = test_fc.predicted_mean
    m = metrics(y_test, test_pred)

    print(f"{cat:<12} order={order}  val_MAE={best['val_mae']:.1f}  test_MAE={m['mae']:.1f}  test_RMSE={m['rmse']:.1f}  test_MAPE={m['mape']:.2f}%")

    all_results[cat] = {
        'order': list(order),
        'aic': float(best['aic']),
        'test_dates': test['date'].dt.strftime('%Y-%m-%d').tolist(),
        'y_test': y_test.tolist(),
        'predictions': test_pred.tolist(),
        'metrics': m,
    }

with open('forecasting/results_arima_category.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print("\nSaved -> forecasting/results_arima_category.json")
