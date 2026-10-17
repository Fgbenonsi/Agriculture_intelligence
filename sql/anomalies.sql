-- ============================================
-- ANOMALIES: Rolling 10-Year Z-Score on YoY Growth
-- ============================================
-- Flags years where production growth is unusual relative to
-- the previous 10 years, not the full history.

INSERT INTO anomalies (country, scope, scope_code, crop, year, metric, value, z_score, severity)
WITH yoy AS (
    SELECT
        year,
        value AS yoy_pct
    FROM indicators
    WHERE metric = 'production_yoy_pct'
),
rolling AS (
    SELECT
        year,
        yoy_pct,
        AVG(yoy_pct) OVER (
            ORDER BY year
            ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING
        ) AS mean_10y,
        STDDEV(yoy_pct) OVER (
            ORDER BY year
            ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING
        ) AS std_10y
    FROM yoy
),
scored AS (
    SELECT
        year,
        yoy_pct,
        (yoy_pct - mean_10y) / NULLIF(std_10y, 0) AS z
    FROM rolling
    WHERE mean_10y IS NOT NULL AND std_10y IS NOT NULL
)
SELECT
    'BRA' AS country,
    'national' AS scope,
    'BR' AS scope_code,
    'soybean' AS crop,
    year,
    'production_yoy_zscore_10y' AS metric,
    ROUND(yoy_pct, 2) AS value,
    ROUND(z, 2) AS z_score,
    CASE
        WHEN ABS(z) >= 2 THEN 'high'
        WHEN ABS(z) >= 1.5 THEN 'medium'
        ELSE 'low'
    END AS severity
FROM scored
WHERE ABS(z) >= 1.5
ORDER BY year DESC;


SELECT year, value AS yoy_pct, z_score, severity
FROM anomalies
WHERE metric = 'production_yoy_zscore_10y'
ORDER BY year DESC; 