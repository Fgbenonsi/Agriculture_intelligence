import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db import get_engine

st.set_page_config(page_title="Trend Analysis", page_icon="📈", layout="wide")

st.title("Trend Analysis")
st.caption("Where does Brazil's soybean growth come from?")

engine = get_engine()

# --- Area vs Yield growth ---
st.subheader("Area vs. Yield Growth")

growth = pd.read_sql("""
    SELECT
        year,
        MAX(CASE WHEN metric = 'area_yoy_pct' THEN value END) AS area_yoy,
        MAX(CASE WHEN metric = 'yield_yoy_pct' THEN value END) AS yield_yoy
    FROM indicators
    WHERE metric IN ('area_yoy_pct', 'yield_yoy_pct')
      AND year >= 2000
    GROUP BY year
    ORDER BY year
""", engine)

fig = go.Figure()
fig.add_trace(go.Bar(x=growth["year"], y=growth["area_yoy"], name="Area growth %"))
fig.add_trace(go.Bar(x=growth["year"], y=growth["yield_yoy"], name="Yield growth %"))
fig.update_layout(
    barmode="group",
    xaxis_title="Year",
    yaxis_title="YoY growth (%)",
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
**Reading this chart:** Area growth is consistently positive — Brazil keeps
expanding soybean area every year. Yield growth swings between positive and
negative, driven by weather. Production growth is the combination of the two.
""")

st.divider()

# --- YoY production growth ---
st.subheader("Production Growth, Year over Year")

yoy = pd.read_sql("""
    SELECT year, value AS yoy_pct
    FROM indicators
    WHERE metric = 'production_yoy_pct'
      AND year >= 2000
    ORDER BY year
""", engine)

fig2 = px.line(
    yoy, x="year", y="yoy_pct",
    labels={"year": "Year", "yoy_pct": "YoY growth (%)"},
)
fig2.add_hline(y=0, line_dash="dash", line_color="gray")
fig2.update_layout(height=350)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- Anomaly alerts ---
st.subheader("Anomaly Alerts")
st.caption("Years where growth was unusual relative to the previous 10 years")

anom = pd.read_sql("""
    SELECT year, value AS yoy_pct, z_score, severity
    FROM anomalies
    WHERE metric = 'production_yoy_zscore_10y'
    ORDER BY year DESC
""", engine)

if len(anom) == 0:
    st.info("No anomalies detected.")
else:
    anom["direction"] = anom["yoy_pct"].apply(lambda x: "📈 Surge" if x > 0 else "📉 Dip")
    st.dataframe(
        anom[["year", "direction", "yoy_pct", "z_score", "severity"]],
        use_container_width=True,
        hide_index=True,
    )