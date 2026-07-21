import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, acf, pacf

daily = pd.read_csv('forecasting/daily_demand.csv', parse_dates=['date'])
y = daily['units_sold'].values

print("Series length:", len(y))
print("Mean:", y.mean(), "Std:", y.std(), "CV:", y.std()/y.mean())

adf_stat, adf_p, *_ = adfuller(y)
print(f"\nADF test (stationarity): stat={adf_stat:.3f}, p={adf_p:.4f} -> {'stationary' if adf_p < 0.05 else 'non-stationary'}")

d1 = np.diff(y)
adf_stat1, adf_p1, *_ = adfuller(d1)
print(f"ADF test on first difference: stat={adf_stat1:.3f}, p={adf_p1:.4f} -> {'stationary' if adf_p1 < 0.05 else 'non-stationary'}")

acf_vals = acf(y, nlags=21, fft=True)
pacf_vals = pacf(y, nlags=21)
print("\nACF lags 1-21:")
print(np.round(acf_vals[1:], 3))
print("\nPACF lags 1-21:")
print(np.round(pacf_vals[1:], 3))

# significance bound ~ 1.96/sqrt(n)
bound = 1.96 / np.sqrt(len(y))
print(f"\n95% significance bound: +-{bound:.3f}")
sig_acf = [i+1 for i, v in enumerate(acf_vals[1:]) if abs(v) > bound]
sig_pacf = [i+1 for i, v in enumerate(pacf_vals[1:]) if abs(v) > bound]
print("Significant ACF lags:", sig_acf)
print("Significant PACF lags:", sig_pacf)

# simple trend check: linear regression slope
from scipy import stats as sps
t = np.arange(len(y))
slope, intercept, r, p, se = sps.linregress(t, y)
print(f"\nLinear trend: slope={slope:.4f} units/day, p={p:.4f}, r^2={r**2:.5f}")
