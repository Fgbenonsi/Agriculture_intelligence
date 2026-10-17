-- Agriculture Intelligence - Database Schema
-- Database: agri_intel
-- Purpose: Store production, trade, and computed indicators for agricultural market analysis

-- ============================================
-- PRODUCTION TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS production (
    id SERIAL PRIMARY KEY,
    country VARCHAR(3) NOT NULL DEFAULT 'BRA',
    state_code VARCHAR(2),
    state_name VARCHAR(50),
    municipality_code VARCHAR(10),
    municipality_name VARCHAR(100),
    year INT NOT NULL,
    crop VARCHAR(50) NOT NULL DEFAULT 'soybean',
    production_t NUMERIC,
    area_planted_ha NUMERIC,
    area_harvested_ha NUMERIC,
    yield_kg_ha NUMERIC,
    source VARCHAR(30) DEFAULT 'IBGE/SIDRA',
    retrieved_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_production_year ON production(year);
CREATE INDEX IF NOT EXISTS idx_production_crop ON production(crop);
CREATE INDEX IF NOT EXISTS idx_production_state ON production(state_code);
CREATE INDEX IF NOT EXISTS idx_production_country ON production(country);

-- ============================================
-- TRADE TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS trade (
    id SERIAL PRIMARY KEY,
    country VARCHAR(3) NOT NULL DEFAULT 'BRA',
    year INT NOT NULL,
    month INT,
    flow VARCHAR(10) NOT NULL CHECK (flow IN ('export', 'import')),
    ncm_code VARCHAR(10),
    ncm_description VARCHAR(200),
    state_code VARCHAR(2),
    partner_country VARCHAR(3),
    value_usd NUMERIC,
    volume_kg NUMERIC,
    crop VARCHAR(50) DEFAULT 'soybean',
    source VARCHAR(30) DEFAULT 'Comex Stat',
    retrieved_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trade_year ON trade(year);
CREATE INDEX IF NOT EXISTS idx_trade_flow ON trade(flow);
CREATE INDEX IF NOT EXISTS idx_trade_crop ON trade(crop);

-- ============================================
-- INDICATORS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS indicators (
    id SERIAL PRIMARY KEY,
    country VARCHAR(3) NOT NULL DEFAULT 'BRA',
    scope VARCHAR(20) NOT NULL,
    scope_code VARCHAR(10) NOT NULL,
    crop VARCHAR(50) NOT NULL DEFAULT 'soybean',
    year INT NOT NULL,
    metric VARCHAR(50) NOT NULL,
    value NUMERIC,
    computed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_indicators_year ON indicators(year);
CREATE INDEX IF NOT EXISTS idx_indicators_metric ON indicators(metric);
CREATE INDEX IF NOT EXISTS idx_indicators_crop ON indicators(crop);

-- ============================================
-- ANOMALIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    country VARCHAR(3) NOT NULL DEFAULT 'BRA',
    scope VARCHAR(20) NOT NULL,
    scope_code VARCHAR(10) NOT NULL,
    crop VARCHAR(50) NOT NULL DEFAULT 'soybean',
    year INT NOT NULL,
    metric VARCHAR(50) NOT NULL,
    value NUMERIC,
    z_score NUMERIC,
    severity VARCHAR(10) CHECK (severity IN ('low', 'medium', 'high')),
    detected_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_anomalies_year ON anomalies(year);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity);



SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;