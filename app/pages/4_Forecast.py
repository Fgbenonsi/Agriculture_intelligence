import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_engine_cloud as get_engine

st.set_page_config(page_title="Forecast", page_icon="🤖", layout="wide")

st.title("Yield Forecast")
st.caption("Random Forest model · municipal soybean yield · 2016–2020 test set")

engine = get_engine()

# --- Model summary KPI ---
st.subheader("Model Performance")

col1, col2, col3 = st.columns(3)
col1.metric("R²", "0.03", help="Fraction of variance explained. Near zero = weak model.")
col2.metric("MAE", "460 kg/ha", help="Mean absolute error on the test set.")
col3.metric("RMSE", "606 kg/ha", help="Root mean squared error on the test set.")

st.info(
    "R² = 0.03 means climate and vegetation variables explain only 3% of the variation "
    "in detrended soybean yield. The model is barely better than predicting the average. "
    "Most of the signal is likely in management, pests, genetics, and measurement error — "
    "variables not present in this dataset."
)

st.divider()

# --- Feature importance ---
st.subheader("What Drives the Prediction?")

imp = pd.read_sql("""
    SELECT feature, importance
    FROM soybean_feature_importance
    ORDER BY importance DESC
""", engine)

fig = px.bar(
    imp, x="importance", y="feature", orientation="h",
    labels={"importance": "Importance", "feature": ""},
)
fig.update_layout(height=450, yaxis=dict(autorange="reversed"))
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Actual vs predicted ---
st.subheader("Actual vs. Predicted Yield")

pred = pd.read_sql("""
    SELECT harvested, state, actual_yield_corrected, predicted_yield_corrected
    FROM soybean_forecasts
""", engine)

fig2 = px.scatter(
    pred, x="actual_yield_corrected", y="predicted_yield_corrected",
    color="state", opacity=0.4,
    labels={
        "actual_yield_corrected": "Actual yield anomaly (kg/ha)",
        "predicted_yield_corrected": "Predicted yield anomaly (kg/ha)",
        "state": "State",
    },
)
fig2.add_shape(
    type="line", line=dict(dash="dash", color="gray"),
    x0=pred["actual_yield_corrected"].min(), x1=pred["actual_yield_corrected"].max(),
    y0=pred["actual_yield_corrected"].min(), y1=pred["actual_yield_corrected"].max(),
)
fig2.update_layout(height=500)
st.plotly_chart(fig2, use_container_width=True)

st.caption("Points on the dashed line are perfect predictions. Spread indicates model error.")