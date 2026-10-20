import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_engine_cloud as get_engine

st.set_page_config(page_title="Market Overview", page_icon="📊", layout="wide")

st.title("Market Overview")
st.caption("Brazilian soybean market at a glance")

engine = get_engine()

# --- Load latest year data ---
latest = pd.read_sql("""
    SELECT year, production_t, area_harvested_ha, yield_kg_ha
    FROM production
    WHERE country = 'BRA' AND crop = 'soybean' AND state_name = 'Brazil'
    ORDER BY year DESC
    LIMIT 1
""", engine)

prev = pd.read_sql("""
    SELECT year, production_t
    FROM production
    WHERE country = 'BRA' AND crop = 'soybean' AND state_name = 'Brazil'
    ORDER BY year DESC
    LIMIT 2
""", engine)

export_share = pd.read_sql("""
    SELECT year, value AS export_share_pct
    FROM indicators
    WHERE metric = 'export_share_pct'
    ORDER BY year DESC
    LIMIT 1
""", engine)

cagr = pd.read_sql("""
    SELECT year, value AS cagr_3yr_pct
    FROM indicators
    WHERE metric = 'production_cagr_3yr_pct'
    ORDER BY year DESC
    LIMIT 1
""", engine)

# --- KPI Cards ---
col1, col2, col3, col4 = st.columns(4)

if len(prev) >= 2:
    yoy = 100 * (prev.iloc[0]["production_t"] - prev.iloc[1]["production_t"]) / prev.iloc[1]["production_t"]
else:
    yoy = 0

col1.metric(
    f"Production ({int(latest.iloc[0]['year'])})",
    f"{latest.iloc[0]['production_t'] / 1e6:,.1f}M t",
    f"{yoy:+.1f}% YoY",
)

col2.metric(
    f"Area Harvested ({int(latest.iloc[0]['year'])})",
    f"{latest.iloc[0]['area_harvested_ha'] / 1e6:,.1f}M ha",
)

col3.metric(
    "Export Share",
    f"{export_share.iloc[0]['export_share_pct']:.1f}%",
    f"({int(export_share.iloc[0]['year'])})",
)

col4.metric(
    "3-Year CAGR",
    f"{cagr.iloc[0]['cagr_3yr_pct']:.2f}%",
    f"({int(cagr.iloc[0]['year'])})",
)

st.divider()

# --- Production over time ---
st.subheader("Soybean Production, 1974–2025")

prod = pd.read_sql("""
    SELECT year, production_t / 1e6 AS production_mt
    FROM production
    WHERE country = 'BRA' AND crop = 'soybean' AND state_name = 'Brazil'
    ORDER BY year
""", engine)

fig = px.line(
    prod, x="year", y="production_mt",
    labels={"year": "Year", "production_mt": "Production (million tonnes)"},
)
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# --- Export share over time ---
st.subheader("Export Share of Production")

exp = pd.read_sql("""
    SELECT year, value AS export_share_pct
    FROM indicators
    WHERE metric = 'export_share_pct'
    ORDER BY year
""", engine)

fig2 = px.line(
    exp, x="year", y="export_share_pct",
    labels={"year": "Year", "export_share_pct": "Export share (%)"},
)
fig2.update_layout(height=350)
st.plotly_chart(fig2, use_container_width=True)