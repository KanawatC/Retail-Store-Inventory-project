import json
import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from utils import load_daily, make_split, metrics

warnings.filterwarnings('ignore')

daily = load_daily()
train, val, train_full, test = make_split(daily)

y_train = train['units_sold'].values.astype(float)
y_val = val['units_sold'].values.astype(float)
y_train_full = train_full['units_sold'].values.astype(float)
y_test = test['units_sold'].values.astype(float)

# --- order selection: grid search (p,d,q) by AIC, validated by 1-step val MAE ---
print("Grid searching ARIMA(p,d,q) order on train, validating on val period...")
candidates = []
for d in [0, 1]:
    for p in range(0, 5):
        for q in range(0, 5):
            if p == 0 and q == 0 and d == 0:
                pass  # still allow the "white noise / mean" model as a candidate
            try:
                model = ARIMA(y_train, order=(p, d, q),
                               enforce_stationarity=False, enforce_invertibility=False)
                fit = model.fit()
                # forecast the val horizon, static (no peeking)
                val_fc = fit.forecast(steps=len(y_val))
                val_mae = np.mean(np.abs(y_val - val_fc))
                candidates.append({'p': p, 'd': d, 'q': q, 'aic': fit.aic, 'val_mae': val_mae})
            except Exception:
                continue

cand_df = pd.DataFrame(candidates).sort_values('val_mae')
print(cand_df.head(10).to_string(index=False))

best = cand_df.iloc[0]
order = (int(best['p']), int(best['d']), int(best['q']))
print(f"\nSelected order by validation MAE: ARIMA{order}  (AIC={best['aic']:.1f}, val_MAE={best['val_mae']:.1f})")

# also show the best-AIC model for comparison
best_aic = cand_df.sort_values('aic').iloc[0]
print(f"Best-AIC order for reference: ARIMA({int(best_aic['p'])},{int(best_aic['d'])},{int(best_aic['q'])})  AIC={best_aic['aic']:.1f}, val_MAE={best_aic['val_mae']:.1f}")

# --- refit on train_full (train+val), forecast the held-out test horizon ---
final_model = ARIMA(y_train_full, order=order, enforce_stationarity=False, enforce_invertibility=False)
final_fit = final_model.fit()
print(final_fit.summary())

test_fc = final_fit.get_forecast(steps=len(y_test))
test_pred = test_fc.predicted_mean
test_ci = test_fc.conf_int(alpha=0.05)

m = metrics(y_test, test_pred)
print(f"\nARIMA{order} on held-out test ({len(y_test)} days): MAE={m['mae']:.1f}  RMSE={m['rmse']:.1f}  MAPE={m['mape']:.2f}%  bias={m['bias']:+.1f}")

with open('forecasting/results_arima.json', 'w') as f:
    json.dump({
        'order': list(order),
        'aic': float(best['aic']),
        'grid_top10': cand_df.head(10).to_dict(orient='records'),
        'test_dates': test['date'].dt.strftime('%Y-%m-%d').tolist(),
        'y_test': y_test.tolist(),
        'predictions': test_pred.tolist(),
        'ci_lower': test_ci[:, 0].tolist(),
        'ci_upper': test_ci[:, 1].tolist(),
        'metrics': m,
    }, f, indent=2)
print("\nSaved -> forecasting/results_arima.json")
