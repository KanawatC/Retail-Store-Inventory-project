import json
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler

from utils import metrics, TEST_SIZE, VAL_SIZE

SEED = 42
LOOKBACK = 14

np.random.seed(SEED)
tf.random.set_seed(SEED)
tf.keras.utils.set_random_seed(SEED)

cat_daily = pd.read_csv('forecasting/daily_demand_by_category.csv', parse_dates=['date'])
categories = sorted(cat_daily['category'].unique())
n_cat = len(categories)
cat_to_idx = {c: i for i, c in enumerate(categories)}

def split(g):
    n = len(g)
    test = g.iloc[n - TEST_SIZE:].reset_index(drop=True)
    train_full = g.iloc[:n - TEST_SIZE].reset_index(drop=True)
    val = train_full.iloc[len(train_full) - VAL_SIZE:].reset_index(drop=True)
    train = train_full.iloc[:len(train_full) - VAL_SIZE].reset_index(drop=True)
    return train, val, train_full, test

def make_sequences(series_scaled, lookback, cat_onehot):
    X, C, y = [], [], []
    for i in range(lookback, len(series_scaled)):
        X.append(series_scaled[i - lookback:i])
        C.append(cat_onehot)
        y.append(series_scaled[i])
    return np.array(X), np.array(C), np.array(y)

def onehot(cat):
    v = np.zeros(n_cat)
    v[cat_to_idx[cat]] = 1.0
    return v

# ---------- Phase 1: model-selection training (train -> val) ----------
per_cat = {}
X_all, C_all, y_all = [], [], []
Xv_all, Cv_all, yv_all = [], [], []

for cat in categories:
    g = cat_daily[cat_daily['category'] == cat].sort_values('date').reset_index(drop=True)
    train, val, train_full, test = split(g)
    y_train = train['units_sold'].values.astype(float)
    y_val = val['units_sold'].values.astype(float)
    y_train_full = train_full['units_sold'].values.astype(float)
    y_test = test['units_sold'].values.astype(float)

    scaler = StandardScaler().fit(y_train.reshape(-1, 1))
    y_train_s = scaler.transform(y_train.reshape(-1, 1)).flatten()
    context_val = np.concatenate([y_train, y_val])
    context_val_s = scaler.transform(context_val.reshape(-1, 1)).flatten()

    Xtr, Ctr, ytr = make_sequences(y_train_s, LOOKBACK, onehot(cat))
    Xv, Cv, yv = make_sequences(context_val_s, LOOKBACK, onehot(cat))
    Xv, Cv, yv = Xv[-len(y_val):], Cv[-len(y_val):], yv[-len(y_val):]

    X_all.append(Xtr); C_all.append(Ctr); y_all.append(ytr)
    Xv_all.append(Xv); Cv_all.append(Cv); yv_all.append(yv)

    per_cat[cat] = dict(train=train, val=val, train_full=train_full, test=test,
                         y_train=y_train, y_val=y_val, y_train_full=y_train_full, y_test=y_test)

X_all = np.concatenate(X_all)[..., np.newaxis]
C_all = np.concatenate(C_all)
y_all = np.concatenate(y_all)
Xv_all = np.concatenate(Xv_all)[..., np.newaxis]
Cv_all = np.concatenate(Cv_all)
yv_all = np.concatenate(yv_all)

print("Global train sequences:", X_all.shape, "val sequences:", Xv_all.shape)

def build_model():
    seq_in = tf.keras.Input(shape=(LOOKBACK, 1), name='seq')
    cat_in = tf.keras.Input(shape=(n_cat,), name='cat')
    x = tf.keras.layers.LSTM(32, activation='tanh')(seq_in)
    x = tf.keras.layers.Concatenate()([x, cat_in])
    x = tf.keras.layers.Dense(16, activation='relu')(x)
    out = tf.keras.layers.Dense(1)(x)
    m = tf.keras.Model([seq_in, cat_in], out)
    m.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss='mse')
    return m

model = build_model()
model.summary()
early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)
history = model.fit(
    {'seq': X_all, 'cat': C_all}, y_all,
    validation_data=({'seq': Xv_all, 'cat': Cv_all}, yv_all),
    epochs=300, batch_size=32, verbose=0, callbacks=[early_stop],
)
n_epochs_run = len(history.history['loss'])
print(f"Trained {n_epochs_run} epochs. final train_loss={history.history['loss'][-1]:.4f} val_loss={history.history['val_loss'][-1]:.4f}")

# ---------- Phase 2: refit on train_full per category, single global model, blind forecast ----------
X_full_all, C_full_all, y_full_all = [], [], []
scalers_full = {}
for cat in categories:
    y_train_full = per_cat[cat]['y_train_full']
    scaler_full = StandardScaler().fit(y_train_full.reshape(-1, 1))
    scalers_full[cat] = scaler_full
    y_train_full_s = scaler_full.transform(y_train_full.reshape(-1, 1)).flatten()
    Xf, Cf, yf = make_sequences(y_train_full_s, LOOKBACK, onehot(cat))
    X_full_all.append(Xf); C_full_all.append(Cf); y_full_all.append(yf)

X_full_all = np.concatenate(X_full_all)[..., np.newaxis]
C_full_all = np.concatenate(C_full_all)
y_full_all = np.concatenate(y_full_all)

tf.keras.utils.set_random_seed(SEED)
final_model = build_model()
final_model.fit({'seq': X_full_all, 'cat': C_full_all}, y_full_all,
                 epochs=n_epochs_run, batch_size=32, verbose=0)

all_results = {}
for cat in categories:
    y_train_full = per_cat[cat]['y_train_full']
    y_test = per_cat[cat]['y_test']
    scaler_full = scalers_full[cat]
    y_train_full_s = scaler_full.transform(y_train_full.reshape(-1, 1)).flatten()
    window = list(y_train_full_s[-LOOKBACK:])
    c_vec = onehot(cat)
    preds_scaled = []
    for _ in range(len(y_test)):
        x = np.array(window[-LOOKBACK:]).reshape(1, LOOKBACK, 1)
        c = c_vec.reshape(1, n_cat)
        yhat = final_model.predict({'seq': x, 'cat': c}, verbose=0)[0, 0]
        preds_scaled.append(yhat)
        window.append(yhat)
    preds = scaler_full.inverse_transform(np.array(preds_scaled).reshape(-1, 1)).flatten()
    m = metrics(y_test, preds)
    print(f"{cat:<12} LSTM test MAE={m['mae']:.1f} RMSE={m['rmse']:.1f} MAPE={m['mape']:.2f}%")
    all_results[cat] = {
        'test_dates': per_cat[cat]['test']['date'].dt.strftime('%Y-%m-%d').tolist(),
        'y_test': y_test.tolist(),
        'predictions': preds.tolist(),
        'metrics': m,
    }

with open('forecasting/results_lstm_category.json', 'w') as f:
    json.dump({
        'lookback': LOOKBACK,
        'epochs_trained': n_epochs_run,
        'architecture': 'global multi-series LSTM(32) + category one-hot -> Dense(16) -> Dense(1)',
        'by_category': all_results,
    }, f, indent=2)
print("\nSaved -> forecasting/results_lstm_category.json")
