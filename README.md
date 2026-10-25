# Agriculture Intelligence

A data pipeline and dashboard for tracking Brazil's soybean market using public data.

**Live app:** [https://agricultureintelligence-zs5egoryds8wcb9rfb5itr.streamlit.app](https://agricultureintelligence-zs5egoryds8wcb9rfb5itr.streamlit.app)

## What It Does

Brazil is the world's largest soybean exporter, but the data is scattered across government websites. This project pulls production data from IBGE and trade data from Comex Stat, stores it in PostgreSQL, computes market indicators, and serves them through an interactive Streamlit dashboard.

## Dashboard Pages

**Market Overview**
- Latest production, area harvested, and export share
- Production trend (1974–2025)
- Export share of production

**Trend Analysis**
- Area growth vs. yield growth
- Year-over-year production growth
- Anomaly alerts (years where growth was statistically unusual)

## Data Sources

| Source | Data | Coverage |
|:---|:---|:---|
| IBGE/SIDRA (table 1612) | Soybean production, area, yield | 1974–2025 |
| Comex Stat | Soybean exports (NCM 1201) | 1997–2025 |

## Pipeline

Two Python scripts fetch data from IBGE and Comex Stat, load it into PostgreSQL, compute indicators in SQL, and serve them through Streamlit.

| Layer | Files | What it does |
|:---|:---|:---|
| Ingestion | `harvest/harvest_ibge.py`, `harvest/harvest_comex.py` | Fetch raw data and load into PostgreSQL |
| Transformation | `sql/indicators.sql`, `sql/anomalies.sql` | Compute YoY growth, CAGR, export share, z-scores |
| Presentation | `app/app.py`, `app/pages/` | Streamlit dashboard |

## Key Findings

- Brazil's soybean area planted grew every year from 2016 to 2025. Growth is structurally driven by land expansion, not yield improvement.
- Yield is the volatile component: +15.9% in 2023, −14.2% in 2022.
- Export share is stable at roughly 65% of production.
- 2023 was a statistically unusual production surge (z-score +1.83 relative to the previous decade).

## Stack

Python · PostgreSQL · SQLAlchemy · Streamlit · Plotly · pandas

## Run Locally

**1. Clone the repository**

```bash
git clone https://github.com/Fgbenonsi/Agriculture_intelligence.git
cd Agriculture_intelligence
```

**2. Create a virtual environment and install dependencies**&

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Create .env with your database connection**

```bash
DATABASE_URL=postgresql+psycopg2://user:password@host:port/database
```

**4. Run the app**

```bash
streamlit run app/app.py
```
