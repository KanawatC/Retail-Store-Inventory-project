import numpy as np
import pandas as pd

TEST_SIZE = 90
VAL_SIZE = 60

def load_daily():
    daily = pd.read_csv('forecasting/daily_demand.csv', parse_dates=['date'])
    return daily

def make_split(daily):
    n = len(daily)
    test = daily.iloc[n - TEST_SIZE:].reset_index(drop=True)
    train_full = daily.iloc[:n - TEST_SIZE].reset_index(drop=True)
    val = train_full.iloc[len(train_full) - VAL_SIZE:].reset_index(drop=True)
    train = train_full.iloc[:len(train_full) - VAL_SIZE].reset_index(drop=True)
    return train, val, train_full, test

def metrics(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    err = y_true - y_pred
    mae = np.mean(np.abs(err))
    rmse = np.sqrt(np.mean(err ** 2))
    mape = np.mean(np.abs(err) / y_true) * 100
    bias = np.mean(err)
    return {'mae': mae, 'rmse': rmse, 'mape': mape, 'bias': bias}
