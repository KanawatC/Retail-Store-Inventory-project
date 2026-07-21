import json
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler

from utils import load_daily, make_split, metrics

SEED = 42
np.random.seed(SEED)
tf.random.set_seed(SEED)

LOOKBACK = 14

daily = load_daily()
train, val, train_full, test = make_split(daily)

y_train = train['units_sold'].values.astype(float)
y_val = val['units_sold'].values.astype(float)
y_train_full = train_full['units_sold'].values.astype(float)
y_test = test['units_sold'].values.astype(float)

# scaler fit on train ONLY (val/test are unseen)
scaler = StandardScaler()
y_train_s = scaler.fit_transform(y_train.reshape(-1, 1)).flatten()

def make_sequences(series_scaled, lookback):
    X, y = [], []
    for i in range(lookback, len(series_scaled)):
        X.append(series_scaled[i - lookback:i])
        y.append(series_scaled[i])
    return np.array(X)[..., np.newaxis], np.array(y)

X_train, y_train_seq = make_sequences(y_train_s, LOOKBACK)

# val sequences: need last LOOKBACK train points as context for the first val predictions
context_for_val = np.concatenate([y_train, y_val])
context_for_val_s = scaler.transform(context_for_val.reshape(-1, 1)).flatten()
X_val, y_val_seq = make_sequences(context_for_val_s, LOOKBACK)
# keep only the sequences whose target falls within the val period
X_val = X_val[-len(y_val):]
y_val_seq = y_val_seq[-len(y_val):]

print("Train sequences:", X_train.shape, "Val sequences:", X_val.shape)

tf.keras.utils.set_random_seed(SEED)
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(LOOKBACK, 1)),
    tf.keras.layers.LSTM(32, activation='tanh'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1),
])
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3), loss='mse')
model.summary()

early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True)
history = model.fit(
    X_train, y_train_seq,
    validation_data=(X_val, y_val_seq),
    epochs=300, batch_size=16, verbose=0,
    callbacks=[early_stop],
)
n_epochs_run = len(history.history['loss'])
print(f"Trained for {n_epochs_run} epochs (early stopping patience=20)")
print(f"Final train loss: {history.history['loss'][-1]:.4f}  val loss: {history.history['val_loss'][-1]:.4f}")

# --- refit scaler on train_full, retrain final model on train_full, then blind multi-step forecast the test horizon ---
scaler_full = StandardScaler()
y_train_full_s = scaler_full.fit_transform(y_train_full.reshape(-1, 1)).flatten()
X_train_full, y_train_full_seq = make_sequences(y_train_full_s, LOOKBACK)

tf.keras.utils.set_random_seed(SEED)
final_model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(LOOKBACK, 1)),
    tf.keras.layers.LSTM(32, activation='tanh'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1),
])
final_model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3), loss='mse')
final_model.fit(X_train_full, y_train_full_seq, epochs=n_epochs_run, batch_size=16, verbose=0)

# blind iterative multi-step forecast over the test horizon (no peeking at y_test)
window = list(y_train_full_s[-LOOKBACK:])
preds_scaled = []
for _ in range(len(y_test)):
    x = np.array(window[-LOOKBACK:]).reshape(1, LOOKBACK, 1)
    yhat = final_model.predict(x, verbose=0)[0, 0]
    preds_scaled.append(yhat)
    window.append(yhat)

preds = scaler_full.inverse_transform(np.array(preds_scaled).reshape(-1, 1)).flatten()

m = metrics(y_test, preds)
print(f"\nLSTM (lookback={LOOKBACK}) on held-out test ({len(y_test)} days): "
      f"MAE={m['mae']:.1f}  RMSE={m['rmse']:.1f}  MAPE={m['mape']:.2f}%  bias={m['bias']:+.1f}")

with open('forecasting/results_lstm.json', 'w') as f:
    json.dump({
        'lookback': LOOKBACK,
        'epochs_trained': n_epochs_run,
        'final_train_loss': float(history.history['loss'][-1]),
        'final_val_loss': float(history.history['val_loss'][-1]),
        'test_dates': test['date'].dt.strftime('%Y-%m-%d').tolist(),
        'y_test': y_test.tolist(),
        'predictions': preds.tolist(),
        'metrics': m,
    }, f, indent=2)
print("\nSaved -> forecasting/results_lstm.json")
