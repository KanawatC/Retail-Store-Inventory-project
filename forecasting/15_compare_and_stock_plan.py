import json
import numpy as np
import pandas as pd

with open('forecasting/results_baselines_category.json') as f:
    BASE = json.load(f)
with open('forecasting/results_arima_category.json') as f:
    ARIMA = json.load(f)
with open('forecasting/results_lstm_category.json') as f:
    LSTM = json.load(f)

categories = sorted(BASE.keys())

rows = []
for cat in categories:
    rows.append({
        'category': cat,
        'mean_mae': BASE[cat]['models']['mean_baseline']['mae'],
        'mean_rmse': BASE[cat]['models']['mean_baseline']['rmse'],
        'mean_mape': BASE[cat]['models']['mean_baseline']['mape'],
        'naive_mae': BASE[cat]['models']['naive_persistence']['mae'],
        'seasonal_mae': BASE[cat]['models']['seasonal_naive_weekly']['mae'],
        'arima_order': tuple(ARIMA[cat]['order']),
        'arima_mae': ARIMA[cat]['metrics']['mae'],
        'arima_rmse': ARIMA[cat]['metrics']['rmse'],
        'arima_mape': ARIMA[cat]['metrics']['mape'],
        'lstm_mae': LSTM['by_category'][cat]['metrics']['mae'],
        'lstm_rmse': LSTM['by_category'][cat]['metrics']['rmse'],
        'lstm_mape': LSTM['by_category'][cat]['metrics']['mape'],
    })

df = pd.DataFrame(rows)
df['best_model'] = df[['mean_mae', 'arima_mae', 'lstm_mae']].idxmin(axis=1).str.replace('_mae', '')
pd.set_option('display.width', 200)
print(df.to_string(index=False))

avg = df[['mean_mae', 'arima_mae', 'lstm_mae']].mean()
print("\nAverage MAE across the 5 categories:")
print(avg.to_string())
lstm_vs_arima = (1 - avg['lstm_mae'] / avg['arima_mae']) * 100
lstm_vs_mean = (1 - avg['lstm_mae'] / avg['mean_mae']) * 100
print(f"\nLSTM vs ARIMA (avg MAE): {lstm_vs_arima:+.1f}%")
print(f"LSTM vs mean baseline (avg MAE): {lstm_vs_mean:+.1f}%")

# --- Practical stock plan: recommended DAILY units per store, per category ---
# Recommendation: use the mean-baseline forecast (most robust / lowest avg error
# across categories - see comparison above) as the chain-wide daily demand
# estimate per category, split evenly across the 5 stores since store has no
# significant effect on demand (within-category eta^2 < 0.001, see diagnostics).
stock_plan = []
for cat in categories:
    chain_daily = BASE[cat]['y_train_full_mean']  # historical mean, most robust estimator here
    stock_plan.append({
        'category': cat,
        'chain_daily_demand_forecast': chain_daily,
        'per_store_daily_stock': chain_daily / 5,
    })
stock_df = pd.DataFrame(stock_plan)
print("\n=== Practical stock plan (equal split across 5 stores) ===")
print(stock_df.to_string(index=False))

df.to_csv('forecasting/comparison_by_category.csv', index=False)
stock_df.to_csv('forecasting/stock_plan.csv', index=False)

with open('forecasting/comparison_summary_category.json', 'w') as f:
    json.dump({
        'table': df.to_dict(orient='records'),
        'avg_mae': avg.to_dict(),
        'lstm_vs_arima_pct': lstm_vs_arima,
        'lstm_vs_mean_pct': lstm_vs_mean,
        'stock_plan': stock_df.to_dict(orient='records'),
        'by_category_series': {
            cat: {
                'test_dates': BASE[cat]['test_dates'],
                'y_test': BASE[cat]['y_test'],
                'mean_baseline': BASE[cat]['models']['mean_baseline']['pred'],
                'arima': ARIMA[cat]['predictions'],
                'lstm': LSTM['by_category'][cat]['predictions'],
            } for cat in categories
        },
    }, f, indent=2)
print("\nSaved -> forecasting/comparison_summary_category.json")
