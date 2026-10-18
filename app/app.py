import streamlit as st

st.set_page_config(
    page_title="Agriculture Intelligence",
    page_icon="🌱",
    layout="wide",
)

st.title("Agriculture Intelligence")
st.subheader("Brazilian Soybean Market Monitor")

st.markdown("""
This application tracks Brazil's soybean market using public data from:

- **IBGE/SIDRA** — production, area, yield (1974–2025)
- **Comex Stat** — exports (2015–2025)

Use the sidebar to navigate between pages.
""")

st.sidebar.success("Select a page above.")