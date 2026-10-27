import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_engine_cloud as get_engine

st.set_page_config(page_title="Weather", page_icon="🌦️", layout="wide")

st.title("Weather")
st.caption("INMET station data, 2000–2025")

engine = get_engine()

# --- Station selector ---
stations = pd.read_sql("""
    SELECT DISTINCT estacao, uf
    FROM weather
    ORDER BY estacao
""", engine)

station_options = stations["estacao"].tolist()
selected = st.selectbox("Station", station_options)

# --- Latest year KPI ---
latest = pd.read_sql(f"""
    SELECT
        EXTRACT(YEAR FROM data_hora)::int AS year,
        ROUND(AVG(temperatura_maxima)::numeric, 1) AS avg_temp_max,
        ROUND(AVG(temperatura_minima)::numeric, 1) AS avg_temp_min,
        ROUND(SUM(precipitacao)::numeric, 1) AS total_rain_mm
    FROM weather
    WHERE estacao = '{selected}'
    GROUP BY year
    ORDER BY year DESC
    LIMIT 1
""", engine)

col1, col2, col3 = st.columns(3)
col1.metric(f"Avg Max Temp ({int(latest.iloc[0]['year'])})", f"{latest.iloc[0]['avg_temp_max']} °C")
col2.metric(f"Avg Min Temp ({int(latest.iloc[0]['year'])})", f"{latest.iloc[0]['avg_temp_min']} °C")
col3.metric(f"Total Rain ({int(latest.iloc[0]['year'])})", f"{latest.iloc[0]['total_rain_mm']} mm")

st.divider()

# --- Temperature over time (monthly average) ---
st.subheader("Temperature, Monthly Average")

temp = pd.read_sql(f"""
    SELECT
        DATE_TRUNC('month', data_hora)::date AS month,
        AVG(temperatura_maxima)::numeric AS temp_max,
        AVG(temperatura_minima)::numeric AS temp_min
    FROM weather
    WHERE estacao = '{selected}'
    GROUP BY month
    ORDER BY month
""", engine)

fig = px.line(
    temp, x="month", y=["temp_max", "temp_min"],
    labels={"value": "Temperature (°C)", "month": "Month", "variable": "Series"},
)
fig.update_layout(height=400, legend_title="")
st.plotly_chart(fig, use_container_width=True)

# --- Rainfall over time (monthly total) ---
st.subheader("Rainfall, Monthly Total")

rain = pd.read_sql(f"""
    SELECT
        DATE_TRUNC('month', data_hora)::date AS month,
        SUM(precipitacao)::numeric AS rain_mm
    FROM weather
    WHERE estacao = '{selected}'
    GROUP BY month
    ORDER BY month
""", engine)

fig2 = px.bar(
    rain, x="month", y="rain_mm",
    labels={"rain_mm": "Rainfall (mm)", "month": "Month"},
)
fig2.update_layout(height=350)
st.plotly_chart(fig2, use_container_width=True)

st.caption(f"Data source: INMET BDMEP · Station: {selected}")