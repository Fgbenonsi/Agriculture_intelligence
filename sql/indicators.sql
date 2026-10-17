-- ============================================
-- INDICATORS: YoY Production Growth
-- ============================================
-- Computes year-over-year production growth for Brazil soybeans
-- and stores it in the indicators table.

INSERT INTO indicators (country, scope, scope_code, crop, year, metric, value)
SELECT
    'BRA' AS country,
    'national' AS scope,
    'BR' AS scope_code,
    'soybean' AS crop,
    year,
    'production_yoy_pct' AS metric,
    ROUND(
        100.0 * (production_t - LAG(production_t) OVER (ORDER BY year))
        / NULLIF(LAG(production_t) OVER (ORDER BY year), 0),
        2
    ) AS value
FROM production
WHERE country = 'BRA' AND crop = 'soybean' AND state_name = 'Brazil'
ORDER BY year;



SELECT year, value AS yoy_pct
FROM indicators
WHERE metric = 'production_yoy_pct'
ORDER BY year DESC
LIMIT 10;


----Import share indicator

-- ============================================
-- INDICATORS: Export Share of Production
-- ============================================

INSERT INTO indicators (country, scope, scope_code, crop, year, metric, value)
SELECT
    'BRA' AS country,
    'national' AS scope,
    'BR' AS scope_code,
    'soybean' AS crop,
    p.year,
    'export_share_pct' AS metric,
    ROUND(100.0 * e.export_t / NULLIF(p.production_t, 0), 2) AS value
FROM (
    SELECT year, SUM(production_t) AS production_t
    FROM production
    WHERE country = 'BRA' AND crop = 'soybean' AND state_name = 'Brazil'
    GROUP BY year
) p
LEFT JOIN (
    SELECT year, SUM(volume_kg) / 1000 AS export_t
    FROM trade
    WHERE country = 'BRA' AND crop = 'soybean' AND flow = 'export'
    GROUP BY year
) e ON p.year = e.year
WHERE e.export_t IS NOT NULL
ORDER BY p.year;


SELECT year, value AS export_share_pct
FROM indicators
WHERE metric = 'export_share_pct'
ORDER BY year DESC
LIMIT 10;


-- ============================================
-- INDICATORS: 3-Year CAGR of Production
-- ============================================

INSERT INTO indicators (country, scope, scope_code, crop, year, metric, value)
WITH yearly AS (
    SELECT year, SUM(production_t) AS total
    FROM production
    WHERE country = 'BRA' AND crop = 'soybean' AND state_name = 'Brazil'
    GROUP BY year
)
SELECT
    'BRA' AS country,
    'national' AS scope,
    'BR' AS scope_code,
    'soybean' AS crop,
    y2.year,
    'production_cagr_3yr_pct' AS metric,
    ROUND(
        (POWER(y2.total / NULLIF(y1.total, 0), 1.0/3) - 1) * 100,
        2
    ) AS value
FROM yearly y1
JOIN yearly y2 ON y2.year = y1.year + 3
WHERE y1.total > 0
ORDER BY y2.year;


SELECT year, value AS cagr_3yr_pct
FROM indicators
WHERE metric = 'production_cagr_3yr_pct'
ORDER BY year DESC
LIMIT 10;