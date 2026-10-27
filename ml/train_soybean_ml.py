import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

df = pd.read_sql("SELECT * FROM soybean_ml_annual", engine)

features = [
    "total_rainfall", "avg_tmin", "avg_tmax", "total_hot_days",
    "total_lowrain_days", "avg_oni", "soy_area",
    "avg_ndvi", "avg_evi", "avg_cvi", "avg_gli",
    "avg_spi1", "avg_spi3", "avg_sti1", "total_etp", "total_def",
    "previous_yield",
]
target = "yield_trend_corrected"

df = df.dropna(subset=features + [target])

train = df[df["harvested"] <= 2015]
test = df[df["harvested"] > 2015]

X_train, y_train = train[features], train[target]
X_test, y_test = test[features], test[target]

print(f"Train: {len(train)} rows ({train['harvested'].min()}–{train['harvested'].max()})")
print(f"Test:  {len(test)} rows ({test['harvested'].min()}–{test['harvested'].max()})")

model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print(f"\nMAE:  {mean_absolute_error(y_test, y_pred):.0f} kg/ha")
print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.0f} kg/ha")
print(f"R²:   {r2_score(y_test, y_pred):.2f}")

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_.round(4),
}).sort_values("importance", ascending=False)
print("\nTop 10 features:")
print(importance.head(10).to_string(index=False))

# --- Save predictions and feature importance ---
pred_df = pd.DataFrame({
    "harvested": test["harvested"].values,
    "code": test["code"].values,
    "state": test["state"].values,
    "county": test["county"].values,
    "actual_yield_corrected": test[target].values,
    "predicted_yield_corrected": y_pred.round(2),
})

with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS soybean_forecasts"))
pred_df.to_sql("soybean_forecasts", engine, index=False)
print(f"\nSaved {len(pred_df)} predictions to soybean_forecasts")

with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS soybean_feature_importance"))
importance.to_sql("soybean_feature_importance", engine, index=False)
print("Saved feature importance")